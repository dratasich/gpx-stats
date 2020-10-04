#!/bin/bash

DIR="data"

for f in $DIR/*.gpx
do
    ./gpx.py "$f"
done
