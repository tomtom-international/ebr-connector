#!/bin/bash

sphinx-apidoc --module-first elastic/ -o .
sphinx-build -b html . docs