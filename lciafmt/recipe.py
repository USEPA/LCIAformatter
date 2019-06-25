import logging as log

import pandas
import xlrd

import lciafmt.cache as cache
import lciafmt.df as df
import lciafmt.xls as xls


def get(file=None, url=None) -> pandas.DataFrame:
    log.info("get method ReCiPe 2016")
    f = file
    if f is None:
        fname = "recipe_2016.xlsx"
        if url is None:
            url = ("http://www.rivm.nl/sites/default/files/2018-11/" +
                   "ReCiPe2016_CFs_v1.1_20180117.xlsx")
        f = cache.get_or_download(fname, url)
    return _read(f)


def _read(file: str) -> pandas.DataFrame:
    log.info("read ReCiPe 2016 from file %s", file)
    wb = xlrd.open_workbook(file)
    records = []
    _read_gwp_sheet(wb.sheet_by_name("Global Warming"), records)
    return df.data_frame(records)


def _read_gwp_sheet(sheet: xlrd.book.sheet, records: list):
    for row in range(3, sheet.nrows):
        if xls.cell_empty(sheet, row, 3):
            continue

        for col in range(3, 6):
            val = xls.cell_f64(sheet, row, col)
            if val == 0.0:
                continue

            category = None
            if col == 3:
                category = "Global Warming - GWP20 - Individualist"
            elif col == 4:
                category = "Global Warming - GWP100 - Hierarchist"
            elif col == 5:
                category = "Global Warming - GWP1000 - Egalitarian"
            else:
                continue

            df.record(
                records,
                method="ReCiPe 2016",
                indicator=category,
                indicator_unit="kg CO2 eq.",
                flow=xls.cell_str(sheet, row, 0),
                flow_category="emissions/air",
                flow_unit="kg",
                factor=val
            )
