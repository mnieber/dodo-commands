#!/bin/bash

INSTALL_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

virtualenv -q -p python3 $INSTALL_DIR/env
$INSTALL_DIR/env/bin/pip install -q plumbum pudb ipython PyYAML six
$INSTALL_DIR/env/bin/python $INSTALL_DIR/install.py "$@"
