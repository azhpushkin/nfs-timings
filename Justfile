set dotenv-load

user := `id -u` + ":" + `id -g`
docker-exec := "docker-compose exec -u " + user


db:
    docker-compose up -d db

run: db
    docker-compose up -d web

logs:
    docker-compose logs -f web

shell:
    {{docker-exec}} web bash

pyshell:
    {{docker-exec}} web python manage.py shell

dbshell:
    {{docker-exec}} db psql -U $POSTGRES_USER

test:
    {{docker-exec}} web pytest

fix:
    black .
    isort .
    ruff check --fix .

compile:
    pip-compile requirements.in --resolver=backtracking > requirements.txt

sim file:
    cd simulation && python serve.py {{file}}

m:
    {{docker-exec}} web python manage.py makemigrations
    {{docker-exec}} web python manage.py migrate

sample_upload name +extra_args:
    {{docker-exec}} web python manage.py upload_sample --name {{name}} --url http://host.docker.internal:7000/getmaininfo.json?use_counter=1 {{extra_args}}


race_to_temp race_id race_name:
    {{docker-exec}} web python manage.py race_to_temp --race {{race_id}}
    {{docker-exec}} db psql -U $POSTGRES_USER -c "COPY requests_temp TO STDOUT WITH CSV HEADER" > {{race_name}}.csv
    cat {{race_name}}.csv | gzip > {{race_name}}.parquet
    # scp host:fullpath.parquet ./race_name.parquet
