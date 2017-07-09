#!/bin/bash

set -e

echo ">> Installing python dependencies..."
pip3 install beautifulsoup4
pip3 install requests

echo ">> Building CompEnvUpdater..."
cd CompEnvUpdater
mvn clean package
cp target/CompEnvUpdater-0.0.1-SNAPSHOT-jar-with-dependencies.jar ../bin/CompEnvUpdater.jar
cd ..
echo ">> Copied CompEnvUpdater to bin/CompEnvUpdater.jar"
