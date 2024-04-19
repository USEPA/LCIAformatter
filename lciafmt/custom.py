# custom.py (lciafmt)
# !/usr/bin/env python3
# coding=utf-8
"""
Functions to create custom manual methods
"""

import pandas as pd
from pathlib import Path
import yaml

import lciafmt
from lciafmt.df import lciafmt_cols
from lciafmt.util import datapath

def get_custom_method(file: str=None, input_df=None):
    """Converts a dataframe or a csv filepath to a dataframe suitable for
    lciafmt. If `file` is passed, input_df is ignored.
    """
    if file:
        input_df = pd.read_csv(file)
    if (pd.Series(['Characterization Factor', 'Flowable', 'Context'])
            .isin(input_df.columns).all()):
        df = input_df.reindex(columns=lciafmt_cols)
        df = df.fillna('')
        return df
    else:
        raise Exception


def generate_lcia_compilation(filename: str,
                              filepath: Path=None
                              ) -> pd.DataFrame:
    """Generates a dataframe consisting of indicators from various LCIA methods
    based on specs provided in yaml file.
    """
    if not filepath:
        filepath = datapath
    with open(filepath / filename) as f:
        build_file = yaml.safe_load(f)
    build_df = pd.DataFrame(build_file['indicators']).transpose()

    indicator_dict = (build_df.groupby('method')
                      .apply(lambda x: [y for y in x['indicator']])
                      .to_dict())
    name_dict = build_df['indicator'].to_dict()
    code_dict = {}
    if 'code' in build_df:
        code_dict = build_df['code'].to_dict()

    method_list = []
    for method, indicators in indicator_dict.items():
        df = lciafmt.get_mapped_method(method_id = method,
                                       indicators = indicators,
                                       methods = [method])
        method_list.append(df)

    df = pd.concat(method_list, ignore_index=True)

    df['category'] = df['Method']
    df['source_method'] = df['Method']
    df['Method'] = build_file.get('name')
    if build_file.get('rename_indicators', False):
        df['category'] = df['Method']
        df['source_indicator'] = df['Indicator']
        df['Indicator'] = df['Indicator'].replace({v: k for k, v in name_dict.items()})
        if code_dict:
            df['Code'] = df['Indicator'].map(code_dict)

    return df


if __name__ == "__main__":
    df = generate_lcia_compilation('epd.yaml')
    name = df['Method'][0]
    lciafmt.util.store_method(df, method_id=None, name=name)
    lciafmt.util.save_json(method_id=None, mapped_data=df, name=name)
