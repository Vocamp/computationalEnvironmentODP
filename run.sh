#!/bin/bash

echo ">> Gathering processor names..."
python3 bin/processors.py > data/processors.txt
echo ">> Updating ontology..."
java -jar bin/CompEnvUpdater.jar
echo ">> Done."
