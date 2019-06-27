import uuid


def make_uuid(*args: str) -> str:
    path = _as_path(*args)
    return str(uuid.uuid3(uuid.NAMESPACE_OID, path))


def _as_path(*args: str) -> str:
    strings = []
    for arg in args:
        if arg is None:
            continue
        strings.append(str(arg).strip().lower())
    return "/".join(strings)


def is_non_empty_str(s: str) -> bool:
    """Tests if the given parameter is a non-empty string."""
    if not isinstance(s, str):
        return False
    return s.strip() != ""


def is_empty_str(s: str) -> bool:
    if s is None:
        return True
    if isinstance(s, str):
        return s.strip() == ''
    else:
        return False


def format_cas(cas) -> str:
    """ In LCIA method sheets CAS numbers are often saved as numbers. This
        function formats such numbers to strings that matches the general
        format of a CAS numner. It also handles other cases like None values
        etc."""
    if cas is None:
        return ""
    if cas == "x" or cas == "-":
        return ""
    if isinstance(cas, (int, float)):
        cas = str(int(cas))
        if len(cas) > 4:
            cas = cas[:-3] + "-" + cas[-3:-1] + "-" + cas[-1]
        return cas
    return str(cas)
