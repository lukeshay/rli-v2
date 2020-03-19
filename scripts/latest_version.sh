#!/bin/sh

set -e

PACKAGE_JSON_URL="https://pypi.org/pypi/${1}/json"

VERSIONS=($(curl -s "$PACKAGE_JSON_URL" | jq  -r '.releases | keys | .[]' | sort -rV))

echo ${VERSIONS[0]}
