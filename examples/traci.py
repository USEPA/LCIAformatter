import logging as log
import os

import lciafmt
import pandas as pd

def main():
    modulepath = os.path.dirname(
        os.path.realpath(__file__)).replace('\\', '/')
    outputpath = modulepath + '/../output/'
    os.makedirs(outputpath, exist_ok=True)

    log.basicConfig(level=log.INFO)
    data = lciafmt.get_method(lciafmt.Method.TRACI)
    
    """ due to substances listed more than once with different names
    this replaces all instances of the Original Flowable with a New Flowable
    based on a csv input file, otherwise zero values for CFs will override
    when there are duplicate names"""
    flowables_replace = pd.read_csv(modulepath+'/TRACI_2.1_replacement.csv')
    for index, row in flowables_replace.iterrows():
        orig = row['Original Flowable']
        new = row['New Flowable']
        data['Flowable']=data['Flowable'].replace(orig, new) 
        
    """ due to substances listed more than once with the same name but different CAS
    this replaces all instances of the Original Flowable with a New Flowable
    based on a csv input file according to the CAS"""
    flowables_split = pd.read_csv(modulepath+'/TRACI_2.1_split.csv')
    for index, row in flowables_split.iterrows():
        CAS = row['CAS']
        new = row['New Flowable']
        data.loc[data['CAS No'] == CAS, 'Flowable'] = new
    
    # map the flows to the Fed.LCA commons flows
    # set preserve_unmapped=True if you want to keep unmapped
    # flows in the resulting data frame
    mapped_data = lciafmt.map_flows(data, system="TRACI2.1")

    # write the result to JSON-LD and CSV
    mapped_data.to_csv(outputpath+"traci_2.1.csv", index=False)
    json_pack = outputpath+"traci_2.1_json.zip"
    if os.path.exists(json_pack):
        os.remove(json_pack)
    lciafmt.to_jsonld(mapped_data, json_pack)


if __name__ == "__main__":
    main()
