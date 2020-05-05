SHELL := $(shell which bash)

default:
	python app.py |& sed 's@".*miniconfig@"root/miniconfig@g' | tee output.txt | exit 0
