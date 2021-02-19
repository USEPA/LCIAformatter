import pyodbc
import logging as log
import pandas
import lciafmt.cache as cache
import lciafmt.df as df
import lciafmt.util as util

print([x for x in pyodbc.drivers() if x.startswith('Microsoft Access Driver')])

def get(endpoint=False, file=None, url=None) -> pandas.DataFrame:
    """ removed add_factors_for_missing_contexts=True from def get() confirm this is not necessary"""
    log.info("get method Impact World")
    f = file
    if f is None:
        fname = "Impact_World.accdb"
        if url is None:
            url = ("https://www.dropbox.com/sh/2sdgbqf08yn91bc/AABIGLlb_OwfNy6oMMDZNrm0a/IWplus_public_v1.3.accdb?dl=1")
        f = cache.get_or_download(fname, url)
    df = _read(f)
    
    if endpoint:
        df = df[df["Indicator unit"]=='DALY']
        df["Method"] = "Impact World - Endpoint"
    else:
        df = df[df["Indicator unit"]!='DALY']
        df["Method"] = "Impact World - Midpoint"
    
    return df

def _read(access_file: str) -> pandas.DataFrame:
    """Read the data from the Access database with the given path into a Pandas data frame."""

    log.info("read Impact World from file %s", access_file)

    path = cache.get_path(access_file)

    connStr = (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        r'DBQ=' + path + ";")

    cnxn = pyodbc.connect(connStr)
    crsr = cnxn.cursor()
    crsr.execute("SELECT * FROM [CF - not regionalized - All other impact categories]")
    rows = crsr.fetchall()

    records = []
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

    return df.data_frame(records)



