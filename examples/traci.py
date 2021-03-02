import os

import lciafmt
from lciafmt.util import outputpath, store_method, log

mod = None

method = lciafmt.Method.TRACI

def main():
    os.makedirs(outputpath, exist_ok=True)
    file = method.get_filename()

    data = lciafmt.get_method(method)
    
    if mod is not None:
        log.info("getting modified CFs")
        modified_cfs=lciafmt.get_modification(mod,"TRACI2.1")
        data = data.merge(modified_cfs,how='left',on=['Flowable','Context','Indicator'])
        data.loc[data['Updated CF'].notnull(),'Characterization Factor']=data['Updated CF']
        data = data.drop(columns=['Updated CF','Note'])
        data['Method']="TRACI 2.1 ("+mod+" mod)"
    
    # map the flows to the Fed.LCA commons flows
    # set preserve_unmapped=True if you want to keep unmapped
    # flows in the resulting data frame
    mapping = method.get_metadata()['mapping']
    mapped_data = lciafmt.map_flows(data, system=mapping)

    # write the result to parquet and JSON-LD
    store_method(mapped_data, method)
    if mod is not None:
        file=mod+"_"+file
    json_pack = outputpath+file+"_json.zip"
    if os.path.exists(json_pack):
        os.remove(json_pack)
    lciafmt.to_jsonld(mapped_data, json_pack)


if __name__ == "__main__":
    main()
