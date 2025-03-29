#!/bin/bash

DIR=$1
DB=$2

for f in $DIR/*.gpx
do
    uv run python stats_loader/import.py "$f" --db $DB
done
