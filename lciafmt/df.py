# df.py (lciafmt)
# !/usr/bin/env python3
# coding=utf-8
"""
Functions to support generating a dataframe from list of elements
"""

import pandas

lciafmt_cols = [
    "Method",
    "Method UUID",
    "Indicator",
    "Indicator UUID",
    "Indicator unit",
    "Flowable",
    "Flow UUID",
    "Context",
    "Unit",
    "CAS No",
    "Location",
    "Location UUID",
    "Characterization Factor"
    ]

def data_frame(records: list) -> pandas.DataFrame:
    """Convert the given list of lists into a data frame."""
    return pandas.DataFrame(records, columns=lciafmt_cols)


def as_list(df: pandas.DataFrame, row=-1) -> list:
    """Converts the given data frame into a list of lists. When the `row`
    paremeter is given with a value >= 0, only that row is extracted as
    list from the data frame.
    """
    if df is None:
        return []
    if row >= 0:
        rec = []
        for col in range(0, 13):
            rec.append(df.iat[row, col])
        return rec
    recs = []
    for row in range(df.shape[0]):
        recs.append(as_list(df, row=row))


def record(records: list,
           method="",
           method_uuid="",
           indicator="",
           indicator_uuid="",
           indicator_unit="",
           flow="",
           flow_uuid="",
           flow_category="",
           flow_unit="",
           cas_number="",
           location="",
           location_uuid="",
           factor=0.0) -> list:
    """Append a new row to the given list (which may be the empty list)."""
    records.append([
        method,
        method_uuid,
        indicator,
        indicator_uuid,
        indicator_unit,
        flow,
        flow_uuid,
        flow_category,
        flow_unit,
        cas_number,
        location,
        location_uuid,
        factor])
    return records
