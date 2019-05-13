import logging as log
import os
import tempfile

import pandas
import requests

import lciafmt.traci as traci


def get_traci(file=None) -> pandas.DataFrame:
    log.info("get method Traci 2.1")
    if file is None:
        cache_path = os.path.join(cache_dir(), "traci_2.1.xlsx")
        if os.path.isfile(cache_path):
            log.info("take file from cache: %s", cache_path)
            file = cache_path
        else:
            url = ("https://www.epa.gov/sites/production/files/2015-12/" +
                   "traci_2_1_2014_dec_10_0.xlsx")
            log.info("download method from %s", url)
            cache_dir(create=True)
            resp = requests.get(url, allow_redirects=True)
            with open(cache_path, "wb") as f:
                f.write(resp.content)
            file = cache_path
    df = traci.read(file)
    return df


def cache_dir(create=False) -> str:
    """Returns the path to the folder where cached files are stored. """
    tdir = tempfile.gettempdir()
    cdir = os.path.join(tdir, "lciafmt")
    if create:
        os.makedirs(cdir, exist_ok=True)
    return cdir
