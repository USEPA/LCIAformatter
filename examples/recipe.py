import logging as log
import os

import lciafmt

def main():
    modulepath = os.path.dirname(
        os.path.realpath(__file__)).replace('\\', '/')
    outputpath = modulepath + '/../output/'
    os.makedirs(outputpath, exist_ok=True)

    log.basicConfig(level=log.INFO)
    data = lciafmt.get_method(lciafmt.Method.RECIPE_2016)

    # map the flows to the Fed.LCA commons flows
    # set preserve_unmapped=True if you want to keep unmapped
    # flows in the resulting data frame
    mapped_data = lciafmt.map_flows(data, system="ReCiPe2016")

    # write the result to JSON-LD and CSV
    for method in mapped_data['Method'].unique():
        mapped_data[mapped_data['Method']==method].to_csv(outputpath+method.replace('/','_')+".csv", index=False)
    json_pack = outputpath+"recipe_2016_json.zip"
    if os.path.exists(json_pack):
        os.remove(json_pack)
    lciafmt.to_jsonld(mapped_data, json_pack)


if __name__ == "__main__":
    main()
