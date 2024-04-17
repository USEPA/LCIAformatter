# jsonld.py (lciafmt)
# !/usr/bin/env python3
# coding=utf-8
"""
Functions to support generating JSONLD files for lciafmt
"""

from typing import Optional
import pandas as pd
try:
    import olca_schema as o
    import olca_schema.units as units
    import olca_schema.zipio as zipio
except ImportError:
    raise ImportError("lciafmt now requires olca-schema to align with "
                      "openLCA v2.0. Use pip install olca-schema")

from esupy.util import make_uuid
from .util import is_non_empty_str, generate_method_description,\
    log, pkg_version_number
from .location import extract_coordinates

location_meta = ('https://raw.githubusercontent.com/GreenDelta/data/'
                 'master/refdata/locations.csv')

class Writer(object):

    def __init__(self, zip_file: str):
        log.debug(f"create JSON-LD writer on {zip_file}")
        self.__writer = zipio.ZipWriter(zip_file)
        self.__methods = {}
        self.__indicators = {}
        self.__flows = {}
        self.__coordinates = {}
        self.__locations = {}
        self.__location_meta = pd.read_csv(location_meta).fillna('')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__writer.close()

    def write(self, df: pd.DataFrame, write_flows=False):
        if any(df['Location'] != ''):
            self.__coordinates = extract_coordinates(group='states')
        for _, row in df.iterrows():
            indicator = self.__indicator(row)
            factor = o.ImpactFactor()
            unit = row['Unit']
            factor.flow = self.__flow(row)
            factor.flow_property = units.property_ref(unit)
            factor.unit = units.unit_ref(unit)
            factor.value = row['Characterization Factor']
            if self.__coordinates != {}:
                factor.location = self.__location(row)
            indicator.impact_factors.append(factor)

        log.debug("write entities")
        dicts = [
            self.__indicators,
            self.__methods,
            self.__locations
        ]
        if write_flows:
            dicts.append(self.__flows)
        for d in dicts:
            for v in d.values():
                self.__writer.write(v)

    def __indicator(self, row) -> o.ImpactCategory:
        uid = row['Indicator UUID']
        if not is_non_empty_str(uid):
            uid = make_uuid(row['Method'], row['Indicator'])

        ind = self.__indicators.get(uid)
        if ind is not None:
            return ind
        log.info("writing %s indicator ...", row['Indicator'])
        ind = o.ImpactCategory()
        ind.id = uid
        ind.name = row['Indicator']
        ind.ref_unit = row['Indicator unit']
        ind.category = row['Method']
        direction = ('INPUT' if row['Context'].startswith('resource')
                     else 'OUTPUT')
        ind.direction = o.Direction(direction)
        ind.description = generate_method_description(row['Method'],
                                                      row['Indicator'])
        ind.impact_factors = []
        ind.version = pkg_version_number
        self.__indicators[uid] = ind

        method = self.__method(row)
        ref = o.ImpactCategory()
        ref.id = uid
        ref.name = ind.name
        ref.ref_unit = ind.ref_unit
        method.impact_categories.append(ref)
        return ind

    def __method(self, row) -> o.ImpactMethod:
        uid = row['Method UUID']
        if not is_non_empty_str(uid):
            uid = make_uuid(row['Method'])
        description = generate_method_description(row['Method'])
        m = self.__methods.get(uid)
        if m is not None:
            return m
        log.info("writing %s method ...", row['Method'])
        m = o.ImpactMethod()
        m.id = uid
        m.name = row['Method']
        m.version = pkg_version_number
        m.impact_categories = []
        m.description = description
        self.__methods[uid] = m
        return m

    def __flow(self, row):
        uid = row['Flow UUID']
        if not is_non_empty_str(uid):
            uid = make_uuid(row['Flowable'], row['Context'], row['Unit'])

        flow = self.__flows.get(uid)
        if flow is not None:
            return flow
        flow = o.Flow()
        flow.id = uid
        flow.name = row['Flowable']
        flow.category = 'Elementary flows/' + row['Context']
        flow.cas = row['CAS No']
        flow.flow_type = o.FlowType.ELEMENTARY_FLOW

        # flow property
        prop_ref = units.property_ref(row['Unit'])
        if prop_ref is None:
            log.error("could not infer flow property for unit %s", row['Unit'])
        if prop_ref is not None:
            prop_fac = o.FlowPropertyFactor()
            prop_fac.conversion_factor = 1.0
            prop_fac.is_ref_flow_property = True
            prop_fac.flow_property = prop_ref
            flow.flow_properties = [prop_fac]

        # category
        flow.category=row.Context

        self.__flows[uid] = flow
        return flow

    def __location(self, row):
        if row['Location'] == '':
            # no location specified
            return None
        meta = (self.__location_meta.loc[
            self.__location_meta['Code'] == row['Location']].squeeze())
        if len(meta) == 0:
            # not an available location
            return None
        location = self.__locations.get(meta.ID)
        if location is not None:
            # location found, no need to regenerate
            return location
        location = o.Location(
            id=meta.ID,
            name=meta.Name,
            description=meta.Description,
            category=meta.Category,
            code=meta.Code,
            geometry=self.__coordinates.get(row['Location']),
            latitude=meta.Latitude,
            longitude=meta.Longitude)
        self.__locations[meta.ID] = location
        return location
