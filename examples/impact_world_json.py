import logging as log
import os

import lciafmt
from lciafmt.util import outputpath, store_method

method = lciafmt.Method.ImpactWorld

def main():
    os.makedirs(outputpath, exist_ok=True)
    log.basicConfig(level=log.INFO)

    file = method.get_filename()

    data = lciafmt.get_method(method, endpoint = False)
    data_endpoint = lciafmt.get_method(method, endpoint = True)
    data = data.append(data_endpoint, ignore_index = True)

    # map the flows to the Fed.LCA commons flows
    # set preserve_unmapped=True if you want to keep unmapped
    # flows in the resulting data frame
    mapping = method.get_metadata()['mapping']
    mapped_data = lciafmt.map_flows(data, system=mapping)

    # write the result to parquet and JSON-LD
    store_method(mapped_data, method)

    for m in mapped_data['Method'].unique():
        json_pack = outputpath + m + "_json.zip"
        if os.path.exists(json_pack):
            os.remove(json_pack)
        data_for_json = mapped_data[mapped_data['Method']==m]
        lciafmt.to_jsonld(data_for_json, json_pack)


if __name__ == "__main__":
    main()
