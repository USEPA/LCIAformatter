import pandas as pd

import fedelemflowlist as flowlist
import fedelemflowlist.subset_list as subsets

import lciafmt.df as df

def get(subset=None) -> pd.DataFrame:
    """
    Returns a dataframe of inventory based methods.
    :param subset: a list of dictionary keys from available inventories, if 
    none selected all availabile inventories will be generated
    :return: df in standard LCIAmethod format
    """
    method = df.data_frame(list())
    method['Characterization Factor'] = pd.to_numeric(method['Characterization Factor'])

    if subset == None:
        list_of_inventories = subsets.get_subsets()
    else:
        list_of_inventories = subset
    
    for inventory in list_of_inventories:
        flows = flowlist.get_flows(subset=inventory)
        flows.drop(['Formula','Synonyms','Class','External Reference',
                    'Preferred'], axis=1, inplace=True)
        flows['Indicator']=inventory
        flows['Indicator unit']=subsets.get_inventory_unit(inventory)
        flows['Characterization Factor']=1
        
        # Apply unit conversions where flow unit differs from indicator unit
        flows.loc[(flows['AltUnit']==flows['Indicator unit']),
                  'Characterization Factor'] = flows['AltUnitConversionFactor']
        flows.drop(['AltUnit','AltUnitConversionFactor'], axis=1, inplace=True)
        method = pd.concat([method,flows], ignore_index=True)

    method['Method']='Inventory'
    return method
