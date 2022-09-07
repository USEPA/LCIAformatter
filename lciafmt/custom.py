# custom.py (lciafmt)
# !/usr/bin/env python3
# coding=utf-8
"""
Functions to create custom manual methods
"""

import pandas as pd

from lciafmt.df import lciafmt_cols

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

