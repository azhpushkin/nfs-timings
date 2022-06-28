run:
	python -m uvicorn webui.main:app --reload

sim:
	cd simulation && python serve.py

simone:
	cd simulation && python serve.py single

black:
	python -m black .
