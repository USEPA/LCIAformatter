import logging as log
from typing import Optional

import olca
import olca.pack as pack
import pandas

from .util import make_uuid


class Writer(object):

    def __init__(self, zip_file: str):
        log.info("create JSON-LD writer on %s", zip_file)
        self.__writer = pack.Writer(zip_file)
        self.__methods = {}
        self.__indicators = {}
        self.__flows = {}
        self.__categories = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__writer.close()

    def write(self, df: pandas.DataFrame):
        for _, row in df.iterrows():
            indicator = self.__indicator(row)
            factor = olca.ImpactFactor()
            flow = self.__flow(row)
            unit = row[8]
            factor.flow = olca.ref(olca.Flow, flow.id)
            factor.flow_property = _property_ref(unit)
            factor.unit = _unit_ref(unit)
            factor.value = row[12]
            indicator.impact_factors.append(factor)

        log.info("write entities")
        dicts = [
            self.__categories,
            self.__flows,
            self.__indicators,
            self.__methods
        ]
        for d in dicts:
            for v in d.values():
                self.__writer.write(v)

    def __indicator(self, row) -> olca.ImpactCategory:
        uid = row[3]
        ind = self.__indicators.get(uid)
        if ind is not None:
            return ind
        log.info("init indicator %s", row[2])
        ind = olca.ImpactCategory()
        ind.id = uid
        ind.name = row[2]
        ind.reference_unit_name = row[4]
        ind.impact_factors = []
        self.__indicators[uid] = ind

        method = self.__method(row)
        ref = olca.ImpactCategoryRef()
        ref.id = uid
        ref.name = ind.name
        ref.ref_unit = ind.reference_unit_name
        method.impact_categories.append(ref)
        return ind

    def __method(self, row) -> olca.ImpactMethod:
        uid = row[1]
        m = self.__methods.get(uid)
        if m is not None:
            return m
        log.info("init method %s", row[0])
        m = olca.ImpactMethod()
        m.id = uid
        m.name = row[0]
        m.impact_categories = []
        self.__methods[uid] = m
        return m

    def __flow(self, row):
        uid = row[6]
        flow = self.__flows.get(uid)
        if flow is not None:
            return flow
        flow = olca.Flow()
        flow.id = uid
        flow.name = row[5]
        flow.cas = row[6]

        # flow property
        prop_ref = _property_ref(row[8])
        if prop_ref is not None:
            prop_fac = olca.FlowPropertyFactor()
            prop_fac.conversion_factor = 1.0
            prop_fac.reference_flow_property = True
            prop_fac.flow_property = prop_ref
            flow.flow_properties = [prop_fac]

        # category
        c = self.__category(row)
        if c is not None:
            flow.category = olca.ref(olca.Category, c.id)

        self.__flows[uid] = flow
        return flow

    def __category(self, row) -> Optional[olca.Category]:
        cpath = row[7]  # type: str
        if cpath is None or cpath.strip() == "":
            return None
        c = self.__categories.get(cpath)
        if c is not None:
            return c

        p = None
        parts = cpath.split("/")
        for i in range(0, len(parts)):
            if c is not None:
                p = c
            cpath = "/".join(parts[0:(i + 1)])
            c = self.__categories.get(cpath)
            if c is not None:
                continue
            log.info("init category %s", cpath)
            c = olca.Category()
            c.id = make_uuid("category/flow/" + cpath)
            c.name = parts[i]
            c.model_type = olca.ModelType.FLOW
            if p is not None:
                c.category = olca.ref(olca.Category, p.id)
            self.__categories[cpath] = c
        return c


def _property_ref(unit: str) -> Optional[olca.Ref]:
    if unit == "kg":
        return olca.ref(
            olca.FlowProperty, "93a60a56-a3c8-11da-a746-0800200b9a66", "Mass")
    log.error("unknown unit %s", unit)
    return None


def _unit_ref(unit: str) -> Optional[olca.Ref]:
    if unit == "kg":
        return olca.ref(
            olca.Unit, "20aadc24-a391-41cf-b340-3e4529f44bde", "kg")
    log.error("unknown unit %s", unit)
    return None
