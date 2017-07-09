#!/bin/bash

echo ">> Gathering processor names..."
python3 bin/processors.py > data/processors.txt
echo ">> Gathering processor architectures..."
python3 bin/architectures.py > data/architectures.txt
echo ">> Gathering kernel..."
echo "" > data/kernels.txt
echo ">> Gathering distros..."
echo "" > data/distros.txt
echo ">> Updating ontology..."
java -jar bin/CompEnvUpdater.jar
echo ">> Done."
