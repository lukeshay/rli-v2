#!/bin/sh

set -e

PACKAGE_JSON_URL="https://pypi.org/pypi/${1}/json"

curl -s "$PACKAGE_JSON_URL" | jq  -r '.releases | keys | .[]' | sort -V
