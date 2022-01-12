import requests
import pandas as pd
import io
import numpy as np
import csv

def find_ev_chargers_location(lat, long, dist_from_coord):

    response = requests.get(f"http://chargepoints.dft.gov.uk/api/retrieve/registry/lat/{lat}/long/{long}"
                            f"/dist/{dist_from_coord}/format/csv")
    r = response.content
    rawdata = pd.read_csv(io.StringIO(r.decode('utf-8')))
    df = pd.DataFrame(rawdata)
    df.drop(df.columns.difference(['name', 'latitude', 'longitude']), 1, inplace=True)
    print(df.shape)

    xlim = (-2.27002, -2.14955)
    ylim = (53.43895, 53.51545)

    df1 = df[(df['latitude'] <= ylim[1]) & (df['latitude'] >= ylim[0])].copy()
    df2 = df1[(df1['longitude'] <= xlim[1]) & (df1['longitude'] >= xlim[0])].copy()

    df2.to_csv(path_or_buf='ev_charging_locations.csv')

    return df2


find_ev_chargers_location(53.47656, -2.21168, 5)
