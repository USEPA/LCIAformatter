import uuid
import pandas as pd
import numpy as np
import yaml
import os
from os.path import join
import logging as log

datapath = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')+'/data'

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
    modulepath = os.path.dirname(
    os.path.realpath(__file__)).replace('\\', '/')
    datapath = modulepath + '/../lciafmt/data/'
    if "TRACI 2.1" in name: 
        method = 'TRACI'
    elif "ReCiPe 2016" in name:
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
