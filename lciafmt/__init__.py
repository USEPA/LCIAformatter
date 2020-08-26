import json
import logging as log
import pkg_resources

import pandas as pd

import lciafmt.cache as cache
import lciafmt.fmap as fmap
import lciafmt.jsonld as jsonld
import lciafmt.traci as traci
import lciafmt.recipe as recipe
import lciafmt.fedefl_inventory as fedefl_inventory
import lciafmt.util as util

from enum import Enum

class Method(Enum):
    TRACI = "TRACI 2.1"
    RECIPE_2016 = "ReCiPe 2016"
    FEDEFL_INV = "FEDEFL Inventory"

def supported_methods() -> list:
    """Returns a list of dictionaries that contain meta-data of the supported
       LCIA methods."""
    json_file = pkg_resources.resource_filename("lciafmt", 'data/methods.json')
    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f)


def get_method(method_id, add_factors_for_missing_contexts=True, endpoint=False, summary=False,
               file=None, url=None, subset=None) -> pd.DataFrame:
    """Returns the data frame of the method with the given ID. You can get the
       IDs of the supported methods from the `supported_methods` function or
       directly use the constants defined in the Method enumeration type."""
    if method_id == Method.TRACI.value or method_id == Method.TRACI:
        return traci.get(add_factors_for_missing_contexts, file=file, url=None)
    if method_id == Method.RECIPE_2016.value or method_id == Method.RECIPE_2016:
        return recipe.get(add_factors_for_missing_contexts, endpoint, summary, file=file, url=url)
    if method_id == Method.FEDEFL_INV.value or method_id == Method.FEDEFL_INV:
        return fedefl_inventory.get(subset)

def get_modification(source, method_id) -> pd.DataFrame:
    """Returns a dataframe of modified CFs based on csv"""
    modified_factors = pd.read_csv(util.datapath+"/"+source+"_"+method_id+".csv")
    return modified_factors

def clear_cache():
    cache.clear()


def to_jsonld(df: pd.DataFrame, zip_file: str, write_flows=False):
    log.info("write JSON-LD package to %s", zip_file)
    with jsonld.Writer(zip_file) as w:
        w.write(df, write_flows)


def map_flows(df: pd.DataFrame, system=None, mapping=None,
              preserve_unmapped=False, case_insensitive=False) -> pd.DataFrame:
    """Maps the flows in the given data frame using the given target system. It
       returns a new data frame with the mapped flows."""
    mapper = fmap.Mapper(df, system=system, mapping=mapping,
                         preserve_unmapped=preserve_unmapped,
                         case_insensitive=case_insensitive)
    return mapper.run()


def supported_mapping_systems() -> list:
    """Returns the mapping systems that are supported in the `map_flows`
       function."""
    return fmap.supported_mapping_systems()
