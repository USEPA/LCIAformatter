# odp.py (lciafmt)
# !/usr/bin/env python3
# coding=utf-8
"""
This module contains functions needed to compile LCIA methods from the
Annex to the World Meteorological Organizations Scientific Asssessment of Ozone Depletion 2022
Document Title: ANNEX: Summary of Abundances, Lifetimes, ODPs, REs, GWPs, and GTPs.
Available at: https://csl.noaa.gov/assessments/ozone/2022/downloads/Annex_2022OzoneAssessment.pdf
"""

import pandas as pd
import openpyxl as pyxl

import lciafmt.cache as cache
import lciafmt.df as dfutil
import lciafmt.xls as xls
import codecs

from util import log


# The Annex file mentioned in the script header was converted to a csv format by the developers and provided to ERG. 
# The csv source file is located in the data folder associated with this package. 
log.info("read ODP factors from file")
# BenY, is there a good way to set it up so the file path is adjusted to reflect the users local machine when the repo is cloned? 
wb = pyxl.load_workbook('C:\\Users\\bmorelli\\Code\\lciafmt\\lciafmt\\data\\Annex.Formatted.xlsx', read_only=True, data_only=True)
print("opened")
sheet = wb['Sheet1']
data = sheet.values
print("loaded")
columns = next(data)  # Assuming the first row contains column names
df = pd.DataFrame(data, columns=columns)
print("in df")

# Write to a CSV file 
with codecs.open('odp_factors.csv', 'w', 'utf-8-sig') as f: #codex includes BOM label in generated csv file to tell Excel how to decode accurately.
    df.to_csv(f, index=False)  # Set index=False to exclude row numbers


# Assign FEDEFL contexts to ODP flowables.
# The original file contains no context information. It is assumed that all flowables have a context of 'Elementary flows/emission/air'