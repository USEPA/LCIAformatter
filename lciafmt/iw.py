# iw.py (lciafmt)
# !/usr/bin/env python3
# coding=utf-8
"""
This module contains functions needed to compile LCIA methods from ImpactWorld+
"""

import pandas as pd
import lciafmt.cache as cache
import lciafmt.df as dfutil
from lciafmt.util import log, format_cas

try:
    import pyodbc
except ImportError:
    log.error("Must install pyodbc for ImpactWorld. See install instructions "
              "for optional package installation or install it independently "
              "and retry.")


def get(file=None, url=None) -> pd.DataFrame:
    """Generate a method for ImpactWorld+ in standard format.

    :param file: str, alternate filepath for method, defaults to file stored
        in cache
    :param url: str, alternate url for method, defaults to url in method config
    :return: DataFrame of method in standard format
    """
    log.info("get method ImpactWorld+")

    # Check for drivers and display help message if absent
    driver_check = ([x for x in pyodbc.drivers()])
    if any('Microsoft Access Driver' in word for word in driver_check):
        log.debug("Drivers Available")
    else:
        log.warning(
            "Please install drivers to remotely connect to Access Database. "
            "Drivers only available on windows platform. For instructions visit: "
            "https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-Microsoft-Access")

    f = file
    if f is None:
        fname = "Impact_World.accdb"
        if url is None:
            url = "https://www.dropbox.com/sh/2sdgbqf08yn91bc/AABIGLlb_OwfNy6oMMDZNrm0a/IWplus_public_v1.3.accdb?dl=1"
        f = cache.get_or_download(fname, url)
    df = _read(f)

    # Identify midpoint and endpoint records and differentiate in data frame.
    end_point_units = ['DALY', 'PDF.m2.yr']

    df.loc[df["Indicator unit"].isin(end_point_units), ["Method"]] = "ImpactWorld+ - Endpoint"
    df.loc[~df["Indicator unit"].isin(end_point_units), ["Method"]] = "ImpactWorld+ - Midpoint"

    # call function to replace contexts for unspecified water and air flows.
    df = update_context(df)

    return df


def _read(access_file: str) -> pd.DataFrame:
    """Read the Access database at passed access_file into DataFrame."""
    log.info(f"read ImpactWorld+ from file {access_file}")

    path = cache.get_path(access_file)

    connStr = (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        r'DBQ=' + path + ";")

    cnxn = pyodbc.connect(connStr)
    crsr = cnxn.cursor()
    records = []

    # Extract non regionalized data from "CF - not regionalized - All other impact categories"
    crsr.execute("SELECT * FROM [CF - not regionalized - All other impact categories]")
    rows = crsr.fetchall()
    for row in rows:
        dfutil.record(records,
                      method="ImpactWorld+",
                      indicator=row[1],
                      indicator_unit=row[2],
                      flow=row[5],
                      flow_category=row[3] + "/" + row[4],
                      flow_unit=row[8],
                      cas_number=format_cas(row[6]).lstrip("0"),
                      factor=row[7])

    """List relevant sheets in Impact World Access file. Second item in tuple
    tells the source of compartment information. Compartment for water
    categories are not included in access file, defined below. Elementary flow
    names are used to define the compartment for land transformation and
    occupation. Compartment and Subcompartment data is available in the Access
    file for other categories."""
    regional_sheets = [("CF - regionalized - WaterScarc - aggregated", "Raw/in water"),
                       ("CF - regionalized - WaterAvailab_HH - aggregated", "Raw/in water"),
                       ("CF - regionalized - LandTrans - aggregated", "Elementary Flow"),
                       ("CF - regionalized - LandOcc - aggregated", "Elementary Flow"),
                       ("CF - regionalized - EutroMar - aggregated", "Compartment"),
                       ("CF - regionalized - PartMatterForm - aggregated", "Compartment"),
                       ("CF - regionalized - AcidFW - aggregated", "Compartment"),
                       ("CF - regionalized - AcidTerr - aggregated", "Compartment"),
                       ("CF - regionalized - EutroFW - aggregated", "Compartment"),
                       ]

    for x in regional_sheets:
        if x[0] == "CF - regionalized - PartMatterForm - aggregated":
            # Extract global flows from the particulate matter Access sheet
            # Structure of this sheet is
            sql = "SELECT * FROM [" + x[0] + "] WHERE (([" + x[0] + "].Region In('World')))"
            crsr.execute(sql)
            rows = crsr.fetchall()

            for row in rows:
                dfutil.record(records,
                              method="ImpactWorld+",
                              indicator=row.ImpCat,
                              indicator_unit=row.Unit.strip('[]').split('/')[0],
                              flow=row.__getattribute__('Elem flow'),
                              flow_category="Air/" + row.__getattribute__("Archetype 1"),
                              flow_unit=row.Unit.strip('[]').split('/')[1],
                              cas_number="",
                              factor=row.CFvalue)

        else:
            sql = "SELECT * FROM [" + x[0] + "] WHERE (([" + x[0] + "].Resolution In('Global', 'Not regionalized')))"
            crsr.execute(sql)
            rows = crsr.fetchall()

            # extract column headers from Access sheet for exception testing
            cols = [column[0] for column in crsr.description]

            for row in rows:
                # Add water to detailed context information available in Access file
                if x[0] in ['CF - regionalized - WaterScarc - aggregated',
                            'CF - regionalized - WaterAvailab_HH - aggregated']:
                    flow_stmt = 'Water, ' + row.__getattribute__('Elem flow')
                else:
                    flow_stmt = row.__getattribute__('Elem flow')

                # Define context/compartment for flow based on impact category.
                if {'Compartment', 'Subcompartment'}.issubset(cols):
                    category_stmt = row.Compartment + "/" + row.Subcompartment
                elif x[0] in ['CF - regionalized - LandTrans - aggregated',
                              'CF - regionalized - LandOcc - aggregated',
                              'CF - regionalized - WaterScarc - aggregated',
                              'CF - regionalized - WaterAvailab_HH - aggregated']:
                    category_stmt = flow_stmt
                else:
                    category_stmt = x[1]

                dfutil.record(records,
                              method="ImpactWorld+",
                              indicator=row.ImpCat,
                              indicator_unit=row.Unit.strip('[]').split('/')[0],
                              flow=flow_stmt,
                              flow_category=category_stmt,
                              flow_unit=row.Unit.strip('[]').split('/')[1],
                              cas_number="",
                              factor=row.__getattribute__('Weighted Average'))

    return dfutil.data_frame(records)


def update_context(df_context) -> pd.DataFrame:
    """Replace unspecified contexts for indicators.

    For indicators that don't rely on sub-compartments for characterization
    factor selection, update the context for improved context mapping.
    """
    single_context = ['Freshwater acidification',
                      'Terrestrial acidification',
                      'Climate change, long term',
                      'Climate change, short term',
                      'Climate change, ecosystem quality, short term',
                      'Climate change, ecosystem quality, long term',
                      'Climate change, human health, short term',
                      'Climate change, human health, long term',
                      'Photochemical oxidant formation',
                      'Ozone Layer Depletion',
                      'Ozone layer depletion',
                      'Marine acidification, short term',
                      'Marine acidification, long term',
                      'Ionizing radiations',
                      ]

    context = {'Air/(unspecified)': 'Air',
               # 'Water/(unspecified)': 'Water',
               }

    df_context.loc[df_context['Indicator'].isin(single_context),
                   'Context'] = df_context['Context'].map(context).fillna(df_context['Context'])

    return df_context
