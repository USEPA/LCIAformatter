import logging as log

import pandas
import xlrd

import lciafmt.cache as cache
import lciafmt.df as df
import lciafmt.util as util
import lciafmt.xls as xls

contexts = {
        'urban air' : 'air/urban',
        'urban  air' : 'air/urban',
        'Urban air' : 'air/urban',
        'Rural air' : 'air/rural',
        'rural air' : 'air/rural',
        'agricultural soil' : 'soil/agricultural',
        'Agricultural soil' : 'soil/agricultural',
        'industrial soil' : 'soil/industrial',
        'Industrial soil' : 'soil/industrial',
        'freshwater' : 'water/freshwater',
        'Freshwater' : 'water/freshwater',
        'fresh water' : 'water/freshwater',
        'seawater' : 'water/sea water',
        'sea water' : 'water/sea water',
        'Sea water' : 'water/sea water',
        'marine water' : 'water/sea water'}

def get(add_factors_for_missing_contexts=True, file=None, url=None) -> pandas.DataFrame:
    log.info("get method ReCiPe 2016")
    f = file
    if f is None:
        fname = "recipe_2016.xlsx"
        if url is None:
            url = ("http://www.rivm.nl/sites/default/files/2018-11/" +
                   "ReCiPe2016_CFs_v1.1_20180117.xlsx")
        f = cache.get_or_download(fname, url)
    df = _read(f)
    if add_factors_for_missing_contexts:
        log.info("Adding average factors for primary contexts")
        df = util.aggregate_factors_for_primary_contexts(df)    
    return df


def _read(file: str) -> pandas.DataFrame:
    log.info("read ReCiPe 2016 from file %s", file)
    wb = xlrd.open_workbook(file)
    records = []
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
        if compartment_col > -1:
            compartment = xls.cell_str(sheet, row, compartment_col)
        if compartment in contexts:
            compartment = contexts[compartment]
        if unit_col > -1:
            flow_unit = xls.cell_str(sheet, row, unit_col)
            if "/" in flow_unit:
                flow_unit = flow_unit.split("/")[1].strip()
        cas = ""
        if cas_col > -1:
            util.format_cas(xls.cell_str(sheet, row, cas_col))

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
        if _containstr(s, "compartment") \
            or _containstr(s, "name", "in", "ecoinvent"):
            compartment_col = col
            break

    if compartment_col > -1:
        log.debug("found compartment column %i", compartment_col)
        return "", compartment_col

    elif _containstr(sheet.name, "global", "warming") \
            or _containstr(sheet.name, "ozone") \
            or _containstr(sheet.name, "particulate") \
            or _containstr(sheet.name, "acidification"):
        log.warning("no compartment column; assuming 'air'")
        return "air", -1
   
    elif _containstr(sheet.name, "mineral", "resource", "scarcity") \
            or _containstr(sheet.name, "fossil", "resource", "scarcity"):
        log.warning("no compartment column; assuming 'resource/ground'")
        return "resource/ground", -1
 
    if _containstr(sheet.name, "water", "consumption"):
        log.warning("no compartment column; assuming 'resource/fresh water'")
        return "resource/fresh water", -1

    log.warning("no compartment column")
    return "", -1


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
