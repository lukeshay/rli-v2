#!/bin/sh

sonar-scanner \
    -Dsonar.branch.name=$1 \
    -Dsonar.login=$2 \
    -Dsonar.host.url=https://sonarcloud.io/ \
    -Dsonar.organization=luke-shay \
    -Dsonar.projectKey=rli \
    -Dsonar.projectName=rli \
    -Dsonar.sources=./rli/ \
    -Dsonar.tests=./tests/ \
    -Dsonar.python.xunit.reportPath=./test_output/test-report.xml \
    -Dsonar.python.coverage.reportPath=./test_output/coverage.xml