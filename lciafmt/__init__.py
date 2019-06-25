import json
import logging as log
import pkg_resources

import pandas as pd

import lciafmt.cache as cache
import lciafmt.fmap as fmap
import lciafmt.jsonld as jsonld
import lciafmt.traci as traci

from enum import Enum


class Method(Enum):
    TRACI = "Traci 2.1"


def supported_methods() -> list:
    """Returns a list of dictionaries that contain meta-data of the supported
       LCIA methods."""
    json_file = pkg_resources.resource_filename("lciafmt", 'data/methods.json')
    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f)


def get_traci(file=None, url=None) -> pd.DataFrame:
    log.info("get method Traci 2.1")
    f = file
    if f is None:
        fname = "traci_2.1.xlsx"
        f = cache.get_path(fname)
        if cache.exists(fname):
            log.info("take file from cache: %s", f)
        else:
            if url is None:
                url = ("https://www.epa.gov/sites/production/files/2015-12/" +
                       "traci_2_1_2014_dec_10_0.xlsx")
            log.info("download method from %s", url)
            cache.download(url, fname)
    df = traci.read(f)
    return df


def clear_cache():
    cache.clear()


def to_jsonld(df: pd.DataFrame, zip_file: str, write_flows=False):
    log.info("write JSON-LD package to %s", zip_file)
    with jsonld.Writer(zip_file) as w:
        w.write(df, write_flows)


def map_flows(df: pd.DataFrame, system=None, mapping=None,
              preserve_unmapped=False) -> pd.DataFrame:
    """Maps the flows in the given data frame using the given target system. It
       returns a new data frame with the mapped flows."""
    mapper = fmap.Mapper(df, system=system, mapping=mapping,
                         preserve_unmapped=preserve_unmapped)
    return mapper.run()
