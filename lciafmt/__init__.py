import json
import logging as log
import pkg_resources

import pandas as pd

import lciafmt.cache as cache
import lciafmt.fmap as fmap
import lciafmt.jsonld as jsonld
import lciafmt.traci as traci
import lciafmt.recipe as recipe

from enum import Enum


class Method(Enum):
    TRACI = "Traci 2.1"
    RECIPE_2016 = "ReCiPe 2016"


def supported_methods() -> list:
    """Returns a list of dictionaries that contain meta-data of the supported
       LCIA methods."""
    json_file = pkg_resources.resource_filename("lciafmt", 'data/methods.json')
    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f)


def get_method(method_id, file=None, url=None) -> pd.DataFrame:
    """Returns the data frame of the method with the given ID. You can get the
       IDs of the supported methods from the `supported_methods` function or
       directly use the constants defined in the Method enumeration type."""
    if method_id == Method.TRACI.value or method_id == Method.TRACI:
        return traci.get(file=file, url=None)
    if method_id == Method.RECIPE_2016.value or method_id == Method.RECIPE_2016:
        return recipe.get(file=file, url=url)


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
