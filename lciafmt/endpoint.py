import pandas as pd

import lciafmt

def apply_endpoints(endpoints):
    """
    Returns a dataframe in LCIAmethod format that contains endpoint factors
    based on conversion factors supplied in passed param 'endpoints'
    param endpoints must conform to Endpoints specs
    """
    indicators = endpoints[['Method','Indicator']]
    
    method = pd.DataFrame()
    
    # TODO handle methods with multiple methods eg. recipe E/H/I
    
    for m in indicators['Method'].unique():
        method_indicators = indicators[indicators['Method']==m]
        indicator_list = list(method_indicators['Indicator'].unique())
        mapped_method = lciafmt.get_mapped_method(m, indicators=indicator_list)
        endpoint_method = mapped_method.merge(endpoints[['Indicator',
                                                  'Endpoint Indicator',
                                                  'Endpoint Indicator unit',
                                                  'Conversion factor']],
                                       how = 'left',
                                       on = ['Indicator'])
        endpoint_method['Indicator']=endpoint_method['Endpoint Indicator']
        endpoint_method['Indicator unit']=endpoint_method['Endpoint Indicator unit']
        endpoint_method['Characterization Factor']=endpoint_method['Characterization Factor']\
            *endpoint_method['Conversion factor']
        endpoint_method.drop(columns=['Endpoint Indicator',
                                      'Endpoint Indicator unit',
                                      'Conversion factor'],
                             inplace=True)
        method = method.append(endpoint_method, ignore_index = True)
    
    return method
