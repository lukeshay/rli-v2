TAG=sha-$(shell git rev-parse --short HEAD)$(shell git diff --quiet || echo ".uncommitted")
IMAGE_NAME=lukeshaydocker/rli

.PHONY: default help setup build lint format clean init integration-test latest-version local-version

default: help

## display this help message
help:
	@awk '/^##.*$$/,/^[~\/\.a-zA-Z_-]+:/' $(MAKEFILE_LIST) | awk '!(NR%2){print $$0p}{p=$$0}' | awk 'BEGIN {FS = ":.*?##"}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' | sort

## sets up the repository to start devloping
setup:
	@./init.sh

## set up the repo for Github Actions
ci-cd:
	pip install --upgrade pip
	pip install poetry
	@poetry install
	@poetry run pip install -e .

## lints the python files
lint:
	@poetry run black --check setup.py rli/

## formats the python files
format:
	@poetry run black setup.py rli/

## runs all tests
test:
	@poetry run pytest --junitxml=./test_output/test-report.xml --cov=rli --cov-report=xml:test_output/coverage.xml --cov-report=html:test_output/coverage tests

## cleans all temp files
clean:
	@rm -rf .pytest_cache test_output .coverage rli.egg-info .pytest_cache .scannerwork dist

## initializes the repo for development
init:
	@./scripts/init.sh

## runs the integration smoke test
integration-test:
	@./scripts/integration_test.sh

## prints the latest published version of RLI
latest-version:
	@./scripts/latest_version.sh rli

## prints the local version of RLI
local-version:
	@poetry version | sed 's/rli //g'

## builds the docker image
build:
	docker build -t ${IMAGE_NAME}:${TAG} -t ${IMAGE_NAME}:latest .

## pushes the docker image to docker hub
push: build
	docker push ${IMAGE_NAME}:${TAG}

## pushes the image tagged latest to docker hub. THIS IS DANGEROUS
push-latest: test lint push
	docker push ${IMAGE_NAME}:latest