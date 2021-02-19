import pandas as pd
import logging as log

import lciafmt

def apply_endpoints(endpoints, matching_fields = ['Indicator']):
    """
    Returns a dataframe in LCIAmethod format that contains endpoint factors
        based on conversion factors supplied in passed param 'endpoints'
    param endpoints must conform to Endpoints specs
    param matching_fields: list of fields on which to apply unique endpoint
        conversions
    """
    indicators = endpoints[['Method'] + matching_fields]
    
    method = pd.DataFrame()
    
    # TODO handle methods with multiple methods eg. recipe E/H/I
    
    for e in matching_fields:
        endpoints[e].fillna("", inplace=True)
    
    for m in indicators['Method'].unique():
        method_indicators = indicators[indicators['Method']==m]
        indicator_list = list(method_indicators['Indicator'].unique())
        mapped_method = lciafmt.get_mapped_method(m, indicators=indicator_list)
        endpoint_method = mapped_method.merge(endpoints[matching_fields +
                                                  ['Endpoint Indicator',
                                                  'Endpoint Indicator unit',
                                                  'Conversion factor']],
                                       how = 'left',
                                       on = matching_fields)
        endpoint_method['Indicator']=endpoint_method['Endpoint Indicator']
        endpoint_method['Indicator unit']=endpoint_method['Endpoint Indicator unit']
        endpoint_method['Characterization Factor']=endpoint_method['Characterization Factor']\
            *endpoint_method['Conversion factor']
        endpoint_method.drop(columns=['Endpoint Indicator',
                                      'Endpoint Indicator unit',
                                      'Conversion factor'],
                             inplace=True)
        endpoint_method.dropna(subset=['Characterization Factor'], inplace=True)
        if (len(endpoint_method.index) != len(mapped_method.index)):
            log.warn("some characterization factors lost")
        method = method.append(endpoint_method, ignore_index = True)
    
    method.dropna(subset=['Characterization Factor'], inplace=True)
    return method
