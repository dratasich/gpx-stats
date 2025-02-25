gpx-stats
=========

Dashboard visualizing stats based on gpx files.


## Setup

```bash
# install environment
$ uv sync
```


## Usage

Add your gpx files to `data` (e.g., sync from your phone).

Load gpx files, generate metadata and save to sqlite database:
```bash
$ ./gpx.py data/<file>.gpx
```

Load all gpx files from a folder:
```bash
$ ./load.sh data
```

Visualize [stats](http://localhost:8050):
```bash
$ python app.py
```
or with [grafana](https://grafana.com/docs/grafana/latest/)
at [localhost:3000](http://localhost:3000)
with default username and password `admin:admin`:
```bash
$ docker-compose up
# or with podman
$ podman compose up
```


## Development

Debug database:
```bash
sqlite3 db/gpx.db
# list tables
> .tables
```

List latest entries:
```sql
SELECT * FROM files ORDER BY load_timestamp DESC LIMIT 5;
```

Run before commit
```bash
# code formatting
ruff check --fix
ruff format
```
