import pandas


def data_frame(records):
    cols = ["Method",
            "Method UUID",
            "Indicator",
            "Indicator UUID",
            "Indicator unit",
            "Flow",
            "Flow UUID",
            "Flow category",
            "Flow unit",
            "CAS",
            "Location",
            "Location UUID",
            "Factor"]
    return pandas.DataFrame(records, columns=cols)


def record(records: list,
           method="",
           method_uuid="",
           indicator="",
           indicator_uuid="",
           indicator_unit="",
           flow="",
           flow_uuid="",
           flow_category="",
           flow_unit="",
           cas_number="",
           location="",
           location_uuid="",
           factor=0.0) -> list:
    """Append a new row to the given list (which may be the empty list)."""
    records.append([
        method,
        method_uuid,
        indicator,
        indicator_uuid,
        indicator_unit,
        flow,
        flow_uuid,
        flow_category,
        flow_unit,
        cas_number,
        location,
        location_uuid,
        factor])
    return records
