import logging as log
import os
import lciafmt
import lciafmt.fedefl_inventory as methods
import fedelemflowlist as fedefl

def main():

    modulepath = os.path.dirname(
        os.path.realpath(__file__)).replace('\\', '/')
    outputpath = modulepath + '/../output/'
    os.makedirs(outputpath, exist_ok=True)
    
    print(list(fedefl.subset_list.subsets))
    subsets = None
    
    log.basicConfig(level=log.INFO)
    inventory_methods = methods.get_inventory_methods(subsets)
    json_pack = outputpath+"inventory_method_json.zip"
    if os.path.exists(json_pack):
        os.remove(json_pack)
    lciafmt.to_jsonld(inventory_methods, json_pack)
    
if __name__ == "__main__":
    main()
