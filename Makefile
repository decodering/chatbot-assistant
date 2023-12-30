.PHONY: *

#################################################################################
# GLOBALS
#################################################################################

VENV_NAME="venv"
VENV_DIR="./${VENV_NAME}"
VENV_BIN="${VENV_DIR}/bin/activate" # ./ is optional at front

REQUIREMENTS_DEV_TXT="requirements/requirements_dev.txt"
REQUIREMENTS_PROD_TXT="requirements/requirements.txt"

LOCAL_CACHE_DIR=".local/pip-cache"

#################################################################################
# DEV COMMANDS (Building, deps mgmt)
#################################################################################

## Compile requirements.txt and requirements_dev.txt
compile_requirements:
	@bash scripts/compile_requirements.sh

## Sync requirements from requirements_dev.txt in local venv
sync_requirements:
	@source ${VENV_BIN} && \
	echo "Syncing requirement files (prod and dev)... " && \
	pip-sync --verbose \
		${REQUIREMENTS_DEV_TXT} ${REQUIREMENTS_PROD_TXT} && \
	echo "Done!"

## Run app
run:
	@source ${VENV_BIN} && \
	gradio src/app.py
