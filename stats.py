#!/usr/bin/env python3

# code derived from
# https://towardsdatascience.com/how-tracking-apps-analyse-your-gps-data-a-hands-on-tutorial-in-python-756d4db6715d

import gpxpy
import haversine
import pandas as pd
import math
import matplotlib.pyplot as plt


# parse GPX
gpx_file = open('../gpx-pipeline/test/RunnerUp_01.gpx', 'r')
gpx = gpxpy.parse(gpx_file)
data = gpx.tracks[0].segments[0].points


# GPX to pandas data frame
df = pd.DataFrame(columns=['lon', 'lat', 'alt', 'time'])
for segment in gpx.tracks[0].segments:
    for point in segment.points:
        df = df.append({'lon': point.longitude, 'lat': point.latitude,
                        'alt': point.elevation, 'time': point.time},
                       ignore_index=True)

df['time'] = df['time'].dt.tz_localize(None)
print("> convert time to seconds for calculations")
df['timestamp'] = df.apply(lambda row: row['time'].timestamp(), axis=1)
print(df.head())

print("> time as index")
df = df.set_index('time')

print("> data including null values")
df_null = df[df.isnull().any(axis=1)]
print(df_null.head())

print("> sort by time")
df = df.sort_index()
print(df.head())
print(":")
print(df.tail())

print("> calculate distance")
df['delta_t'] = (df.timestamp - df.timestamp.shift()).fillna(0)
df['t'] = df['delta_t'].cumsum()
hav2d = [0.0]
hav3d = [0.0]
for i in range(len(df)):
    if i == 0:
        continue
    a = (df.iloc[i-1].lat, df.iloc[i-1].lon)
    b = (df.iloc[i].lat, df.iloc[i].lon)
    hav2d.append(haversine.haversine(a, b, unit=haversine.Unit.METERS))
    dalt = df.iloc[i].alt - df.iloc[i-1].alt
    hav3d.append(math.sqrt(hav2d[-1]**2 + dalt**2))
df['delta_2d'] = hav2d
df['delta_3d'] = hav3d
df['2d'] = df['delta_2d'].cumsum()
df['3d'] = df['delta_3d'].cumsum()
print(df)

print(f"distance: {df.iloc[-1]['2d']}")
print(f"avg km/h: {df.iloc[-1]['2d'] / df.iloc[-1]['t'] * 3.6}")
min_per_km = int(float(df.iloc[-1]['t']) / 60)
sec_remainder = int(float(df.iloc[-1]['t']) - (min_per_km * 60))
print(f"pace min/km: { float(df.iloc[-1]['t']) / 60.0 / (df.iloc[-1]['2d'] / 1000)}")

df.plot.line(x='lon', y='lat')
df.plot(y='alt')

plt.show()
