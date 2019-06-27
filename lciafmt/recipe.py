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
    # _read_gwp_sheet(wb.sheet_by_name("Global Warming"), records)
    # _read_odp_sheet(wb.sheet_by_name("Stratospheric ozone depletion"), records)
    # _read_irp_sheet(wb.sheet_by_name("Ionizing radiation"), records)

    for name in wb.sheet_names():
        if _eqstr(name, "Version") or _eqstr(
                name, "Midpoint to endpoint factors"):
            continue
        _read_mid_points(wb.sheet_by_name(name), records)

    return df.data_frame(records)


def _read_mid_points(sheet: xlrd.book.sheet, records: list):
    log.info("try to read midpoint factors from sheet %s", sheet.name)

    start_row, data_col, with_perspectives = _find_data_start(sheet)
    if start_row < 0:
        log.warning("could not find a value column in sheet %s", sheet.name)
        return

    flow_col = _find_flow_column(sheet)
    if flow_col < 0:
        return

    cas_col = _find_cas_column(sheet)
    indicator_unit, flow_unit, unit_col = _determine_units(sheet)
    compartment, compartment_col = _determine_compartments(sheet)

    perspectives = ["I", "H", "E"]
    factor_count = 0
    for row in range(start_row, sheet.nrows):
        if xls.cell_f64(sheet, row, data_col) == 0.0:
            continue

        if compartment_col > -1:
            compartment = xls.cell_str(sheet, row, compartment_col)
        if unit_col > -1:
            flow_unit = xls.cell_str(sheet, row, unit_col)
            if "/" in flow_unit:
                flow_unit = flow_unit.split("/")[1].strip()
        cas = ""
        if cas_col > -1:
            cas = xls.cell_str(sheet, row, cas_col)

        if with_perspectives:
            for i in range(0, 3):
                val = xls.cell_f64(sheet, row, data_col + i)
                if val == 0.0:
                    continue
                df.record(records,
                          method="ReCiPe 2016 - Midpoint/" + perspectives[i],
                          indicator=sheet.name,
                          indicator_unit=indicator_unit,
                          flow=xls.cell_str(sheet, row, flow_col),
                          flow_category=compartment,
                          flow_unit=flow_unit,
                          cas_number=cas,
                          factor=val)
                factor_count += 1
        else:
            val = xls.cell_f64(sheet, row, data_col)
            if val == 0.0:
                continue
            for p in perspectives:
                df.record(records,
                          method="ReCiPe 2016 - Midpoint/" + p,
                          indicator=sheet.name,
                          indicator_unit=indicator_unit,
                          flow=xls.cell_str(sheet, row, flow_col),
                          flow_category=compartment,
                          flow_unit=flow_unit,
                          cas_number=cas,
                          factor=val)
                factor_count += 1
    log.debug("extracted %i factors", factor_count)


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


def _determine_units(sheet: xlrd.book.sheet) -> (str, str, int):
    indicator_unit = "?"
    flow_unit = "?"
    unit_col = -1
    row, col, _ = _find_data_start(sheet)
    row -= 2

    if row > 0:
        s = xls.cell_str(sheet, row, col)
        if s is not None and s != "":
            if "/" in s:
                parts = s.strip(" ()").split("/")
                indicator_unit = parts[0].strip()
                flow_unit = parts[1].strip()
            else:
                indicator_unit = s.strip()

    for row, col in xls.iter_cells(sheet):
        if row > 5:
            break
        s = xls.cell_str(sheet, row, col)
        if _eqstr(s, "Unit"):
            unit_col = col
            break

    if indicator_unit != "?":
        log.debug("determined indicator unit: %s", indicator_unit)
    elif _containstr(sheet.name, "land", "transformation"):
        log.warning("unknown indicator unit; assuming it is m2")
        indicator_unit = "m2"
    elif _containstr(sheet.name, "land", "occupation"):
        log.warning("unknown indicator unit; assuming it is m2*a")
        indicator_unit = "m2*a"
    elif _containstr(sheet.name, "water", "consumption"):
        log.warning("unknown indicator unit; assuming it is m3")
        indicator_unit = "m3"
    else:
        log.warning("unknown indicator unit")

    if _containstr(flow_unit, "kg"):
        flow_unit = "kg"

    if unit_col > -1:
        log.debug("take units from column %i", unit_col)
    elif flow_unit != "?":
        log.debug("determined flow unit: %s", flow_unit)
    elif _containstr(sheet.name, "land", "transformation"):
        log.warning("unknown flow unit; assume it is m2")
        flow_unit = "m2"
    elif _containstr(sheet.name, "land", "occupation"):
        log.warning("unknown flow unit; assuming it is m2*a")
        flow_unit = "m2*a"
    elif _containstr(sheet.name, "water", "consumption"):
        log.warning("unknown flow unit; assuming it is m3")
        flow_unit = "m3"
    else:
        log.warning("unknown flow unit; assuming it is 'kg'")
        flow_unit = "kg"

    return indicator_unit, flow_unit, unit_col


def _determine_compartments(sheet: xlrd.book.sheet) -> (str, int):
    compartment_col = -1
    for row, col in xls.iter_cells(sheet):
        if row > 5:
            break
        s = xls.cell_str(sheet, row, col)
        if _containstr(s, "compartment"):
            compartment_col = col
            break

    if compartment_col > -1:
        log.debug("found compartment column %i", compartment_col)
        return "", compartment_col

    if _containstr(sheet.name, "global", "warming") \
            or _containstr(sheet.name, "ozone") \
            or _containstr(sheet.name, "particulate") \
            or _containstr(sheet.name, "acidification"):
        log.warning("no compartment column; assuming 'emission/air'")
        return "emission/air", -1

    log.warning("no compartment column")
    return "", -1


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
