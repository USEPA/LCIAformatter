import logging as log
import os

import lciafmt

mod = None

def main():
    modulepath = os.path.dirname(
        os.path.realpath(__file__)).replace('\\', '/')
    outputpath = modulepath + '/../output/'
    os.makedirs(outputpath, exist_ok=True)

    log.basicConfig(level=log.INFO)
    data = lciafmt.get_method(lciafmt.Method.TRACI)
    
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
    mapped_data = lciafmt.map_flows(data, system="TRACI2.1")

    # write the result to JSON-LD and CSV
    if mod is not None:
        outputpath=outputpath+mod+"_"
    mapped_data.to_csv(outputpath+"traci_2.1.csv", index=False)
    json_pack = outputpath+"traci_2.1_json.zip"
    if os.path.exists(json_pack):
        os.remove(json_pack)
    lciafmt.to_jsonld(mapped_data, json_pack)



if __name__ == "__main__":
    main()
