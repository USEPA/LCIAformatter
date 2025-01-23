# odp.py (lciafmt)
# !/usr/bin/env python3
# coding=utf-8
"""
This module contains functions needed to compile LCIA methods from the
Annex to the World Meteorological Organizations Scientific Asssessment of Ozone Depletion 2022
Document Title: ANNEX: Summary of Abundances, Lifetimes, ODPs, REs, GWPs, and GTPs.
Available at: https://csl.noaa.gov/assessments/ozone/2022/downloads/Annex_2022OzoneAssessment.pdf
"""
"""
Key Assumptions: 
     # compounds with ODP or GWP == 0 are excluded from the respective method.
     # Table A-5 footnote GWP/GTP Footnote:
        #"GWP and GTP values that are less then 0.1 are reported as “<<1” in the table. GWP and GTP values that are between 0.1 and 1
        are reported as “<1” in the table."
     # Table A-5 footnote O11 states that values with < symbol are the upper limit of identified values
     # compounds with a GWP and ODP labeled '<x' are set equal to 1*x
     # compounds with a GWP labeled '<<x' are set equal to 0.1*x
     # compounds with a ODP labeled '>' are set equal to 1*x. No guidance was identified to inform selection of a higher number. 
     # compounds with a GWP labeled '~' are set equal to x.

     # The original file contains no context information. All flowables are assigned the context 'Elementary flows/emission/air'. 

"""
import pandas as pd
import openpyxl as pyxl

import lciafmt.cache as cache
import lciafmt.df as dfutil
import lciafmt.xls as xls
import codecs
import re 
from util import log


# The Annex file mentioned in the script header was converted to a csv format by the developers and provided to ERG. 
# The csv source file is located in the data folder associated with this package. 
log.info("read ODP factors from file")
# BenY
    # Is there a good way to set it up so the file path is adjusted to reflect the users local machine when the repo is cloned? 
wb = pyxl.load_workbook('C:\\Users\\bmorelli\\Code\\lciafmt\\lciafmt\\data\\Annex.Formatted.xlsx', read_only=True, data_only=True)
print("opened")
sheet = wb['Sheet1']
data = sheet.values
print(type(data))
print("loaded")
columns = next(data)  # Assuming the first row contains column names
df = pd.DataFrame(data, columns=columns)
# print(df)

# Write input dataframe to a CSV file 
# Purpose of this file is for visualizing the dataframe and QC.
with codecs.open('odp_factors.csv', 'w', 'utf-8-sig') as f: #codecs includes BOM label in generated csv file to tell Excel how to decode accurately.
    df.to_csv(f, index=False)  # Set index=False to exclude row numbers

#initialize blank list to record LCIA data using dfutil.records
records = []
skippedrows = [['row number', 'ODP', 'GWP100']]  # to examine compounds with multirow entries.
not_number = [ ] # check for special characters to deal with.

#order of special characters matters. If '<' is before '<<' it will create separate rows for each factor containing '<<'.
special_characters = {
    '~': 1,
    '<<': 0.1,
    '<': 1,
    '>': 1
}
for index, row in df.iterrows():
    # These cas numbers are being encoded as dates when written to Excel. Don't appear to be an issue within python. 
    if row['Industrial Designation or Chemical Name'] in ['HCFC-234cb', 'HCFC-241ac', 'HCFC-242ac', 'HCFC-242bc', 'HCFC-243ab']:
        print(row['CAS RN'])
    #Check that rows with missing chemical name do not contain valuable information.
    #If you examine the dataframe generated above, you will see that multirow entries (i.e. merged in excel) for a single chemical get parsed to multiple rows in the dataframe.
    #Rows other than the first row do not contain a chemical name and based on visual inspection are not known to contain GWP or ODP data that we are looking to extract.
    #This if test creates a list of blank rows and extracts the potentially useful data is not missed. If Identified, it will be dealt with. 
    if row['Industrial Designation or Chemical Name'] in [None, '']:
        skippedrows.append([index, row['ODP'], row['GWP 100-yr']])
    # Build list in standard format for conversion to a dataframe.
    # check if the ODP factor is a non-zero number. 
    else: 
        if row['ODP'] not in ['', 0, '–', None, 'xxx']:
            if isinstance(row['ODP'], (int, float)):
                odpCF = row['ODP']
            else:
                not_number.append(row['ODP'])
                #strip off special characters and multiply by defined factor for each special character.
                for item in special_characters:
                    if item in row['ODP']:
                        odpCF = float(row['ODP'].replace(item, ''))*float(special_characters[item])
                        break
            dfutil.record(records,
                        method='NOAA',
                        indicator='Ozone Depletion Potential', 
                        indicator_unit='kg CFC-11 equivalent',
                        flow=row['Industrial Designation or Chemical Name'],
                        flow_category='air',
                        flow_unit='kg', 
                        cas_number="'"+row['CAS RN'], # single quote inserted to prevent excel from interpreting as date
                        location='Global',
                        factor=odpCF)
        # check if the GWP factor is a non-zero number. 
        if row['GWP 100-yr'] not in ['', 0, '–', None, 'xxx']:
            if isinstance(row['GWP 100-yr'], (int, float)):
                gwpCF = row['GWP 100-yr']
            else:
                not_number.append(row['GWP 100-yr'])
                #strip off special characters and multiply by defined factor for each special character.
                for item in special_characters:
                    if item in row['GWP 100-yr']:
                        gwpCF = float(row['GWP 100-yr'].replace(item, ''))*float(special_characters[item])
                        break 
            dfutil.record(records,
                        method='NOAA',
                        indicator='Climate Change Potential', 
                        indicator_unit='kg CO2 equivalent',
                        flow=row['Industrial Designation or Chemical Name'],
                        flow_category='air',
                        flow_unit='kg', 
                        cas_number="'"+row['CAS RN'], # single quote inserted to prevent excel from interpreting as date
                        location='Global',
                        factor=gwpCF)   

output_df = dfutil.data_frame(records)
output_df['CAS No'] = output_df['CAS No'].astype(str)
                    
# Write output dataframe to a CSV file 
# Purpose of this file is for visualizing the dataframe and QC.
with codecs.open('noaa_records.csv', 'w', 'utf-8-sig') as f: #codex includes BOM label in generated csv file to tell Excel how to decode accurately.
    output_df.to_csv(f, index=False)  # Set index=False to exclude row numbers

# create csv to examine skipped rows
skipped_df = pd.DataFrame(skippedrows)                
with codecs.open('skipped_records.csv', 'w', 'utf-8-sig') as f: #codex includes BOM label in generated csv file to tell Excel how to decode accurately.
    skipped_df.to_csv(f, index=False)  # Set index=False to exclude row numbers

# create csv to examine non-numbers
number_df = pd.DataFrame(not_number)                
with codecs.open('not_number.csv', 'w', 'utf-8-sig') as f: #codex includes BOM label in generated csv file to tell Excel how to decode accurately.
    number_df.to_csv(f, index=False)  # Set index=False to exclude row numbers 