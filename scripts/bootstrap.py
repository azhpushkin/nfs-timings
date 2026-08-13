#!/usr/bin/env python3
"""Create a Docker-backed NFS Timings installation from a fresh checkout."""

from __future__ import annotations

import argparse
import filecmp
import os
import re
import secrets
import shutil
import subprocess
import sys
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn, Optional


ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / '.env'
RECORDINGS_DIR = ROOT_DIR / 'recordings'

IDENTIFIER_PATTERN = re.compile(r'^[A-Za-z0-9_]+$')
ADMIN_USERNAME_PATTERN = re.compile(r'^[A-Za-z0-9_.@+-]+$')
POSTGRES_PASSWORD_PATTERN = re.compile(r'^[A-Za-z0-9_-]{12,}$')


@dataclass(frozen=True)
class CliOptions:
    reset_database: bool
    recording_path: Optional[Path]


@dataclass(frozen=True)
class RuntimeConfig:
    postgres_user: str
    postgres_password: str
    postgres_database: str
    django_secret_key: str
    admin_username: str
    admin_password: str
    web_port: int
    debug: bool
    runserver_command: str
    user_id: int
    group_id: int


@dataclass(frozen=True)
class RecordingImport:
    source_path: Path
    staged_name: str
    race_name: str
    race_length: int


@dataclass(frozen=True)
class BootstrapConfig:
    runtime: RuntimeConfig
    recording: Optional[RecordingImport]


@dataclass(frozen=True)
class DockerCompose:
    command: tuple[str, ...]

    def run(
        self,
        *arguments: str,
        check: bool = True,
        input_text: Optional[str] = None,
        environment: Optional[dict[str, str]] = None,
        quiet: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        if environment:
            env.update(environment)

        return subprocess.run(
            [*self.command, *arguments],
            cwd=ROOT_DIR,
            check=check,
            input=input_text,
            text=True,
            env=env,
            stdout=subprocess.DEVNULL if quiet else None,
            stderr=subprocess.DEVNULL if quiet else None,
        )


@dataclass(frozen=True)
class BootstrapContext:
    compose: DockerCompose
    config: BootstrapConfig


@dataclass(frozen=True)
class SetupStep:
    name: str
    action: Callable[[BootstrapContext], None]


def fail(message: str) -> NoReturn:
    raise RuntimeError(message)


def parse_cli_options(arguments: Sequence[str]) -> CliOptions:
    parser = argparse.ArgumentParser(
        description=(
            'Create .env, PostgreSQL schema, materialized view, admin account, '
            'and Docker services for NFS Timings.'
        )
    )
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Delete this Docker Compose project\'s database volume after confirmation.',
    )
    parser.add_argument(
        '--recording',
        type=Path,
        help='Optional Parquet recording to replay and fully ingest.',
    )
    parsed = parser.parse_args(arguments)
    return CliOptions(reset_database=parsed.reset, recording_path=parsed.recording)


def find_docker_compose() -> DockerCompose:
    if not shutil.which('docker'):
        fail('Docker is required. Install Docker Desktop or Docker Engine first.')

    candidates = (('docker', 'compose'), ('docker-compose',))
    for candidate in candidates:
        try:
            subprocess.run(
                [*candidate, 'version'],
                cwd=ROOT_DIR,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue
        return DockerCompose(command=candidate)

    fail('Docker Compose is required. Install Docker Desktop or Docker Compose first.')


def ask_text(label: str, default: str) -> str:
    response = input(f'{label} [{default}]: ').strip()
    return response or default


def ask_yes_no(label: str, default: bool) -> bool:
    suffix = 'Y/n' if default else 'y/N'
    while True:
        response = input(f'{label} [{suffix}]: ').strip().lower()
        if not response:
            return default
        if response in ('y', 'yes'):
            return True
        if response in ('n', 'no'):
            return False
        print('Please answer yes or no.')


def ask_password(label: str, validator: Callable[[str], bool], error: str) -> str:
    import getpass

    while True:
        password = getpass.getpass(f'{label}: ')
        if not validator(password):
            print(error, file=sys.stderr)
            continue
        confirmation = getpass.getpass(f'Confirm {label.lower()}: ')
        if secrets.compare_digest(password, confirmation):
            return password
        print('Passwords do not match.', file=sys.stderr)


def ask_identifier(label: str, default: str, pattern: re.Pattern[str], error: str) -> str:
    while True:
        value = ask_text(label, default)
        if pattern.fullmatch(value):
            return value
        print(error, file=sys.stderr)


def ask_port() -> int:
    while True:
        raw_port = ask_text('Web port', '8000')
        try:
            port = int(raw_port)
        except ValueError:
            port = 0
        if 1 <= port <= 65535:
            return port
        print('Web port must be a number from 1 to 65535.', file=sys.stderr)


def ask_optional_recording(options: CliOptions) -> Optional[RecordingImport]:
    raw_path = options.recording_path
    if raw_path is None:
        entered_path = input(
            'Optional Parquet recording to replay and ingest (leave blank to skip): '
        ).strip()
        if not entered_path:
            return None
        raw_path = Path(entered_path)

    source_path = raw_path.expanduser().resolve()
    if not source_path.is_file():
        fail(f'Recording does not exist: {source_path}')

    race_name = ask_text('Sample race name', 'Local recording')
    while True:
        raw_length = ask_text('Sample race length in seconds', '14400')
        try:
            race_length = int(raw_length)
        except ValueError:
            race_length = 0
        if race_length > 0:
            break
        print('Sample race length must be a positive integer.', file=sys.stderr)

    return RecordingImport(
        source_path=source_path,
        staged_name=source_path.name,
        race_name=race_name,
        race_length=race_length,
    )


def collect_bootstrap_config(options: CliOptions) -> BootstrapConfig:
    postgres_user = ask_identifier(
        'PostgreSQL user',
        'nfs',
        IDENTIFIER_PATTERN,
        'PostgreSQL user may contain only letters, numbers, and underscores.',
    )
    postgres_password = ask_password(
        'PostgreSQL password (12+ letters, numbers, _ or -)',
        lambda value: bool(POSTGRES_PASSWORD_PATTERN.fullmatch(value)),
        'Use at least 12 letters, numbers, underscores, or hyphens.',
    )
    postgres_database = ask_identifier(
        'PostgreSQL database',
        'nfs',
        IDENTIFIER_PATTERN,
        'PostgreSQL database may contain only letters, numbers, and underscores.',
    )
    admin_username = ask_identifier(
        'Admin username',
        'admin',
        ADMIN_USERNAME_PATTERN,
        'Admin username contains unsupported characters.',
    )
    admin_password = ask_password(
        'Admin password',
        lambda value: bool(value),
        'Admin password must not be empty.',
    )
    web_port = ask_port()
    use_development_server = ask_yes_no('Run Django with the development server?', True)

    if use_development_server:
        runserver_command = 'python manage.py runserver 0.0.0.0:8000'
    else:
        runserver_command = (
            'gunicorn timings.wsgi -b 0.0.0.0:8000 -w 2 --access-logfile -'
        )

    runtime = RuntimeConfig(
        postgres_user=postgres_user,
        postgres_password=postgres_password,
        postgres_database=postgres_database,
        django_secret_key=secrets.token_urlsafe(48),
        admin_username=admin_username,
        admin_password=admin_password,
        web_port=web_port,
        debug=use_development_server,
        runserver_command=runserver_command,
        user_id=get_user_id(),
        group_id=get_group_id(),
    )
    return BootstrapConfig(runtime=runtime, recording=ask_optional_recording(options))


def get_user_id() -> int:
    return getattr(os, 'getuid', lambda: 1000)()


def get_group_id() -> int:
    return getattr(os, 'getgid', lambda: 1000)()


def confirm_env_replacement() -> None:
    if ENV_PATH.exists() and not ask_yes_no('.env already exists. Replace it?', False):
        fail('Existing .env was preserved. Move it aside or choose replacement to continue.')


def confirm_database_reset(options: CliOptions, compose: DockerCompose) -> None:
    if not options.reset_database:
        return

    print('WARNING: this stops the project and permanently deletes its PostgreSQL volume.')
    if input('Type RESET to continue: ').strip() != 'RESET':
        fail('Database reset cancelled.')
    compose.run('down', '--volumes', '--remove-orphans')


def write_environment_file(context: BootstrapContext) -> None:
    runtime = context.config.runtime
    contents = '\n'.join(
        (
            f'POSTGRES_USER={runtime.postgres_user}',
            f'POSTGRES_PASSWORD={runtime.postgres_password}',
            f'POSTGRES_DB={runtime.postgres_database}',
            f'DJANGO_SECRET_KEY={runtime.django_secret_key}',
            f'DEBUG={runtime.debug}',
            f'RUNSERVER_CMD={runtime.runserver_command}',
            f'DEV_PORT={runtime.web_port}',
            f'UID={runtime.user_id}',
            f'GID={runtime.group_id}',
            'SIMULATION_RECORDING=',
            '',
        )
    )
    temporary_path = ENV_PATH.with_suffix('.tmp')
    temporary_path.write_text(contents)
    temporary_path.chmod(0o600)
    temporary_path.replace(ENV_PATH)


def stage_recording(context: BootstrapContext) -> None:
    recording = context.config.recording
    if recording is None:
        return

    RECORDINGS_DIR.mkdir(exist_ok=True)
    target_path = RECORDINGS_DIR / recording.staged_name
    if target_path.exists():
        if not filecmp.cmp(recording.source_path, target_path, shallow=False):
            fail(f'Refusing to overwrite a different recording at {target_path}')
        return
    shutil.copy2(recording.source_path, target_path)


def start_database(context: BootstrapContext) -> None:
    context.compose.run('up', '-d', '--build', 'db')


def wait_for_database(context: BootstrapContext) -> None:
    runtime = context.config.runtime
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        result = context.compose.run(
            'exec',
            '-T',
            'db',
            'pg_isready',
            '-U',
            runtime.postgres_user,
            '-d',
            runtime.postgres_database,
            check=False,
            quiet=True,
        )
        if result.returncode == 0:
            return
        time.sleep(1)
    fail('PostgreSQL did not become ready within 30 seconds.')


def apply_schema(context: BootstrapContext) -> None:
    context.compose.run('run', '--rm', 'web', 'python', 'manage.py', 'migrate', '--noinput')
    context.compose.run('run', '--rm', 'web', 'python', 'manage.py', 'recreate_stints')


def ensure_admin(context: BootstrapContext) -> None:
    runtime = context.config.runtime
    context.compose.run(
        'run',
        '--rm',
        '-T',
        'web',
        'python',
        'manage.py',
        'ensure_admin',
        '--username',
        runtime.admin_username,
        '--password-stdin',
        input_text=f'{runtime.admin_password}\n',
    )


def import_recording(context: BootstrapContext) -> None:
    recording = context.config.recording
    if recording is None:
        return

    context.compose.run(
        '--profile',
        'simulation',
        'up',
        '-d',
        '--build',
        'simulator',
        environment={'SIMULATION_RECORDING': recording.staged_name},
    )
    context.compose.run(
        'run',
        '--rm',
        'web',
        'python',
        'manage.py',
        'upload_sample',
        '--name',
        recording.race_name,
        '--length',
        str(recording.race_length),
        '--url',
        'http://simulator:7000/getmaininfo.json?use_counter=1',
    )


def start_application(context: BootstrapContext) -> None:
    context.compose.run('up', '-d', 'web', 'worker')


def run_steps(context: BootstrapContext) -> None:
    steps: list[SetupStep] = [
        SetupStep('Writing .env', write_environment_file),
        SetupStep('Building images and starting PostgreSQL', start_database),
        SetupStep('Waiting for PostgreSQL', wait_for_database),
        SetupStep('Applying migrations and creating the display view', apply_schema),
        SetupStep('Creating admin account', ensure_admin),
        SetupStep('Starting web service and worker', start_application),
    ]
    if context.config.recording:
        steps.insert(1, SetupStep('Staging recording', stage_recording))
        steps.insert(-1, SetupStep('Importing recording', import_recording))

    for step in steps:
        print(f'\n==> {step.name}')
        step.action(context)


def print_completion(config: BootstrapConfig) -> None:
    print(
        f'\nSetup complete. Open http://localhost:{config.runtime.web_port}/admin/ '
        f'and sign in as {config.runtime.admin_username}.'
    )
    if config.recording:
        print('The simulator remains available at http://localhost:7000/.')
    print('Use --reset only when you intentionally want to erase this Compose database.')


def main(arguments: Sequence[str]) -> int:
    options = parse_cli_options(arguments)
    compose = find_docker_compose()
    confirm_env_replacement()
    confirm_database_reset(options, compose)
    config = collect_bootstrap_config(options)
    context = BootstrapContext(compose=compose, config=config)
    run_steps(context)
    print_completion(config)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main(sys.argv[1:]))
    except (KeyboardInterrupt, RuntimeError, subprocess.CalledProcessError) as error:
        print(f'Error: {error}', file=sys.stderr)
        raise SystemExit(1) from error
