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
    _read_odp_sheet(wb.sheet_by_name("Stratospheric ozone depletion"), records)
    _read_irp_sheet(wb.sheet_by_name("Ionizing radiation"), records)

    for name in wb.sheet_names():
        if _eqstr(name, "Version") or _eqstr(
                name, "Midpoint to endpoint factors"):
            continue
        _read_mid_points(name, wb.sheet_by_name(name), records)

    return df.data_frame(records)


def _read_mid_points(name: str, sheet: xlrd.book.sheet, records: list):
    log.info("try to read midpoint factors from sheet %s", name)

    # find the start position from where we will read the data
    start_row, data_col, with_perspectives = _find_data_start(sheet)
    if start_row < 0:
        log.warning("could not find a value column in sheet %s", name)
        return

    flow_col = _find_flow_column(sheet)
    if flow_col < 0:
        return
    cas_col = _find_cas_column(sheet)


def _find_data_start(sheet: xlrd.book.sheet) -> (int, int, bool):
    for row, col in xls.iter_cells(sheet):
        s = xls.cell_str(sheet, row, col)
        if s is None or s == "":
            continue
        if _eqstr(s, "I") or _containstr(s, "Individualist"):
            return row + 1, col, True
        if _eqstr(s, "all perspectives"):
            return row + 1, col, False
    return -1, -1


def _find_flow_column(sheet: xlrd.book.sheet) -> int:
    ncol = -1
    for row, col in xls.iter_cells(sheet):
        s = xls.cell_str(sheet, row, col)
        if _containstr(s, "name") or _containstr(s, "substance"):
            ncol = col
            log.debug("identified column %i %s for flow names", ncol, s)
            break
    if ncol < 0:
        log.warning("no 'name' column in %s, take col=0 for that", sheet.name)
        ncol = 0
    return ncol


def _find_cas_column(sheet: xlrd.book.sheet) -> int:
    ccol = -1
    for row, col in xls.iter_cells(sheet):
        s = xls.cell_str(sheet, row, col)
        if _eqstr(s, "cas"):
            ccol = col
            log.debug("identified column %i %s for CAS numbers", ccol, s)
            break
    return ccol


def _read_gwp_sheet(sheet: xlrd.book.sheet, records: list):
    for row in range(3, sheet.nrows):
        if xls.cell_empty(sheet, row, 3):
            continue

        for col in range(3, 6):
            val = xls.cell_f64(sheet, row, col)
            if val == 0.0:
                continue

            category = "Global warming - "
            if col == 3:
                category += "GWP20 - I"
                factor_hh = 0.0000000812
                factor_te = 0.000000000532
                factor_fe = 0.0000000000000145
            elif col == 4:
                category += "GWP100 - H"
                factor_hh = 0.000000928
                factor_te = 0.0000000028
                factor_fe = 0.0000000000000765
            elif col == 5:
                category += "GWP1000 - E"
                factor_hh = 0.0000125
                factor_te = 0.000000025
                factor_fe = 0.000000000000682
            else:
                continue

            df.record(
                records,
                method="ReCiPe 2016 - Midpoint",
                indicator=category,
                indicator_unit="kg CO2 eq.",
                flow=xls.cell_str(sheet, row, 0),
                flow_category="emissions/air",
                flow_unit="kg",
                factor=val
            )

            df.record(
                records,
                method="ReCiPe 2016 - Endpoint",
                indicator=category + " - Human health",
                indicator_unit="DALY",
                flow=xls.cell_str(sheet, row, 0),
                flow_category="emissions/air",
                flow_unit="kg",
                factor=val * factor_hh
            )

            df.record(
                records,
                method="ReCiPe 2016 - Endpoint",
                indicator=category + " - Terrestrial ecosystems",
                indicator_unit="species*year",
                flow=xls.cell_str(sheet, row, 0),
                flow_category="emissions/air",
                flow_unit="kg",
                factor=val * factor_te
            )

            df.record(
                records,
                method="ReCiPe 2016 - Endpoint",
                indicator=category + " - Freshwater ecosystems",
                indicator_unit="species*year",
                flow=xls.cell_str(sheet, row, 0),
                flow_category="emissions/air",
                flow_unit="kg",
                factor=val * factor_fe
            )


def _read_odp_sheet(sheet: xlrd.book.sheet, records: list):
    for row in range(4, sheet.nrows):
        if xls.cell_empty(sheet, row, 2):
            continue

        for col in range(2, 5):
            val = xls.cell_f64(sheet, row, col)
            if val == 0.0:
                continue

            category = "Stratospheric ozone depletion - "
            if col == 2:
                category += "ODP20 - I"
                factor_hh = 0.000237
            elif col == 3:
                category += "ODP200 - H"
                factor_hh = 0.000531
            elif col == 4:
                category += "ODPinfinite - E"
                factor_hh = 0.00134
            else:
                continue

            df.record(
                records,
                method="ReCiPe 2016 - Midpoint",
                indicator=category,
                indicator_unit="kg CFC11 eq.",
                flow=xls.cell_str(sheet, row, 0),
                flow_category="emissions/air",
                flow_unit="kg",
                factor=val
            )

            df.record(
                records,
                method="ReCiPe 2016 - Endpoint",
                indicator=category + " - Human health",
                indicator_unit="DALY",
                flow=xls.cell_str(sheet, row, 0),
                flow_category="emissions/air",
                flow_unit="kg",
                factor=val * factor_hh
            )


def _read_irp_sheet(sheet: xlrd.book.sheet, records: list):
    for row in range(3, sheet.nrows):
        if xls.cell_empty(sheet, row, 3):
            continue

        for col in range(4, 7):
            val = xls.cell_f64(sheet, row, col)
            if val == 0.0:
                continue

            category = "Ionizing radiation - "
            if col == 4:
                category += "I"
                factor_hh = 0.0000000068
            elif col == 5:
                category += "H"
                factor_hh = 0.0000000085
            elif col == 6:
                category += "E"
                factor_hh = 0.000000014
            else:
                continue

            df.record(
                records,
                method="ReCiPe 2016 - Midpoint",
                indicator=category,
                indicator_unit="kBq Co-60 to air eq.",
                flow=xls.cell_str(sheet, row, 0),
                flow_category="emissions/" + xls.cell_str(sheet, row, 3),
                flow_unit="kBq",
                factor=val
            )

            df.record(
                records,
                method="ReCiPe 2016 - Endpoint",
                indicator=category + " - Human health",
                indicator_unit="DALY",
                flow=xls.cell_str(sheet, row, 0),
                flow_category="emissions/" + xls.cell_str(sheet, row, 3),
                flow_unit="kBq",
                factor=val * factor_hh
            )


def _eqstr(s1: str, s2: str) -> bool:
    if s1 is None or s2 is None:
        return False
    return s1.strip().lower() == s2.strip().lower()


def _containstr(s: str, *words) -> bool:
    if s is None:
        return False
    base = s.lower()
    for w in words:
        if not isinstance(w, str):
            return False
        if w.lower().strip() not in base:
            return False
    return True
