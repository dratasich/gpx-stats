#!/bin/bash

DIR=$1

for f in $DIR/*.gpx
do
    uv run python stats_loader/import.py "$f"
done
