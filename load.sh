#!/bin/bash

DIR=$1

for f in $DIR/*.gpx
do
    uv run ./gpx.py "$f"
done
