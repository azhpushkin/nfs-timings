.PHONY: webui work sim simone black i

webui:
	python manage.py runserver

worker:
	python3 worker.py

sim:
	cd simulation && python serve.py

black:
	python -m black --extend-exclude migrations --skip-string-normalization .

i:
	python -m IPython  # easier to deal with venv

compile-reqs:
	pip-compile requirements.in --resolver=backtracking > requirements.txt

