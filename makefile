run:
	python -m uvicorn webui.main:app --reload

work:
	python -m worker

sim:
	cd simulation && python serve.py

simone:
	cd simulation && python serve.py single

black:
	python -m black .

i:
	python -m IPython  # easier to deal with venv