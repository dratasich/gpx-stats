#!/bin/bash

DIR=$1

for f in $DIR/*.gpx
do
    poetry run ./gpx.py "$f"
done
