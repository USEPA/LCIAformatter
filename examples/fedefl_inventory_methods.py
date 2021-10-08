import lciafmt
import fedelemflowlist as fedefl
from lciafmt.util import store_method, save_json, log


method = lciafmt.Method.FEDEFL_INV


def main():

    log.debug('Subsets available: ' + ", ".join(map(str, fedefl.subset_list.get_subsets())))

    subsets = None

    inventory_methods = lciafmt.get_method(method_id='FEDEFL Inventory', subset=subsets)

    store_method(inventory_methods, method)
    save_json(method, inventory_methods)


if __name__ == "__main__":
    main()
