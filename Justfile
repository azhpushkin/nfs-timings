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

black:
    black --extend-exclude migrations --skip-string-normalization .

exec cmd:
    {{docker-exec}} web {{cmd}}

compile:
    pip-compile requirements.in --resolver=backtracking > requirements.txt

sim file:
    cd simulation && python serve.py {{file}}

sample_upload name:
    {{docker-exec}} web python manage.py upload_sample --name {{name}} --url http://host.docker.internal:7000/getmaininfo.json?use_counter=1