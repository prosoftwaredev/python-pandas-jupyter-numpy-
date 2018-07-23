#!/bin/bash

deactivate 2> /dev/null
# create virtualenv if required
if [ ! -d .venv ]
then
    virtualenv -p python3 .venv
fi

# activate and install packages
. .venv/bin/activate
pip install -r requirements.txt

# print messages about make
echo "setup OK"
echo ""
echo "you must activate the virtual environment before any of the following make commands will work"
echo ""
echo "do it like this:"
echo ""
echo "    . .venv/bin/activate"
echo ""
echo "make commands:"
make show-help
