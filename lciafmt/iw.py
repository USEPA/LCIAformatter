import pyodbc
import logging as log
import pandas
import lciafmt.cache as cache
import lciafmt.df as df
import lciafmt.util as util

# Check for drivers and display help message if absent
Driver_Check = ([x for x in pyodbc.drivers()])
if any('Microsoft Access Driver' in word for word in Driver_Check):
    print("Drivers Available")
else:
    print("Please install drivers to remotely connect to Access Database. Drivers only available on windows platform. "
          "For instructions visit: https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-Microsoft-Access")

# Download Access file and call read function to transfer into dataframe
def get(endpoint=False, file=None, url=None) -> pandas.DataFrame:
    log.info("get method Impact World")
    f = file
    if f is None:
        fname = "Impact_World.accdb"
        if url is None:
            url = ("https://www.dropbox.com/sh/2sdgbqf08yn91bc/AABIGLlb_OwfNy6oMMDZNrm0a/IWplus_public_v1.3.accdb?dl=1")
        f = cache.get_or_download(fname, url)
    df = _read(f)

    # Identify midpoint and endpoint records and differentiate in data frame.
    end_point_units = ['DALY', 'PDF.m2.yr']

    if endpoint:
        df = df[df["Indicator unit"].isin(end_point_units)]
        df["Method"] = "Impact World - Endpoint"
    else:
        df = df[~df["Indicator unit"].isin(end_point_units)]
        df["Method"] = "Impact World - Midpoint"
    
    return df

# Read cached Access file into dataframe.
def _read(access_file: str) -> pandas.DataFrame:
    """Read the data from the Access database with the given path into a Pandas data frame."""

    log.info("read Impact World from file %s", access_file)

    path = cache.get_path(access_file)

    connStr = (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        r'DBQ=' + path + ";")

    cnxn = pyodbc.connect(connStr)
    crsr = cnxn.cursor()

# List relevant sheets in Impact World Access file. Second item in tuple tells the source of compartment information.
# Compartment for water categories are not included in access file, defined below.
# Elementary flow names are used to define the compartment for land transformation and occupation
# Compartment and Subcompartment data is available in the Access file for other categories.
    Regional_sheets = [("CF - regionalized - WaterScarc - aggregated", "Raw/in water"),
                       ("CF - regionalized - WaterAvailab_HH - aggregated", "Raw/in water"),
                       ("CF - regionalized - LandTrans - aggregated", "Elementary Flow"),
                       ("CF - regionalized - LandOcc - aggregated", "Elementary Flow"),
                       ("CF - regionalized - EutroMar - aggregated", "Compartment"),
                       ("CF - regionalized - PartMatterForm - aggregated","Compartment"),
                       ("CF - regionalized - AcidFW - aggregated", "Compartment"),
                       ("CF - regionalized - AcidTerr - aggregated", "Compartment"),
                       ("CF - regionalized - EutroFW - aggregated", "Compartment"),
                       ("CF - not regionalized - All other impact categories", "Compartment")]

    records = []

    for x in Regional_sheets:
        # Extract all data from Access sheet containing non-regionalized flows and write to records.
        if x[0] == "CF - not regionalized - All other impact categories":
            crsr.execute("SELECT * FROM [CF - not regionalized - All other impact categories]")
            rows = crsr.fetchall()
            for row in rows:
                df.record(
                    records,
                    method="Impact World",
                    indicator = row[1],
                    indicator_unit=row[2],
                    flow=row[5],
                    flow_category=row[3] + "/" + row[4],
                    flow_unit=row[8],
                    cas_number=util.format_cas(row[6]).lstrip("0"),
                    factor=row[7])

        elif x[0] == "CF - regionalized - PartMatterForm - aggregated":
            # Extract global flows from the particulate matter Access sheet
            # Structure of this sheet is
            sql = "SELECT * FROM [" + x[0] + "] WHERE (([" + x[0] + "].Region In('World')))"
            crsr.execute(sql)
            rows = crsr.fetchall()

            for row in rows:
                df.record(
                    records,
                    method="Impact World",
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

            cols = [column[0] for column in crsr.description]

            for row in rows:

                #Add water to detailed context information available in Access file
                if x[0] in ['CF - regionalized - WaterScarc - aggregated', 'CF - regionalized - WaterAvailab_HH - aggregated']:
                    flow_stmt = 'Water, ' + row.__getattribute__('Elem flow')
                else:
                    flow_stmt = row.__getattribute__('Elem flow')

                # Define context/compartment for flow based on impact category.
                if {'Compartment', 'Subcompartment'}.issubset(cols):
                    category_stmt = row.Compartment + "/" + row.Subcompartment
                elif x[0] in ['CF - regionalized - LandTrans - aggregated', 'CF - regionalized - LandOcc - aggregated']:
                    category_stmt = row.__getattribute__('Elem flow')
                else:
                    category_stmt = x[1]

                df.record(
                    records,
                    method="Impact World",
                    indicator = row.ImpCat,
                    indicator_unit=row.Unit.strip('[]').split('/')[0],
                    flow=flow_stmt,
                    flow_category=category_stmt,
                    flow_unit=row.Unit.strip('[]').split('/')[1],
                    cas_number="",
                    factor=row.__getattribute__('Weighted Average'))

    return df.data_frame(records)



