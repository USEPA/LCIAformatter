# ced.py (lciafmt)
# !/usr/bin/env python3
# coding=utf-8
"""
Generate method for Cumulative Energy Demand (CED)
"""

import numpy as np
import pandas as pd

import lciafmt
from lciafmt.util import store_method


def get() -> pd.DataFrame():

    inv_orig = lciafmt.get_method(method_id = 'FEDEFL_INV', subset = ['ced'])
    inv = inv_orig.copy()
    inv['Indicator'] = ''
    inv['Method'] = 'Cumulative Energy Demand'

    conditions = [
        inv['Flowable'].isin(['Wood, primary forest']),
        inv['Flowable'].isin(['Biomass', 'Softwood', 'Hardwood', 'Wood']),
        inv['Flowable'].isin(['Energy, hydro']),
        inv['Flowable'].str.contains('|'.join(['wind', 'solar', 'geothermal'])),
        inv['Flowable'].str.contains('Uranium'),
        inv['Flowable'].str.contains('|'.join(['Coal', 'Oil', 'Crude',
                                               'gas', 'Methane'])),
        ]

    indicators = ['Non-renewable, biomass',
                  'Renewable, biomass',
                  'Renewable, water',
                  'Renewable, wind, solar, geothermal',
                  'Non-renewable, nuclear',
                  'Non-renewable, fossil',
                  ]
    inv['Indicator'] = np.select(conditions, indicators, default='')

    ## Original CED Method included the
    # "Energy, fossil, unspecified" technosphere flow
    # https://www.lcacommons.gov/lca-collaboration/National_Renewable_Energy_Laboratory/USLCI_Database_Public/dataset/FLOW/46dc4693-2f24-39d2-b69f-dd059737fd5e

    ## Original CED Method used HHV for biomass/wood flows
    # Some wood flows were removed after the original method in FEDEFLv1.0.8

    # Dropped flows from FEDEFL inv method: "Hydrogen", "Energy, heat"

    inv = inv.query('Indicator != ""').reset_index(drop=True)

    return inv


if __name__ == "__main__":
    method = lciafmt.Method.CED
    df = get()
    store_method(df, method)
    lciafmt.util.save_json(method, df)
