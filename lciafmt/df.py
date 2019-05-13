import pandas


def data_frame(records):
    cols = ["Method",
            "Indicator",
            "Indicator unit",
            "Flow",
            "Flow category",
            "Flow unit",
            "CAS",
            "Flow UUID",
            "Factor"]
    return pandas.DataFrame(records, columns=cols)


def record(records: list,
           method="",
           indicator="",
           indicator_unit="",
           flow="",
           flow_category="",
           flow_unit="",
           cas_number="",
           flow_uuid="",
           factor=0.0) -> list:
    """Append a new row to the given list (which may be the empty list)."""
    records.append([
        method,
        indicator,
        indicator_unit,
        flow,
        flow_category,
        flow_unit,
        cas_number,
        flow_uuid,
        factor])
    return records
