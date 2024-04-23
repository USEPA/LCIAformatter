# location.py (lciafmt)
# !/usr/bin/env python3
# coding=utf-8
"""
Functions to facilitate creation of location objects
"""

import bz2
import json

from esupy.remote import make_url_request

location_meta = ('https://raw.githubusercontent.com/GreenDelta/data/'
                 'master/refdata/locations.csv')

# %% get GeoJSON
url = 'https://geography.ecoinvent.org/files'

object_dict = {'states': 'states.geojson.bz2'}

def extract_coordinates(group) -> dict:
    file = object_dict.get(group)
    if file is None:
        print('error')
        return
    response = make_url_request(f'{url}/{file}')
    content = bz2.decompress(response.content)
    data = json.loads(content)

    # %% extract GeoJSON objects from the FeatureCollection
    features = data['features']
   
    us_states = {f['properties']['shortname']: f['geometry']
                 for f in features 
                 if f['properties']['shortname'].startswith('US')}
    return us_states


def assign_state_names(df):
    import flowsa
    f = flowsa.location.get_state_FIPS(abbrev=True).drop(columns='County')
    f['State'] = f['State'].apply(lambda x: f"US-{x}")
    fd = f.set_index('FIPS').to_dict()['State']
    fd['00000'] = 'US'
    df['Location'] = df['Location'].replace(fd)
    return df.dropna(subset='Location')


if __name__ == "__main__":
    d = extract_coordinates(group='states')
