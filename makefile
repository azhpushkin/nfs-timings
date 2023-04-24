.PHONY: webui work sim simone black i

webui:
	python -m uvicorn webui.main:app --reload --host 0.0.0.0 --port 8080

worker:
	rq worker --with-scheduler

sim:
	cd simulation && python serve.py

black:
	python -m black .

i:
	python -m IPython  # easier to deal with venv

compile-reqs:
	pip-compile requirements.in --resolver=backtracking > requirements.txt

