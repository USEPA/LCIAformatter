import os
import lciafmt
import fedelemflowlist as fedefl
from lciafmt.util import outputpath, store_method, log

method = lciafmt.Method.FEDEFL_INV

def main():

    os.makedirs(outputpath, exist_ok=True)
    file = method.get_filename()
    log.debug('Subsets available: ' + ", ".join(map(str, fedefl.subset_list.get_subsets())))
    subsets = None

    inventory_methods = lciafmt.get_method(method_id='FEDEFL Inventory',subset=subsets)
    
    store_method(inventory_methods, method)
    json_pack = outputpath+file+"_json.zip"
    if os.path.exists(json_pack):
        os.remove(json_pack)
    #lciafmt.to_jsonld(inventory_methods, json_pack)
    
if __name__ == "__main__":
    main()
