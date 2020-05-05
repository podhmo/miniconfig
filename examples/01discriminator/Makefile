SHELL := $(shell which bash)

default:
	mypy --strict --strict-equality app.py
	python app.py |& sed 's@".*miniconfig@"root/miniconfig@g' | tee output.txt | exit 0
