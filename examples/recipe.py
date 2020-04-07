import logging as log
import os

import lciafmt

#To obtain LCIA endpoint set to True
apply_endpoint = True

#To obtain summary LCIA endpoint categories (damage assessment) set to True
apply_summary = False

def main():
    modulepath = os.path.dirname(
        os.path.realpath(__file__)).replace('\\', '/')
    outputpath = modulepath + '/../output/'
    os.makedirs(outputpath, exist_ok=True)

    log.basicConfig(level=log.INFO)
    data = lciafmt.get_method(lciafmt.Method.RECIPE_2016, endpoint = apply_endpoint, summary = apply_summary)
    
    #export lcia to csv before mapping
    data.to_csv(outputpath+'Recipe_source.csv', index=False)
    
    # make flowables case insensitive to handle lack of consistent structure in source file
    data['Flowable'] = data['Flowable'].str.lower()
    
    # map the flows to the Fed.LCA commons flows
    # set preserve_unmapped=True if you want to keep unmapped
    # flows in the resulting data frame
    mapped_data = lciafmt.map_flows(data, system="ReCiPe2016", case_insensitive=True)

    # write the result to JSON-LD and CSV
    for method in mapped_data['Method'].unique():
        mapped_data[mapped_data['Method']==method].to_csv(outputpath+method.replace('/','_')+".csv", index=False)
        json_pack = outputpath+method.replace('/','_')+"_json.zip"
        if os.path.exists(json_pack):
            os.remove(json_pack)
        data_for_json = mapped_data[mapped_data['Method']==method]
        lciafmt.to_jsonld(data_for_json, json_pack)


if __name__ == "__main__":
    main()
