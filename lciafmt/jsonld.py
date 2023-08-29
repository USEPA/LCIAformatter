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


class Writer(object):

    def __init__(self, zip_file: str):
        log.debug(f"create JSON-LD writer on {zip_file}")
        self.__writer = zipio.ZipWriter(zip_file)
        self.__methods = {}
        self.__indicators = {}
        self.__flows = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__writer.close()

    def write(self, df: pd.DataFrame, write_flows=False):
        for _, row in df.iterrows():
            indicator = self.__indicator(row)
            factor = o.ImpactFactor()
            unit = row[8]
            factor.flow = self.__flow(row)
            factor.flow_property = units.property_ref(unit)
            factor.unit = units.unit_ref(unit)
            factor.value = row[12]
            indicator.impact_factors.append(factor)

        log.debug("write entities")
        dicts = [
            self.__indicators,
            self.__methods
        ]
        if write_flows:
            dicts.append(self.__flows)
        for d in dicts:
            for v in d.values():
                self.__writer.write(v)

    def __indicator(self, row) -> o.ImpactCategory:
        uid = row[3]
        if not is_non_empty_str(uid):
            uid = make_uuid(row[0], row[2])

        ind = self.__indicators.get(uid)
        if ind is not None:
            return ind
        log.info("writing %s indicator ...", row[2])
        ind = o.ImpactCategory()
        ind.id = uid
        ind.name = row[2]
        ind.ref_unit = row[4]
        ind.impact_factors = []
        self.__indicators[uid] = ind

        method = self.__method(row)
        ref = o.ImpactCategory()
        ref.id = uid
        ref.name = ind.name
        ref.ref_unit = ind.ref_unit
        method.impact_categories.append(ref)
        return ind

    def __method(self, row) -> o.ImpactMethod:
        uid = row[1]
        if not is_non_empty_str(uid):
            uid = make_uuid(row[0])
        description = generate_method_description(row[0])
        m = self.__methods.get(uid)
        if m is not None:
            return m
        log.info("writing %s method ...", row[0])
        m = o.ImpactMethod()
        m.id = uid
        m.name = row[0]
        m.version = pkg_version_number
        m.impact_categories = []
        m.description = description
        self.__methods[uid] = m
        return m

    def __flow(self, row):
        uid = row[6]
        if not is_non_empty_str(uid):
            uid = make_uuid(row[5], row[7], row[8])

        flow = self.__flows.get(uid)
        if flow is not None:
            return flow
        flow = o.Flow()
        flow.id = uid
        flow.name = row[5]
        flow.cas = row[6]
        flow.flow_type = o.FlowType.ELEMENTARY_FLOW

        # flow property
        prop_ref = units.property_ref(row[8])
        if prop_ref is None:
            log.error("could not infer flow property for unit %s", row[8])
        if prop_ref is not None:
            prop_fac = o.FlowPropertyFactor()
            prop_fac.conversion_factor = 1.0
            prop_fac.reference_flow_property = True
            prop_fac.flow_property = prop_ref
            flow.flow_properties = [prop_fac]

        # category
        flow.category=row.Context

        self.__flows[uid] = flow
        return flow
