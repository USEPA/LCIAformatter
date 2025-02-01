# usetox.py (lciafmt)
# !/usr/bin/env python3
# coding=utf-8
"""
This module contains functions needed to compile LCIA methods from USETox
"""

import pandas as pd

import lciafmt
import lciafmt.cache as cache
from lciafmt.df import lciafmt_cols
from lciafmt.util import log, aggregate_factors_for_primary_contexts, format_cas,\
    datapath


def get(method) -> pd.DataFrame:
    """Generate a method for USEtox in standard format.

    :param add_factors_for_missing_contexts: bool, if True generates average
        factors for unspecified contexts
    :param file: str, alternate filepath for method, defaults to file stored
        in cache
    :param url: str, alternate url for method, defaults to url in method config
    :return: DataFrame of method in standard format
    """
    log.info("getting method USEtox")
    method_meta = method.get_metadata()
    # f = _get_file(method_meta)
    df = pd.DataFrame()
    for xls_file in method_meta.get('file'):
        df1 = _read(datapath / xls_file, 'Human tox CF')
        df2 = _read(datapath / xls_file, 'Ecotox CF')
        df = pd.concat([df, df1, df2], ignore_index=True)
    
    df['Method'] = method_meta.get('name')

    return df

def _get_file(method_meta, url=None):
    if url is None:
        url = method_meta['url']
    f = cache.get_or_download(fname, url)
    return f

def _read(xls_file, sheet: str) -> pd.DataFrame:
    """Read the data from Excel with given path into a DataFrame."""
    if sheet == "Ecotox CF":
        usecols = "B:K, U"
        i_unit = 'UNIT FOR ECOTOX'
    elif sheet == "Human tox CF":
        usecols = "B:BI"
        i_unit = 'UNIT FOR HH'
    df = pd.read_excel(xls_file, sheet_name=sheet, skiprows=3, usecols=usecols)
    headers = pd.read_excel(xls_file, sheet_name=sheet, nrows=2, skiprows=1, usecols=usecols).values
    headers = pd.DataFrame(headers).ffill(axis=1)
    ## TODO: fix future warning
    headers = headers.drop(headers.columns[:2], axis=1)
    header = headers.apply(lambda x: f"{x[0]}: {x[1]}")
    df.columns = pd.concat([pd.Series(['CAS', 'Name']), header])
    df_melt = pd.melt(df, id_vars=['CAS', 'Name'], var_name='header')
    df_melt[['compartment', 'indicator']] = df_melt['header'].str.split(": ", expand=True)
    
    indicator_dict = {'cancer': 'Human health cancer',
                      'non-canc.': 'Human health noncancer',
                      'freshwater': 'Ecotoxicity'}
    compartment_dict = {
        'Emission to household indoor air': 'air/indoor',
        'Emission to industrial indoor air': 'air/industrial',
        'Emission to urban air': 'air/urban',
        'Emission to cont. rural air': 'air/rural',
        'Emission to cont. freshwater': 'water/freshwater',
        'Emission to cont. sea water': 'water/marine',
        'Emission to cont. natural soil': 'ground',
        'Emission to cont. agric. soil': 'ground/agricultural',
        # 'Application to wheat': ''
        'Em.hom.airI': 'air/indoor',
        'Em.ind.airI': 'air/industrial',
        'Em.airU': 'air/urban',
        'Em.airC': 'air/rural',
        'Em.fr.waterC': 'water/freshwater',
        'Em.sea waterC': 'water/marine',
        'Em.nat.soilC': 'ground',
        'Em.agr.soilC': 'ground/agricultural',
        }
    
    df_melt = (df_melt
               .assign(Indicator = lambda x: x['indicator'].map(indicator_dict))
               .assign(Context = lambda x: x['compartment'].map(compartment_dict))
               .dropna(subset=['Indicator', 'value', 'Context'])
               .assign(i_unit = i_unit)
               .assign(Unit = 'kg')
               .rename(columns={'value': 'Characterization Factor',
                                'CAS': 'CAS No',
                                'i_unit': 'Indicator unit',
                                'Name': 'Flowable'})
               .drop(columns=['header', 'compartment', 'indicator'])
               .reindex(columns=lciafmt_cols)
               .fillna('')
               )

    return df_melt


if __name__ == "__main__":
    from lciafmt.util import store_method, save_json
    method = lciafmt.Method.USETOX
    df = get(method)
    mapping = method.get_metadata()['mapping']
    #%%
    mapped_df = lciafmt.map_flows(df, system=mapping)
    # store_method(df, method)
    # save_json(method, df)
