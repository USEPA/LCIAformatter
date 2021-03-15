import logging as log

import lciafmt
from lciafmt.util import store_method, save_json

mod = None

method = lciafmt.Method.TRACI

def main():
    log.basicConfig(level=log.INFO)

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
    save_json(method, mapped_data)

if __name__ == "__main__":
    main()
