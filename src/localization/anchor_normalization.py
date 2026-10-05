from .anchors import AnchorType

def normalize_anchor(value: str, anchor_type: AnchorType) -> str:
    if anchor_type == AnchorType.FILE_PATH:
        val = value.replace("\\", "/")
        if val.startswith("/workspace/"):
            val = val[len("/workspace/"):]
        return val
    elif anchor_type == AnchorType.CONFIG_KEY:
        if value.startswith("--"):
            return value[2:]
        return value
    elif anchor_type == AnchorType.DOTTED_NAME or anchor_type == AnchorType.BACKTICKED_TERM:
        if value.endswith("()"):
            return value[:-2]
        return value
    elif anchor_type in (AnchorType.DOMAIN_TERM, AnchorType.TEST_CLUE):
        return value.lower()
    return value
