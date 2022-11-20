gpx-stats
=========

Dashboard visualizing stats based on gpx files.


## Setup

```bash
# install environment
$ poetry install
# load environment
$ poetry shell
```


## Usage

Add your gpx files to `data` (e.g., sync from your phone).

Load gpx files, generate metadata and save to sqlite database:
```bash
$ ./gpx.py data/<file>.gpx
```

Visualize [stats](http://localhost:8050):
```bash
$ python app.py
```
