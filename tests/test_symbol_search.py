import tempfile
from pathlib import Path
from src.localization.symbols import extract_symbols_from_ast

def test_extract_symbols():
    code = """
class Response:
    def render(self):
        pass
        
def parse_url():
    pass
    
async def request():
    pass
"""
    symbols = extract_symbols_from_ast(code, "test.py")
    qualnames = {s["qualname"]: s["kind"] for s in symbols}
    
    assert qualnames.get("Response") == "CLASS"
    assert qualnames.get("Response.render") == "METHOD"
    assert qualnames.get("parse_url") == "FUNCTION"
    assert qualnames.get("request") == "ASYNC_FUNCTION"

def test_extract_symbols_malformed():
    code = "def class () : error"
    symbols = extract_symbols_from_ast(code, "test.py")
    assert symbols == []
