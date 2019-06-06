import logging as log
import os
import shutil
import tempfile

import pandas as pd
import requests

import lciafmt.fmap as fmap
import lciafmt.jsonld as jsonld
import lciafmt.traci as traci


def get_traci(file=None, url=None) -> pd.DataFrame:
    log.info("get method Traci 2.1")
    if file is None:
        cache_path = os.path.join(cache_dir(), "traci_2.1.xlsx")
        if os.path.isfile(cache_path):
            log.info("take file from cache: %s", cache_path)
            file = cache_path
        else:
            if url is None:
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


def clear_cache():
    d = cache_dir()
    if not os.path.isdir(d):
        return
    shutil.rmtree(d)


def to_jsonld(df: pd.DataFrame, zip_file: str):
    log.info("write JSON-LD package to %s", zip_file)
    with jsonld.Writer(zip_file) as w:
        w.write(df)


def cache_dir(create=False) -> str:
    """Returns the path to the folder where cached files are stored. """
    tdir = tempfile.gettempdir()
    cdir = os.path.join(tdir, "lciafmt")
    if create:
        os.makedirs(cdir, exist_ok=True)
    return cdir


def map_flows(df: pd.DataFrame, system=None, mapping=None,
              preserve_unmapped=False) -> pd.DataFrame:
    """Maps the flows in the given data frame using the given target system. It
       returns a new data frame with the mapped flows."""
    mapper = fmap.Mapper(df, system=system, mapping=mapping,
                         preserve_unmapped=preserve_unmapped)
    return mapper.run()
