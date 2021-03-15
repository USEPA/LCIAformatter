# fedefl_inventory.py (lciafmt)
# !/usr/bin/env python3
# coding=utf-8
"""
This module contains functions needed to develop life cycle inventory methods
from the EPA Federal Elementary Flow List (fedelemflowlist)
(https://github.com/USEPA/Federal-LCA-Commons-Elementary-Flow-List)
"""
import pandas as pd

import fedelemflowlist as flowlist
import fedelemflowlist.subset_list as subsets

import lciafmt.df as dfutil


def get(subset=None) -> pd.DataFrame:
    """
    Returns a dataframe of inventory based methods.
    :param subset: a list of dictionary keys from available inventories, if
    none selected all availabile inventories will be generated
    :return: df in standard LCIAmethod format
    """
    method = dfutil.data_frame(list())
    method['Characterization Factor'] = pd.to_numeric(method['Characterization Factor'])

    if subset is None:
        list_of_inventories = subsets.get_subsets()
    else:
        list_of_inventories = subset

    alt_units = flowlist.get_alt_conversion()
    for inventory in list_of_inventories:
        flows = flowlist.get_flows(subset=inventory)
        flows.drop(['Formula','Synonyms','Class','External Reference',
                    'Preferred', 'AltUnit','AltUnitConversionFactor'], axis=1, inplace=True)
        flows['Indicator'] = inventory
        flows['Indicator unit'] = subsets.get_inventory_unit(inventory)
        flows['Characterization Factor'] = 1

        # Apply unit conversions where flow unit differs from indicator unit
        flows_w_conversion = pd.merge(flows, alt_units, how='left',
                                      left_on=['Flowable','Indicator unit', 'Unit'],
                                      right_on=['Flowable','AltUnit', 'Unit'])
        flows_w_conversion.loc[
            (flows_w_conversion['AltUnit']==flows_w_conversion['Indicator unit']),
            'Characterization Factor'] = flows_w_conversion['AltUnitConversionFactor']
        flows_w_conversion.drop(
            ['AltUnit','AltUnitConversionFactor','InverseConversionFactor'],
            axis=1, inplace=True)

        method = pd.concat([method,flows_w_conversion], ignore_index=True)

    method['Method'] = 'Inventory'
    return method
