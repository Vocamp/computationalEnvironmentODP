#!/bin/bash

set -e

export LANG=en_US.UTF-8

echo ">> Gathering processor names..."
python3 bin/processors.py > data/processors.txt
echo ">> Gathering processor architectures..."
python3 bin/architectures.py > data/architectures.txt
echo ">> Gathering OS kernel names..."
python3 bin/kernels.py > data/kernels.txt
echo ">> Gathering OS distro names..."
python3 bin/distros.py > data/distros.txt
echo ">> Updating ontology..."
java -jar bin/CompEnvUpdater.jar

ontology=data/ComputationalEnvironment.rdf

if [[ -n $(git diff --name-only -- $ontology) ]]; then
	echo ">> The ontology has changed."
	read -p ">> Commit it [y/n]? " yn
	if [[ $yn == "y" ]]; then
		echo ">> Committing..."
		git commit "$ontology" -m "Update ontology"
	else
		echo ">> Discarding..."
		git checkout "$ontology"
	fi
fi

echo ">> Done."
