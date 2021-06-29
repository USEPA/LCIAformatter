# traci.py (lciafmt)
# !/usr/bin/env python3
# coding=utf-8
"""
This module contains functions needed to compile LCIA methods from EPA's
Tool for Reduction and Assessment of Chemicals and Other Environmental
Impacts (TRACI)
"""

import pandas as pd
import openpyxl

import lciafmt.cache as cache
import lciafmt.df as dfutil
import lciafmt.xls as xls

from .util import log, aggregate_factors_for_primary_contexts, format_cas, datapath


flowables_replace = pd.read_csv(datapath+'TRACI_2.1_replacement.csv')
flowables_split = pd.read_csv(datapath+'TRACI_2.1_split.csv')


def get(add_factors_for_missing_contexts=True, file=None, url=None) -> pd.DataFrame:
    """  Downloads and processes the TRACI impact method. """
    log.info("getting method Traci 2.1")
    f = file
    if f is None:
        fname = "traci_2.1.xlsx"
        if url is None:
            url = ("https://www.epa.gov/sites/production/files/2015-12/" +
                   "traci_2_1_2014_dec_10_0.xlsx")
        f = cache.get_or_download(fname, url)
    df = _read(f)
    if add_factors_for_missing_contexts:
        log.info("adding average factors for primary contexts")
        df = aggregate_factors_for_primary_contexts(df)

    log.info("handling manual replacements")
    """ due to substances listed more than once with different names
    this replaces all instances of the Original Flowable with a New Flowable
    based on a csv input file, otherwise zero values for CFs will override
    when there are duplicate names"""
    for index, row in flowables_replace.iterrows():
        orig = row['Original Flowable']
        new = row['New Flowable']
        df['Flowable']=df['Flowable'].replace(orig, new)

    """ due to substances listed more than once with the same name but different CAS
    this replaces all instances of the Original Flowable with a New Flowable
    based on a csv input file according to the CAS"""
    for index, row in flowables_split.iterrows():
        cas = row['CAS']
        new = row['New Flowable']
        df.loc[df['CAS No'] == cas, 'Flowable'] = new

    length=len(df)
    df.drop_duplicates(keep='first',inplace=True)
    length=length-len(df)
    log.info("%s duplicate entries removed", length)

    return df


def _read(xls_file: str) -> pd.DataFrame:
    """Read the data from the Excel file with the given path into a Pandas
       data frame."""

    log.info("read Traci 2.1 from file %s", xls_file)
    wb = openpyxl.load_workbook(xls_file, read_only = True)
    sheet = wb["Substances"]
    df = pd.read_excel(xls_file, sheet_name='Substances')
    categories = {}
    for col in range(4, sheet.max_column):
        name = xls.cell_str(sheet, 1, col)
        if name == "":
            break
        cat_info = _category_info(name)
        if cat_info is not None:
            categories[col] = cat_info

    records = []
    for row in range(2, sheet.max_row):
        print(row)
        flow = xls.cell_str(sheet, row, 3)
        if flow == "":
            break
        cas = format_cas(xls.cell_val(sheet, row, 2))
        for col in range(4, sheet.max_column):
            cat_info = categories.get(col)
            if cat_info is None:
                continue
            factor = xls.cell_f64(sheet, row, col)
            if factor == 0.0:
                continue
            dfutil.record(records,
                          method="TRACI 2.1",
                          indicator=cat_info[0],
                          indicator_unit=cat_info[1],
                          flow=flow,
                          flow_category=cat_info[2],
                          flow_unit=cat_info[3],
                          cas_number=cas,
                          factor=factor)

    return dfutil.data_frame(records)


def _category_info(c: str):
    """"Get the meta data which are encoded in the category name. It returns
        a tuple (indicator, indicator unit, flow category, flow unit) for the
        given category name. If it is an unknown category, `None` is returned.
    """

    if c == "Global Warming Air (kg CO2 eq / kg substance)":
        return "Global warming", "kg CO2 eq", "air", "kg"

    if c == "Acidification Air (kg SO2 eq / kg substance)":
        return "Acidification", "kg SO2 eq", "air", "kg"

    if c == "HH Particulate Air (PM2.5 eq / kg substance)":
        return ("Human health - particulate matter", "PM 2.5 eq",
                "air", "kg")

    if c == "Eutrophication Air (kg N eq / kg substance)":
        return "Eutrophication", "kg N eq", "air", "kg"

    if c == "Eutrophication Water (kg N eq / kg substance)":
        return "Eutrophication", "kg N eq", "water", "kg"

    if c == "Ozone Depletion Air (kg CFC-11 eq / kg substance)":
        return "Ozone depletion", "kg CFC-11 eq", "air", "kg"

    if c == "Smog Air (kg O3 eq / kg substance)":
        return "Smog formation", "kg O3 eq", "air", "kg"

    if c == "Ecotox. CF [CTUeco/kg], Em.airU, freshwater":
        return "Freshwater ecotoxicity", "CTUeco", "air/urban", "kg"

    if c == "Ecotox. CF [CTUeco/kg], Em.airC, freshwater":
        return "Freshwater ecotoxicity", "CTUeco", "air/rural", "kg"

    if c == "Ecotox. CF [CTUeco/kg], Em.fr.waterC, freshwater":
        return "Freshwater ecotoxicity", "CTUeco", "water/freshwater", "kg"

    if c == "Ecotox. CF [CTUeco/kg], Em.sea waterC, freshwater":
        return "Freshwater ecotoxicity", "CTUeco", "water/sea water", "kg"

    if c == "Ecotox. CF [CTUeco/kg], Em.nat.soilC, freshwater":
        return "Freshwater ecotoxicity", "CTUeco", "soil/natural", "kg"

    if c == "Ecotox. CF [CTUeco/kg], Em.agr.soilC, freshwater":
        return "Freshwater ecotoxicity", "CTUeco", "soil/agricultural", "kg"

    if c == "Human health CF  [CTUcancer/kg], Emission to urban air, cancer":
        return "Human health - cancer", "CTUcancer", "air/urban", "kg"

    if c == "Human health CF  [CTUnoncancer/kg], Emission to urban air, non-canc.":
        return "Human health - non-cancer", "CTUnoncancer", "air/urban", "kg"

    if c == "Human health CF  [CTUcancer/kg], Emission to cont. rural air, cancer":
        return "Human health - cancer", "CTUcancer", "air/rural", "kg"

    if c == "Human health CF  [CTUnoncancer/kg], Emission to cont. rural air, non-canc.":
        return "Human health - non-cancer", "CTUnoncancer", "air/rural", "kg"

    if c == "Human health CF  [CTUcancer/kg], Emission to cont. freshwater, cancer":
        return "Human health - cancer", "CTUcancer", "water/freshwater", "kg"

    if c == "Human health CF  [CTUnoncancer/kg], Emission to cont. freshwater, non-canc.":
        return "Human health - non-cancer", "CTUnoncancer", "water/freshwater", "kg"

    if c == "Human health CF  [CTUcancer/kg], Emission to cont. sea water, cancer":
        return "Human health - cancer", "CTUcancer", "water/sea water", "kg"

    if c == "Human health CF  [CTUnoncancer/kg], Emission to cont. sea water, non-canc.":
        return "Human health - non-cancer", "CTUnoncancer", "water/sea water", "kg"

    if c == "Human health CF  [CTUcancer/kg], Emission to cont. natural soil, cancer":
        return "Human health - cancer", "CTUcancer", "soil/natural", "kg"

    if c == "Human health CF  [CTUnoncancer/kg], Emission to cont. natural soil, non-canc.":
        return "Human health - non-cancer", "CTUnoncancer", "soil/natural", "kg"

    if c == "Human health CF  [CTUcancer/kg], Emission to cont. agric. Soil, cancer":
        return "Human health - cancer", "CTUcancer", "soil/agricultural", "kg"

    if c == "Human health CF  [CTUnoncancer/kg], Emission to cont. agric. Soil, non-canc.":
        return "Human health - non-cancer", "CTUnoncancer", "soil/agricultural", "kg"
