#!/usr/bin/env python3

# code derived from
# https://towardsdatascience.com/how-tracking-apps-analyse-your-gps-data-a-hands-on-tutorial-in-python-756d4db6715d

import gpxpy
import pandas as pd
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
df = df.set_index('time')

start = df.iloc[0]
finish = df.iloc[-1]
print(start)
print(finish)

df.plot.line(x='lon', y='lat')

plt.show()
