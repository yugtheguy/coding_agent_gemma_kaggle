def normalize_relation(raw_relation: str) -> str:
    r = raw_relation.upper()
    if "CALLER" in r or "CALLED_BY" in r:
        return "CALLER"
    if "CALLEE" in r or "CALLS" in r:
        return "CALLEE"
    if "IMPORT" in r:
        return "IMPORT"
    if "INHERIT" in r or "BASE" in r or "EXTEND" in r or "IMPLEMENT" in r:
        return "INHERITANCE"
    if "OVERRIDE" in r:
        return "OVERRIDE"
    if "TEST" in r:
        return "TEST_TARGET"
    if "REF" in r or r == "USES":
        return "REFERENCE"
        
    return "UNKNOWN"
