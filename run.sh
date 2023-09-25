#!/bin/sh
cd `dirname $0`

$PYTHON="venv/bin/python"

python3 -m venv venv
$PYTHON -m pip install -r requirements.txt

# Be sure to use `exec` so that termination signals reach the python process,
# or handle forwarding termination signals manually
exec $PYTHON -m src.main $@
