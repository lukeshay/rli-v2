#!/bin/bash

poetry run rli smoke

EXIT_STATUS=${?}

echo "Exit status: ${EXIT_STATUS}"

exit ${EXIT_STATUS}
