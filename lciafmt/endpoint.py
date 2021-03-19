# endpoint.py (lciafmt)
# !/usr/bin/env python3
# coding=utf-8
"""
Functions to generate user specified endpoint functions from one or more
LCIA methods
"""

import pandas as pd

import lciafmt
from .util import log

def apply_endpoints(endpoints, matching_fields = ['Indicator']):
    """
    Returns a dataframe in LCIAmethod format that contains endpoint factors
        based on conversion factors supplied in passed param 'endpoints'
    param endpoints must conform to Endpoints specs
    param matching_fields: list of fields on which to apply unique endpoint
        conversions
    """
    log.info('developing endpoint methods...')
    indicators = endpoints[['Method'] + matching_fields]
    
    method = pd.DataFrame()
    
    for e in matching_fields:
        endpoints[e].fillna("", inplace=True)
    
    for m in indicators['Method'].unique():
        method_indicators = indicators[indicators['Method']==m]
        mapped_method = lciafmt.get_mapped_method(m, methods=[m])
        endpoint_method = mapped_method.merge(endpoints[matching_fields +
                                                  ['Method',
                                                  'Endpoint Indicator',
                                                  'Endpoint Indicator unit',
                                                  'Conversion factor']],
                                       how = 'left',
                                       on = matching_fields + ['Method'])
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

        #Determine fields to aggregate over. Use all fields except CF which are summed
        agg_fields = list(set(endpoint_method.columns) - {'Characterization Factor'})
        endpoint_method_agg = endpoint_method.groupby(agg_fields, as_index=False).agg(
            {'Characterization Factor': 'sum'})
        
        # Sort
        endpoint_method_agg = endpoint_method_agg[endpoint_method.columns]
        endpoint_method_agg.sort_values(by=['Indicator','Flowable','Context'], inplace=True)
        
        method = method.append(endpoint_method_agg, ignore_index = True)
    
    return method
