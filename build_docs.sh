#!/bin/bash

mkdir temp_doc _static
sphinx-apidoc --module-first elastic/ -o temp_doc
es-generate-index-template build-results-schema > temp_doc/schema.json
sphinx-build -b html . docs