#!/bin/sh

echo "Setting up virtualenv."
pip3 install virtualenv

if [[ -d ${PWD}/.venv ]]
then
    rm -rf ${PWD}/.venv
fi

python3 -m venv ${PWD}/.venv

source ${PWD}/.venv/bin/activate

pip install --upgrade pip

pip install -Ur requirements.txt

echo "Installing poetry."
curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
source $HOME/.poetry/env

poetry install