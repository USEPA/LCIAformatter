import logging as log
import os
import tempfile

import pandas
import requests
import xlrd

import lciafmt.df as df


def get_traci(file=None) -> pandas.DataFrame:
    log.info("get method Traci 2.1")
    if file is None:
        cache_path = os.path.join(cache_dir(), "traci_2.1.xlsx")
        if os.path.isfile(cache_path):
            log.info("take file from cache: %s", cache_path)
            file = cache_path
        else:
            url = ("https://www.epa.gov/sites/production/files/2015-12/" +
                   "traci_2_1_2014_dec_10_0.xlsx")
            log.info("download method from %s", url)
            cache_dir(create=True)
            resp = requests.get(url, allow_redirects=True)
            with open(cache_path, "wb") as f:
                f.write(resp.content)
            file = cache_path

    log.info("read file %s", file)
    wb = xlrd.open_workbook(file)
    sheet = wb.sheet_by_name("Substances")

    categories = {}
    for col in range(3, sheet.ncols):
        name = _cell_str(sheet, 0, col)
        if name == "":
            break
        categories[col] = name

    records = []
    for row in range(1, sheet.nrows):
        flow = _cell_str(sheet, row, 2)
        if flow == "":
            break
        cas = _cell_str(sheet, row, 1)
        if cas == "x":
            cas = ""

        for col in range(3, sheet.ncols):
            category = categories.get(col)
            if category is None:
                break
            factor = _cell_f64(sheet, row, col)
            if factor == 0.0:
                continue
            df.record(
                records,
                method="traci 2.1",
                indicator=category,
                flow=flow,
                cas_number=cas,
                factor=factor)

    return df.data_frame(records)

def _cell_str(sheet, row, col) -> str:
    cell = sheet.cell(row, col)
    if cell is None:
        return ""
    if cell.value is None:
        return ""
    return str(cell.value).strip()


def _cell_f64(sheet, row, col) -> float:
    cell = sheet.cell(row, col)
    if cell is None:
        return 0.0
    if cell.value is None:
        return 0.0
    try:
        return float(cell.value)
    except ValueError:
        return 0.0


def cache_dir(create=False) -> str:
    """Returns the path to the folder where cached files are stored. """
    tdir = tempfile.gettempdir()
    cdir = os.path.join(tdir, "lciafmt")
    if create:
        os.makedirs(cdir, exist_ok=True)
    return cdir
