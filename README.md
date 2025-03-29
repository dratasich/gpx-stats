gpx-stats
=========

Dashboard visualizing stats based on gpx files.


## Setup

```bash
# install environment
$ uv run pre-commit install
```


## Usage

Add your gpx files to `data` (e.g., sync from your phone).

Load gpx files, generate metadata and save to sqlite database:
```bash
$ ./import.py data/<file>.gpx
```
If the file has no tracks (e.g., because its a manual entry)
then try the `tcx` file (should contain duration and distance).

Load all gpx files from a folder:
```bash
mkdir db
$ ./load.sh data db/gpx.db
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
