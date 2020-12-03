import json
import logging as log
import pkg_resources

import pandas as pd
import os

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
    
    def get_metadata(cls):
        metadata = supported_methods()
        for m in metadata:
            if 'case_insensitivity' in m:
                if m['case_insensitivity']=='True':
                    m['case_insensitivity'] = True
                else:
                    m['case_insensitivity'] = False
            if m['id'] == cls.name:
                return m
    
    def get_filename(cls):
        filename = cls.get_metadata()['name'].replace(" ", "_")
        return filename

    def get_class(name):
        for n,c in Method.__members__.items():
            m = c.get_metadata()
            mapping = None
            if 'mapping' in m: mapping = m['mapping']
            if n == name or c.value == name or mapping == name:
                return c
        log.error('Method not found')

def supported_methods() -> list:
    """Returns a list of dictionaries that contain meta-data of the supported
       LCIA methods."""
    json_file = pkg_resources.resource_filename("lciafmt", 'data/methods.json')
    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f)


def get_method(method_id, add_factors_for_missing_contexts=True, endpoint=False, summary=False,
               file=None, url=None) -> pd.DataFrame:
    """Returns the data frame of the method with the given ID. You can get the
       IDs of the supported methods from the `supported_methods` function or
       directly use the constants defined in the Method enumeration type."""
    method_id = _check_as_class(method_id)
    if method_id == Method.TRACI:
        return traci.get(add_factors_for_missing_contexts, file=file, url=None)
    if method_id == Method.RECIPE_2016:
        return recipe.get(add_factors_for_missing_contexts, endpoint, summary, file=file, url=url)
    if method_id == Method.FEDEFL_INV:
        return fedefl_inventory.get(subset=None)

def get_modification(source, name) -> pd.DataFrame:
    """Returns a dataframe of modified CFs based on csv"""
    modified_factors = pd.read_csv(util.datapath+"/"+source+"_"+name+".csv")
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

def get_mapped_method(method_id, indicators=None, methods=None):
    """Obtains a mapped method stored as parquet, if that file does not exist
    locally, it is generated"""
    method_id = _check_as_class(method_id)
    filename = method_id.get_filename()
    if os.path.exists(util.outputpath+filename+".parquet"):
        mapped_method = util.read_method(method_id)
    else:
        method = get_method(method_id)
        if 'mapping' in method_id.get_metadata():
            mapping_system = method_id.get_metadata()['mapping']
            case_insensitive = method_id.get_metadata()['case_insensitivity']
            if case_insensitive:
                method['Flowable'] = method['Flowable'].str.lower()
            mapped_method = map_flows(method, system=mapping_system, case_insensitive=case_insensitive)
        else:
            mapped_method = method
    if indicators is not None:
        mapped_method = mapped_method[mapped_method['Indicator'].isin(indicators)]
        if len(mapped_method) == 0:
            log.error('indicator not found')
    if methods is not None:
        mapped_method = mapped_method[mapped_method['Method'].isin(methods)]
        if len(mapped_method) == 0:
            log.error('specified method not found')
    return mapped_method

def supported_indicators(method_id):
    """Returns a list of indicators for the identified method."""
    method = util.read_method(method_id)
    if method is not None:
        indicators = set(list(method['Indicator']))
        return list(indicators)
    else: return None

def supported_stored_methods():
    """Returns a list of methods stored as parquet."""
    methods = pd.DataFrame()
    files = os.listdir(util.outputpath)
    for name in files:
        if name.endswith(".parquet"):
            method = pd.read_parquet(util.outputpath+name)
            methods = pd.concat([methods, method])
    methods_list = set(list(methods['Method']))
    return list(methods_list)   

def _check_as_class(method_id):
    if not isinstance(method_id, Method):
        method_id = Method.get_class(method_id)
    return method_id
