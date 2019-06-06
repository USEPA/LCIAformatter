import logging as log

import pandas
import xlrd

import lciafmt.df as df
import lciafmt.xls as xls


def read(xls_file: str) -> pandas.DataFrame:
    """Read the data from the Excel file with the given path into a Pandas
       data frame."""

    log.info("read Traci 2.1 from file %s", xls_file)
    wb = xlrd.open_workbook(xls_file)
    sheet = wb.sheet_by_name("Substances")

    categories = {}
    for col in range(3, sheet.ncols):
        name = xls.cell_str(sheet, 0, col)
        if name == "":
            break
        cat_info = _category_info(name)
        if cat_info is not None:
            categories[col] = cat_info

    records = []
    for row in range(1, sheet.nrows):
        flow = xls.cell_str(sheet, row, 2)
        if flow == "":
            break

        # in traci, CAS numbers are saved as
        # formatted numbers
        cas = xls.cell_val(sheet, row, 1)
        if cas == "x" or cas is None:
            cas = ""
        if isinstance(cas, (int, float)):
            cas = str(int(cas))
            if len(cas) > 4:
                cas = cas[:-3] + "-" + cas[-3:-1] + "-" + cas[-1]

        for col in range(3, sheet.ncols):
            cat_info = categories.get(col)
            if cat_info is None:
                continue
            factor = xls.cell_f64(sheet, row, col)
            if factor == 0.0:
                continue
            df.record(
                records,
                method="Traci 2.1",
                indicator=cat_info[0],
                indicator_unit=cat_info[1],
                flow=flow,
                flow_category=cat_info[2],
                flow_unit=cat_info[3],
                cas_number=cas,
                factor=factor)

    return df.data_frame(records)


def _category_info(c: str):
    """"Get the meta data which are encoded in the category name. It returns
        a tuple (indicator, indicator unit, flow category, flow unit) for the
        given category name. If it is an unknown category, `None` is returned.
    """

    if c == "Global Warming Air (kg CO2 eq / kg substance)":
        return "Global warming", "kg CO2 eq", "air", "kg"

    if c == "Acidification Air (kg SO2 eq / kg substance)":
        return "Acidification", "kg SO2 eq", "air", "kg"

    if c == "HH Particulate Air (PM2.5 eq / kg substance)":
        return ("Human health - particulate matter", "PM 2.5 eq",
                "air", "kg")

    if c == "Eutrophication Air (kg N eq / kg substance)":
        return "Eutrophication", "kg N eq", "air", "kg"

    if c == "Eutrophication Water (kg N eq / kg substance)":
        return "Eutrophication", "kg N eq", "water", "kg"

    if c == "Ozone Depletion Air (kg CFC-11 eq / kg substance)":
        return "Ozone depletion", "kg CFC-11 eq", "air", "kg"

    if c == "Smog Air (kg O3 eq / kg substance)":
        return "Smog formation", "kg O3 eq", "air", "kg"

    if c == "Ecotox. CF [CTUeco/kg], Em.airU, freshwater":
        return "Freshwater ecotoxicity", "CTUeco", "air/urban", "kg"

    if c == "Ecotox. CF [CTUeco/kg], Em.airC, freshwater":
        return "Freshwater ecotoxicity", "CTUeco", "air/rural", "kg"

    if c == "Ecotox. CF [CTUeco/kg], Em.fr.waterC, freshwater":
        return "Freshwater ecotoxicity", "CTUeco", "water/freshwater", "kg"

    if c == "Ecotox. CF [CTUeco/kg], Em.sea waterC, freshwater":
        return "Freshwater ecotoxicity", "CTUeco", "water/sea water", "kg"

    if c == "Ecotox. CF [CTUeco/kg], Em.nat.soilC, freshwater":
        return "Freshwater ecotoxicity", "CTUeco", "soil/natural", "kg"

    if c == "Ecotox. CF [CTUeco/kg], Em.agr.soilC, freshwater":
        return "Freshwater ecotoxicity", "CTUeco", "soil/agricultural", "kg"

    if c == "Human health CF  [CTUcancer/kg], Emission to urban air, cancer":
        return "Human health - cancer", "CTUcancer", "air/urban", "kg"

    if c == "Human health CF  [CTUnoncancer/kg], Emission to urban air, non-canc.":
        return "Human health - non-cancer", "CTUnoncancer", "air/urban", "kg"

    if c == "Human health CF  [CTUcancer/kg], Emission to cont. rural air, cancer":
        return "Human health - cancer", "CTUcancer", "air/rural", "kg"

    if c == "Human health CF  [CTUnoncancer/kg], Emission to cont. rural air, non-canc.":
        return "Human health - non-cancer", "CTUnoncancer", "air/rural", "kg"

    if c == "Human health CF  [CTUcancer/kg], Emission to cont. freshwater, cancer":
        return "Human health - cancer", "CTUcancer", "water/freshwater", "kg"

    if c == "Human health CF  [CTUnoncancer/kg], Emission to cont. freshwater, non-canc.":
        return "Human health - non-cancer", "CTUnoncancer", "water/freshwater", "kg"

    if c == "Human health CF  [CTUcancer/kg], Emission to cont. sea water, cancer":
        return "Human health - cancer", "CTUcancer", "water/sea water", "kg"

    if c == "Human health CF  [CTUnoncancer/kg], Emission to cont. sea water, non-canc.":
        return "Human health - non-cancer", "CTUnoncancer", "water/sea water", "kg"

    if c == "Human health CF  [CTUcancer/kg], Emission to cont. natural soil, cancer":
        return "Human health - cancer", "CTUcancer", "soil/natural", "kg"

    if c == "Human health CF  [CTUnoncancer/kg], Emission to cont. natural soil, non-canc.":
        return "Human health - non-cancer", "CTUnoncancer", "soil/natural", "kg"

    if c == "Human health CF  [CTUcancer/kg], Emission to cont. agric. Soil, cancer":
        return "Human health - cancer", "CTUcancer", "soil/agricultural", "kg"

    if c == "Human health CF  [CTUnoncancer/kg], Emission to cont. agric. Soil, non-canc.":
        return "Human health - non-cancer", "CTUnoncancer", "soil/agricultural", "kg"
