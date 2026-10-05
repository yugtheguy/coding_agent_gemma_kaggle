import ast
from typing import List, Dict, Any

def extract_symbols_from_ast(code: str, path: str) -> List[Dict[str, Any]]:
    symbols = []
    try:
        tree = ast.parse(code)
    except Exception:
        return symbols

    class Visitor(ast.NodeVisitor):
        def __init__(self):
            self.parents = []

        def visit_ClassDef(self, node):
            qualname = ".".join(self.parents + [node.name])
            symbols.append({
                "name": node.name,
                "qualname": qualname,
                "kind": "CLASS",
                "line": node.lineno,
                "end_line": getattr(node, "end_lineno", node.lineno)
            })
            self.parents.append(node.name)
            self.generic_visit(node)
            self.parents.pop()

        def visit_FunctionDef(self, node):
            self._visit_func(node, "FUNCTION")

        def visit_AsyncFunctionDef(self, node):
            self._visit_func(node, "ASYNC_FUNCTION")

        def _visit_func(self, node, kind):
            qualname = ".".join(self.parents + [node.name])
            if self.parents:
                kind = "METHOD"
            symbols.append({
                "name": node.name,
                "qualname": qualname,
                "kind": kind,
                "line": node.lineno,
                "end_line": getattr(node, "end_lineno", node.lineno)
            })
            self.parents.append(node.name)
            self.generic_visit(node)
            self.parents.pop()

    Visitor().visit(tree)
    return symbols
