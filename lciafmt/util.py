# util.py (lciafmt)
# !/usr/bin/env python3
# coding=utf-8
"""
This module contains common functions for processing LCIA methods
"""

import uuid
import os
from os.path import join
import sys
import lciafmt
import logging as log
import pandas as pd
import numpy as np
import yaml
import pkg_resources
from esupy.processed_data_mgmt import Paths, FileMeta, load_preprocessed_output,\
    write_df_to_file, write_metadata_to_file
from esupy.util import get_git_hash
from fedelemflowlist.globals import flow_list_specs


# set version number of package, needs to be updated with setup.py
pkg_version_number = '1.0.0'
modulepath = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')
datapath = modulepath + '/data/'

log.basicConfig(level=log.INFO, format='%(asctime)s %(levelname)-8s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S', stream=sys.stdout)

# Common declaration of write format for package data products
write_format = "parquet"

paths = Paths()
paths.local_path = os.path.realpath(paths.local_path + "/lciafmt")
outputpath = paths.local_path

pkg = pkg_resources.get_distribution('lciafmt')
git_hash = get_git_hash()

method_metadata = {
    'Name': '',
    'Version': '',
    'Source': '',
    'SourceType': '',
    'Citation': '',
    }


def set_lcia_method_meta(method_id):
    lcia_method_meta = FileMeta()
    if method_id is not None:
        lcia_method_meta.name_data = method_id.get_filename()
        lcia_method_meta.category = method_id.get_path()
    else:
        lcia_method_meta.name_data = ""
        lcia_method_meta.category = ""
    lcia_method_meta.tool = pkg.project_name
    lcia_method_meta.tool_version = pkg_version_number
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


def format_cas(cas) -> str:
    """In LCIA method sheets CAS numbers are often saved as numbers. This
    function formats such numbers to strings that matches the general
    format of a CAS numner. It also handles other cases like None values.
    """
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
    # Ignore the following impact categories for generating averages
    ignored_categories = ['Land transformation', 'Land occupation',
                          'Water consumption', 'Mineral resource scarcity',
                          'Fossil resource scarcity']
    indices = df['Context'].str.find('/')
    ignored_list = df['Indicator'].isin(ignored_categories)
    i = 0
    for k in ignored_list.iteritems():
        if k[1]:
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
    # Subset the df to only include the rows were a primary context was added
    df_secondary_context_only = df[df['Primary Context'].notnull()]

    # Determine fields to aggregate over. Do not use flow UUID or old context
    agg_fields = list(set(df.columns) - {'Context', 'Flow UUID',
                                         'Characterization Factor'})

    # drop primary context field from df
    df = df.drop(columns=['Primary Context'])

    df_secondary_agg = df_secondary_context_only.groupby(agg_fields, as_index=False).agg(
        {'Characterization Factor': np.average})
    df_secondary_agg = df_secondary_agg.rename(columns={"Primary Context": "Context"})

    df = pd.concat([df, df_secondary_agg], ignore_index=True, sort=False)
    return df


def get_modification(source, name) -> pd.DataFrame:
    """Return a dataframe of modified CFs based on csv."""
    modified_factors = pd.read_csv(datapath+"/"+source+"_"+name+".csv")
    return modified_factors


def collapse_indicators(df) -> pd.DataFrame:
    """Collapse instances of duplicate flows per indicator.

    For a given flow for an indicator, only one characterization factor
    should be present. In some cases, due to lack of detail in target flow list,
    this assumption is invalid. This function collapses those instances and
    returns an average characterization factor.
    """
    cols = ['Method', 'Indicator', 'Indicator unit', 'Flow UUID']
    duplicates = df[df.duplicated(subset=cols, keep=False)]
    cols_to_keep = [c for c in df.columns.values.tolist()]
    cols_to_keep.remove('Characterization Factor')
    df2 = df.groupby(cols_to_keep, as_index=False)['Characterization Factor'].mean()
    log.info(str(len(duplicates))+" duplicate factors consolidated to "
             + str(len(duplicates)-(len(df)-len(df2))))

    return df2


def check_as_class(method_id):
    if not isinstance(method_id, lciafmt.Method):
        method_id = lciafmt.Method.get_class(method_id)
    return method_id


def generate_method_description(name: str) -> str:
    with open(join(datapath, "description.yaml")) as f:
        generic = yaml.safe_load(f)
    method_description = generic['description']
    method = check_as_class(name)
    if method is None:
        method_meta = {}
        method_meta['name'] = name
        method_meta['url'] = ''
        method_meta['citation'] = ''
    else:
        method_meta = method.get_metadata()
    if 'detail_note' in method_meta:
        method_description += method_meta['detail_note']
    if 'methods' in method_meta:
        try:
            detailed_meta = '\n\n' + method_meta['methods'][name]
            method_description += detailed_meta
        except KeyError:
            log.debug('%s not found in methods.json', name)
    # Replace tagged fields
    if 'version' in method_meta:
        version = ' (v' + method_meta['version'] + ')'
    else:
        version = ''
    method_description = method_description.replace('[LCIAfmt_version]', pkg_version_number)
    method_description = method_description.replace('[FEDEFL_version]', flow_list_specs['list_version'])
    method_description = method_description.replace('[Method]', method_meta['name'])
    method_description = method_description.replace('[version]', version)
    method_description = method_description.replace('[citation]', method_meta['citation'])
    method_description = method_description.replace('[url]', method_meta['url'])

    return method_description


def compile_metadata(method_id):
    """Compile metadata for a method."""
    metadata = dict(method_metadata)
    method_meta = {}
    if method_id is not None:
        method_meta = method_id.get_metadata()
    match_dict = {'Name': 'name',
                  'Version': 'version',
                  'Source': 'url',
                  'SourceType': 'source_type',
                  'Citation': 'citation',
                  }
    for k, v in match_dict.items():
        if v in method_meta:
            metadata[k] = method_meta[v]
    return metadata


def store_method(df, method_id):
    """Save the method as a dataframe to parquet file."""
    meta = set_lcia_method_meta(method_id)
    method_path = outputpath + '/' + meta.category
    if meta.name_data == "":
        meta.name_data = df['Method'][0]
    meta.tool_meta = compile_metadata(method_id)
    try:
        log.info('saving ' + meta.name_data + ' to ' + method_path)
        write_df_to_file(df, paths, meta)
        write_metadata_to_file(paths, meta)
    except:
        log.error('Failed to save method')


def read_method(method_id):
    """Return the method stored in output."""
    meta = set_lcia_method_meta(method_id)
    method = load_preprocessed_output(meta, paths)
    method_path = outputpath + '/' + meta.category
    if method is None:
        log.info(meta.name_data + ' not found in ' + method_path)
    else:
        log.info('loaded ' + meta.name_data + ' from ' + method_path)
    return method


def save_json(method_id, mapped_data, method=None, name=''):
    """Save a method as json file in the outputpath.

    :param method_id: class Method
    :param mapped_data: df of mapped method to save
    :param method: str, name of method to subset the passed mapped_data
    :param name: str, optional method name when method_id does not exist
    """
    meta = set_lcia_method_meta(method_id)
    if name == '':
        filename = meta.name_data
    else:
        filename = name
    if method is not None:
        filename = method.replace('/', '_')
        mapped_data = mapped_data[mapped_data['Method'] == method]
    path = outputpath+'/'+meta.category
    os.makedirs(outputpath, exist_ok=True)
    json_pack = path + '/' + filename + "_json_v" + meta.tool_version + ".zip"
    if os.path.exists(json_pack):
        os.remove(json_pack)
    lciafmt.to_jsonld(mapped_data, json_pack)
