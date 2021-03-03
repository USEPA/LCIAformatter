import uuid
import pandas as pd
import numpy as np
import yaml
import os
from os.path import join
import lciafmt
import logging as log
import pkg_resources
import subprocess
from esupy.processed_data_mgmt import Paths, FileMeta, load_preprocessed_output,\
    write_df_to_file

modulepath = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')
datapath = modulepath + '/data/'

#Common declaration of write format for package data products
write_format = "parquet"

paths = Paths
paths.local_path = os.path.realpath(paths.local_path + "/lciafmt")
outputpath = paths.local_path

#pkg = pkg_resources.get_distribution('lciafmt')
try:
    git_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip().decode(
        'ascii')[0:7]
except:
    git_hash = None

def set_lcia_method_meta(method_id):
    lcia_method_meta = FileMeta
    lcia_method_meta.name_data = method_id.get_filename()
    #lcia_method_meta.tool = pkg.project_name
    #lcia_method_meta.tool_version = pkg.version
    lcia_method_meta.category = method_id.get_path()
    lcia_method_meta.ext = write_format
    lcia_method_meta.git_hash = git_hash
    return lcia_method_meta

def make_uuid(*args: str) -> str:
    path = _as_path(*args)
    return str(uuid.uuid3(uuid.NAMESPACE_OID, path))


def _as_path(*args: str) -> str:
    strings = []
    for arg in args:
        if arg is None:
            continue
        strings.append(str(arg).strip().lower())
    return "/".join(strings)


def is_non_empty_str(s: str) -> bool:
    """Tests if the given parameter is a non-empty string."""
    if not isinstance(s, str):
        return False
    return s.strip() != ""


def is_empty_str(s: str) -> bool:
    if s is None:
        return True
    if isinstance(s, str):
        return s.strip() == ''
    else:
        return False


def format_cas(cas) -> str:
    """ In LCIA method sheets CAS numbers are often saved as numbers. This
        function formats such numbers to strings that matches the general
        format of a CAS numner. It also handles other cases like None values
        etc."""
    if cas is None:
        return ""
    if cas == "x" or cas == "-":
        return ""
    if isinstance(cas, (int, float)):
        cas = str(int(cas))
        if len(cas) > 4:
            cas = cas[:-3] + "-" + cas[-3:-1] + "-" + cas[-1]
        return cas
    return str(cas)


def aggregate_factors_for_primary_contexts(df) -> pd.DataFrame:
    """
    When factors don't exist for flow categories with only a primary context, like "air", but do
    exist for 1 or more categories where secondary contexts are present, like "air/urban", then this
    function creates factors for that primary context as an average of the factors from flows
    with the same secondary context. NOTE this will overwrite factors if they already exist
    :param df: a pandas dataframe for an LCIA method
    :return: a pandas dataframe for an LCIA method
    """
    #Ignore the following impact categories for generating averages
    ignored_categories = ['Land transformation', 'Land occupation',
                          'Water consumption','Mineral resource scarcity',
                          'Fossil resource scarcity']    
    indices = df['Context'].str.find('/')
    ignored_list = df['Indicator'].isin(ignored_categories)
    i = 0
    for k in ignored_list.iteritems():
        if k[1] == True:
            indices.update(pd.Series([-1], index=[i]))
        i = i + 1
                 
    primary_context = []
    i = 0
    for c in df['Context']:
        if indices[i] > 0:
            sub = c[0:indices[i]]+"/unspecified"
        else:
            sub = None
        i = i + 1
        primary_context.append(sub)

    df['Primary Context'] = primary_context
    #Subset the df to only include the rows were a primary context was added
    df_secondary_context_only = df[df['Primary Context'].notnull()]

    #Determine fields to aggregate over. Do not use flow UUID or old context
    agg_fields = list(set(df.columns) - {'Context', 'Flow UUID', 'Characterization Factor'})

    #drop primary context field from df
    df = df.drop(columns=['Primary Context'])

    df_secondary_agg = df_secondary_context_only.groupby(agg_fields, as_index=False).agg(
        {'Characterization Factor': np.average})
    df_secondary_agg = df_secondary_agg.rename(columns={"Primary Context": "Context"})

    df = pd.concat([df, df_secondary_agg], ignore_index=True, sort=False)
    return df

def get_method_metadata(name: str) -> str:
    if "TRACI 2.1" in name: 
        method = 'TRACI'
    elif "ReCiPe 2016" in name:
        if "Endpoint" in name:
            method = 'ReCiPe2016_endpoint'
        method = 'ReCiPe2016'
    else:
        return ""
    with open(join(datapath, method + "_description.yaml")) as f:
        metadata=yaml.safe_load(f)
    method_description = metadata['description']
    detail = ""
    try:
        detail = metadata[name]
        method_description = method_description+detail
    except:
        log.info("No further detail in description")
    return method_description

def store_method(df, method_id):
    """Prints the method as a dataframe to parquet file"""
    meta = set_lcia_method_meta(method_id)
    try:
        write_df_to_file(df,paths,meta)
    except:
        log.error('Failed to save method')

def read_method(method_id):
    """Returns the method stored in output."""
    meta = set_lcia_method_meta(method_id)
    try:
        log.info('reading stored method file')
        method = load_preprocessed_output(meta, paths)
        return method
    except (FileNotFoundError, OSError):
        log.error('No parquet file identified for ' + method_id.value)
        return None

def save_json(method_id, mapped_data, method=None):
    """Saves a method as json file in the outputpath
    param method: str name of method to subset the passed mapped_data"""
    meta = set_lcia_method_meta(method_id)
    filename = meta.name_data
    if method is not None:
        filename = method.replace('/','_')
        mapped_data = mapped_data[mapped_data['Method'] == method]
    path = outputpath+'/'+meta.category
    os.makedirs(outputpath, exist_ok=True)
    json_pack = path +'/'+filename+"_json.zip"
    if os.path.exists(json_pack):
        os.remove(json_pack)
    lciafmt.to_jsonld(mapped_data, json_pack)
