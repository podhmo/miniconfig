default: 00 01

SHELL := $(shell which bash)

00:
	python $(shell echo $@*.py) |& tee $(patsubst %.py,%.output,$(shell echo $@*.py))
01:
	python $(shell echo $@*.py) |& tee $(patsubst %.py,%.output,$(shell echo $@*.py))
