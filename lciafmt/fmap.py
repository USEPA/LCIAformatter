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
