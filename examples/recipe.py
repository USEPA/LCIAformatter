import os
import lciafmt
from lciafmt.util import outputpath, store_method

method = lciafmt.Method.RECIPE_2016

#To obtain summary LCIA endpoint categories (damage assessment) set to True
apply_summary = False

def main():
    os.makedirs(outputpath, exist_ok=True)

    data = lciafmt.get_method(method, endpoint = False, 
                              summary = False)
    data_endpoint = lciafmt.get_method(method, endpoint = True, 
                              summary = apply_summary)
    data = data.append(data_endpoint, ignore_index = True)
    
    # make flowables case insensitive to handle lack of consistent structure in source file
    data['Flowable'] = data['Flowable'].str.lower()
    
    # map the flows to the Fed.LCA commons flows
    # set preserve_unmapped=True if you want to keep unmapped
    # flows in the resulting data frame
    mapping = method.get_metadata()['mapping']
    mapped_data = lciafmt.map_flows(data, system=mapping, case_insensitive=True)
    
    # write the result to parquet and JSON-LD
    store_method(mapped_data, method)

    for m in mapped_data['Method'].unique():
        mapped_data[mapped_data['Method']==m].to_csv(outputpath+m.replace('/','_')+".csv", index=False)
        json_pack = outputpath+m.replace('/','_')+"_json.zip"
        if os.path.exists(json_pack):
            os.remove(json_pack)
        data_for_json = mapped_data[mapped_data['Method']==m]
        lciafmt.to_jsonld(data_for_json, json_pack)


if __name__ == "__main__":
    main()
