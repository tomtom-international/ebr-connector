#!/bin/bash

mkdir temp_doc _static
python3 -msphinx.ext.apidoc --module-first elastic/ -o temp_doc
es-generate-index-template build-results-schema --OUTPUT_FILE temp_doc/schema.json
python3 -msphinx -b html . docs