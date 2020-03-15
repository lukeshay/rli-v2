COMMIT_SHA=$(shell git rev-parse --short HEAD)

.PHONY: default help setup build lint format clean

default: help

## display this help message
help:
	@awk '/^##.*$$/,/^[~\/\.a-zA-Z_-]+:/' $(MAKEFILE_LIST) | awk '!(NR%2){print $$0p}{p=$$0}' | awk 'BEGIN {FS = ":.*?##"}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' | sort

## sets up the repository to start devloping
setup:
	./init.sh

## builds the cli tool
build:
	pip install -e .

## lints the python files
lint:
	black --check setup.py rli/

## formats the python files
format:
	black setup.py rli/

## runs all tests
test:
	pytest --junitxml=./test_output/test-report.xml --cov=rli --cov-report=xml:test_output/coverage.xml --cov-report=html:test_output/coverage tests

## cleans all temp files
clean:
	rm -rf .pytest_cache test_output .coverage rli.egg-info .pytest_cache .scannerwork
