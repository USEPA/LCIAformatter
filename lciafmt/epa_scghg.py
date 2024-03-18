# epa_scghg.py (lciafmt)
# !/usr/bin/env python3
# coding=utf-8
"""
This module contains functions needed to develop life cycle inventory methods
for EPA's Social Cost of Greenhouse Gases
https://www.epa.gov/environmental-economics/scghg
"""

import pandas as pd
import lciafmt
import lciafmt.df as dfutil
from lciafmt.util import store_method, save_json


def get() -> pd.DataFrame:
    """Generate an inventory method from EPA SCGHG.

    :return: df in standard LCIAmethod format
    """
    method = dfutil.data_frame(list())
    method_meta = lciafmt.Method.EPA_SCGHG.get_metadata()
    df = pd.read_csv(method_meta['url'], thousands=',')
    df.columns = ['Flowable', 'EmissionYear', ' (2.5%)', ' (2.0%)', ' (1.5%)']
    df = (df.melt(id_vars=['Flowable', 'EmissionYear'], var_name='discount_rate',
                  value_name='Characterization Factor')
            .assign(Indicator = lambda x: x['EmissionYear'].astype(str) +
                    x['discount_rate'])
            .drop(columns=['EmissionYear', 'discount_rate'])
            )
    method = pd.concat([method, df])
    method['Context'] = 'air'
    # Original source factors are in $ per metric tonne
    method['Unit'] = 'MT'
    method['Indicator unit'] = 'USD / kg'
    # ^^ Units following flow mapping and conversion
    method['Method'] = method_meta['name']

    return method

if __name__ == "__main__":
    method = lciafmt.Method.EPA_SCGHG
    df = get()
    mapped_df = lciafmt.map_flows(
        df, system=method.get_metadata()['mapping'])
    store_method(mapped_df, method)
    save_json(method, mapped_df)
