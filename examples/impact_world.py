import lciafmt
from lciafmt.util import store_method, collapse_indicators, save_json

method = lciafmt.Method.ImpactWorld


def main():

    data = lciafmt.get_method(method)

    # map the flows to the Fed.LCA commons flows
    # set preserve_unmapped=True if you want to keep unmapped
    # flows in the resulting data frame
    mapping = method.get_metadata()['mapping']
    mapped_data = lciafmt.map_flows(data, system=mapping)

    mapped_data = collapse_indicators(mapped_data)

    # write the result to parquet and JSON-LD
    store_method(mapped_data, method)
    for m in mapped_data['Method'].unique():
        save_json(method, mapped_data, m)


if __name__ == "__main__":
    main()
