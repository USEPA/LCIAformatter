def category_info(c: str):
    """"Get the meta data which are encoded in the category name as
        https://nepis.epa.gov/Adobe/PDF/P100HN53.pdf
    """

    if c == "Global Warming Air (kg CO2 eq / kg substance)":
        return "Global Warming", "kg CO2 eq", "air", "unspecified", "kg"

    if c == "Acidification Air (kg SO2 eq / kg substance)":
        return "Acidification", "kg SO2 eq", "air", "unspecified", "kg"

    if c == "HH Particulate Air (PM2.5 eq / kg substance)":
        return "HH Particulate", "PM2.5 eq", "air", "unspecified", "kg"

    if c == "Eutrophication Air (kg N eq / kg substance)":
        return "Eutrophication", "kg N eq", "air", "unspecified", "kg"

    if c == "Eutrophication Water (kg N eq / kg substance)":
        return "Eutrophication", "kg N eq", "water", "unspecified", "kg"

    if c == "Ozone Depletion Air (kg CFC-11 eq / kg substance)":
        return "Ozone Depletion", "kg CFC-11 eq", "air", "unspecified", "kg"

    if c == "Smog Air (kg O3 eq / kg substance)":
        return "Smog", "kg O3 eq", "air", "unspecified", "kg"

    if c == "Ecotox. CF [CTUeco/kg], Em.airU, freshwater":
        return ("Freshwater Ecotoxicity", "CTUeco", "air",
                "urban", "kg")

    if c == "Ecotox. CF [CTUeco/kg], Em.airC, freshwater":
        return ("Freshwater Ecotoxicity", "CTUeco", "air",
                "rural", "kg")

    if c == "Ecotox. CF [CTUeco/kg], Em.fr.waterC, freshwater":
        return ("Freshwater Ecotoxicity", "CTUeco", "water",
                "freshwater", "kg")

    if c == "Ecotox. CF [CTUeco/kg], Em.sea waterC, freshwater":
        return ("Freshwater Ecotoxicity", "CTUeco", "water",
                "seawater", "kg")

    if c == "Ecotox. CF [CTUeco/kg], Em.nat.soilC, freshwater":
        return ("Freshwater Ecotoxicity", "CTUeco", "soil",
                "natural", "kg")

    if c == "Ecotox. CF [CTUeco/kg], Em.agr.soilC, freshwater":
        return ("Freshwater Ecotoxicity", "CTUeco", "soil",
                "agricultural ", "kg")

    if c == "Human health CF  [CTUcancer/kg], Emission to urban air, cancer":
        return ("Human health, cancer", "CTUcancer", "air", "urban ", "kg")

    if c == "Human health CF  [CTUnoncancer/kg], Emission to urban air, non-canc.":
        return ("Human health, non-canc.", "CTUnoncancer", "air",
                "urban ", "kg")

    if c == "Human health CF  [CTUcancer/kg], Emission to cont. rural air, cancer":
    if c == "Human health CF  [CTUnoncancer/kg], Emission to cont. rural air, non-canc.":
    if c == "Human health CF  [CTUcancer/kg], Emission to cont. freshwater, cancer":
    if c == "Human health CF  [CTUnoncancer/kg], Emission to cont. freshwater, non-canc.":
    if c == "Human health CF  [CTUcancer/kg], Emission to cont. sea water, cancer":
    if c == "Human health CF  [CTUnoncancer/kg], Emission to cont. sea water, non-canc.":
    if c == "Human health CF  [CTUcancer/kg], Emission to cont. natural soil, cancer":
    if c == "Human health CF  [CTUnoncancer/kg], Emission to cont. natural soil, non-canc.":
    if c == "Human health CF  [CTUcancer/kg], Emission to cont. agric. Soil, cancer":
    if c == "Human health CF  [CTUnoncancer/kg], Emission to cont. agric. Soil, non-canc.":
    if c == "CF Flag HH carcinogenic":
    if c == "CF Flag HH non-carcinogenic":
