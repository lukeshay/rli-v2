#!/bin/sh

pip3 install virtualenv

if [[ -d ${PWD}/.venv ]]
then
    rm -rf ${PWD}/.venv
fi

python3 -m venv ${PWD}/.venv

source ${PWD}/.venv/bin/activate

pip install --upgrade pip

pip install -Ur requirements.txt
