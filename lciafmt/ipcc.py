# ipcc.py (lciafmt)
# !/usr/bin/env python3
# coding=utf-8
"""
This module contains functions needed to compile LCIA methods from IPCC
"""

import pandas as pd
from lciafmt.util import log, datapath


def get() -> pd.DataFrame:
    """Generate a method for IPCC in standard format.
    :return: DataFrame of method in standard format
    """
    log.info("get method IPCC")

    filename = ''
    df = pd.read_csv(datapath + filename)



    return df
