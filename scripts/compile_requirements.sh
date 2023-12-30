#!/usr/bin/env bash
#
# Compiles requirements for current project

VENV_DIR="venv/bin/activate"
REQUIREMENTS_IN_DIR="requirements"
REQUIREMENTS_PROD_IN="${REQUIREMENTS_IN_DIR}/requirements.in"
REQUIREMENTS_PROD_TXT="${REQUIREMENTS_IN_DIR}/requirements.txt"
REQUIREMENTS_DEV_IN="${REQUIREMENTS_IN_DIR}/requirements_dev.in"
REQUIREMENTS_DEV_TXT="${REQUIREMENTS_IN_DIR}/requirements_dev.txt"

REQUIREMENTS_TXT_HOST_REGEX="s/.*--trusted-host p-nexus/# &/"
REQUIREMENTS_PROD_TXT_REGEX="s/.*-r requirements/# &/"
REQUIREMENTS_PROD_TXT_REGEX_2="^/\-r requirements\.txt$/s/^/#"

PIP_COMPILE_UPGRADE_STRING_TXT=""
PIP_COMPILE_UPGRADE_STRING_HASH=""
TXT_EXISTS=$(ls -1 ${REQUIREMENTS_IN_DIR}/*.txt 2>/dev/null | wc -l)
HASH_EXISTS=$(ls -1 ${REQUIREMENTS_IN_DIR}/*.hash 2>/dev/null | wc -l)

source $VENV_DIR &&
    pip-compile-multi --live \
        --allow-unsafe \
        --use-cache \
        --backtracking \
        --autoresolve \
        --directory ${REQUIREMENTS_IN_DIR} &&
    deactivate

# Remove the -r requirements.txt line from requirements_dev.txt
# Causes error otherwise when running pip install -e .[dev] (pip bug not able to parse '-r requirements' line as literal)
# sed in OSX requires an empty string after -i!! (See: https://unix.stackexchange.com/a/128595)
# https://stackoverflow.com/a/4247319
if [[ "$(uname -s)" == "Darwin" ]]; then
    sed -i \
        '' \
        -e "${REQUIREMENTS_PROD_TXT_REGEX}" \
        -e "${REQUIREMENTS_TXT_HOST_REGEX}" \
        ${REQUIREMENTS_DEV_TXT} &&
        sed -i \
            '' \
            -e "${REQUIREMENTS_PROD_TXT_REGEX}" \
            -e "${REQUIREMENTS_TXT_HOST_REGEX}" \
            ${REQUIREMENTS_PROD_TXT}
elif [[ "$(uname -s)" == "Linux" ]]; then
    sed -i'' \
        -e "${REQUIREMENTS_PROD_TXT_REGEX}" \
        -e "${REQUIREMENTS_TXT_HOST_REGEX}" \
        ${REQUIREMENTS_DEV_TXT} &&
        sed -i'' \
            -e "${REQUIREMENTS_PROD_TXT_REGEX}" \
            -e "${REQUIREMENTS_TXT_HOST_REGEX}" \
            ${REQUIREMENTS_PROD_TXT}
else
    echo -e "Not recognised platform! - $(uname -s)"
    exit 0
fi
