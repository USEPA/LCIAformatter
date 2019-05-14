import logging as log

import pandas
import fedelemflowlist as flowlist


def norm_category(category_path: str) -> str:
    if category_path is None:
        return ""
    parts = [p.strip(" -").lower() for p in category_path.split("/")]

    norm = []
    for part in parts:

        # ignore words with no relevance
        if part in ("elementary flows", "unspecified"):
            continue

        term = part

        # separate qualifiers
        qualifiers = None
        if "," in part:
            pp = [p.strip() for p in part.split(",")]
            term = pp[0]
            qualifiers = pp[1:]

        # remove prefixes
        if term.startswith("emission to "):
            term = term[12:].strip()
        if term.startswith("in ") or term.startswith("to "):
            term = term[3:].strip()

        # replace words
        if term == "high population density":
            term = "urban"
        if term == "low population density":
            term = "rural"

        if len(norm) > 0:
            # if term(i) == term(i - 1)
            if norm[-1] == term:
                if qualifiers is None:
                    continue
                norm.append(", ".join(qualifiers))
                continue
            # if term(i) ends with term(i - 1)
            if term.endswith(norm[-1]):
                term = term[0:-(len(norm[-1]))].strip(" -")

        # append qualifiers
        if qualifiers is not None:
            term = ", ".join([term] + qualifiers)

        norm.append(term)

    return "/".join(norm)


def _is_empty(val: str) -> bool:
    if val is None or val == "":
        return True
    if isinstance(val, str):
        return val.strip() == ""
    return False


def _is_strv(val) -> bool:
    if not isinstance(val, str):
        return False
    return not _is_empty(val)


class _FlowInfo(object):

    def __init__(self):
        self.uuid = ""
        self.name = ""
        self.category = ""
        self.unit = ""

    def key(self) -> str:
        if not _is_empty(self.uuid):
            return self.uuid
        path = [self.name, self.category, self.unit]
        path = [p.strip().lower() for p in path]
        return "/".join(path)


class Mapper(object):

    def __init__(self, df: pandas.DataFrame, version="0.1",
                 system=None, mapping=None):
        self.__df = df
        self.__system = system
        if mapping is None:
            log.info("load flow mapping v=%s from fed.elem.flows", version)
            mapping = flowlist.get_flowmapping(version=version)
        self.__mapping = mapping  # type: pandas.DataFrame

    def run(self):
        log.info("apply flow mapping")
        map_idx = self._build_map_index()
        mapped = 0
        idx = self.__df.iat
        for row in range(0, self.__df.shape[0]):
            key = Mapper._flow_key(
                name=idx[row, 5],
                category=idx[row, 7],
                unit=idx[row, 8],
            )
            target = map_idx.get(key)
            if target is None:
                log.info("could not map flow %s", key)
                continue
            mapped += 1
        log.info("mapped flows in %i of i% factors",
                 mapped, self.__df.shape[0])

    def _build_map_index(self) -> dict:
        log.info("index mapping flows")
        map_idx = {}
        for _, row in self.__mapping.iterrows():
            sys = row["SourceListName"]
            if self.__system is not None and sys != self.__system:
                continue
            key = Mapper._flow_key(
                name=row["SourceFlowName"],
                category=Mapper._cat_path(
                    row["SourceFlowCategory1"],
                    row["SourceFlowCategory2"],
                    row["SourceFlowCategory3"],
                ),
                unit=row["SourceUnit"],
            )
            target = _FlowInfo()
            target.uuid = row["TargetFlowUUID"]
            target.name = row["TargetFlowName"]
            target.category = Mapper._cat_path(
                row["TargetFlowCategory1"],
                row["TargetFlowCategory2"],
                row["TargetFlowCategory3"],
            )
            target.unit = row["TargetUnit"]
            map_idx[key] = target
        log.info("indexed %i of %i flows from flow map",
                 len(map_idx), self.__mapping.shape[0])
        return map_idx

    @staticmethod
    def _flow_key(name="", category="", unit="") -> str:
        parts = [name]
        if _is_strv(category):
            parts.append(norm_category(category))
        if _is_strv(unit):
            parts.append(unit)
        else:
            parts.append("kg")
        parts = [p.strip().lower() for p in parts]
        return "/".join(parts)

    @staticmethod
    def _cat_path(*args) -> str:
        parts = []
        for arg in args:
            if _is_strv(arg):
                parts.append(arg.strip().lower())
        if len(parts) == 0:
            return ""
        return "/".join(parts)
