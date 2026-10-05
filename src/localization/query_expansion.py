import json
import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

QUERY_EXPANSION_PROMPT_VERSION = "e00_qe_v1"
EXPANSION_PROMPT = """You are generating repository-search terms for a software issue.
Return only terms likely to appear in implementation or tests.
Do not propose solutions.
Do not diagnose the bug.
Do not invent libraries or architecture.
Prefer concrete code concepts.
Return at most:
5 implementation concepts
3 test terms
3 possible symbols.
Use the issue text and existing exact-search evidence.
Return structured JSON."""

@dataclass
class QueryExpansion:
    implementation_concepts: List[str] = field(default_factory=list)
    test_terms: List[str] = field(default_factory=list)
    alternative_symbols: List[str] = field(default_factory=list)
    rationale_tags: List[str] = field(default_factory=list)
    source: str = "gemma"
    truncated: bool = False

class QueryExpansionProvider:
    def expand(self, issue_text: str, lexical_summary: str) -> Optional[QueryExpansion]:
        raise NotImplementedError

class MockQueryExpansionProvider(QueryExpansionProvider):
    def __init__(self, mock_response: Optional[QueryExpansion] = None):
        self.mock_response = mock_response
        self.last_issue = ""
        
    def expand(self, issue_text: str, lexical_summary: str) -> Optional[QueryExpansion]:
        self.last_issue = issue_text
        if self.mock_response is None:
            return QueryExpansion(
                implementation_concepts=["mock concept"],
                test_terms=["mock test"],
                alternative_symbols=["mock_symbol"]
            )
        return self.mock_response

class HarnessGemmaQueryExpansionProvider(QueryExpansionProvider):
    def expand(self, issue_text: str, lexical_summary: str) -> Optional[QueryExpansion]:
        raise RuntimeError("HarnessGemmaQueryExpansionProvider not yet bound to official Kaggle runtime.")

def validate_and_truncate_expansion(
    qe: QueryExpansion, 
    max_impl: int = 5, 
    max_test: int = 3, 
    max_sym: int = 3
) -> QueryExpansion:
    def sanitize(terms, max_k):
        clean = []
        for t in terms:
            t = str(t).strip()
            if t and len(t) < 60 and "```" not in t and t not in clean:
                clean.append(t)
        return clean[:max_k], len(clean) > max_k
        
    impl, trunc_impl = sanitize(qe.implementation_concepts, max_impl)
    test, trunc_test = sanitize(qe.test_terms, max_test)
    sym, trunc_sym = sanitize(qe.alternative_symbols, max_sym)
    
    return QueryExpansion(
        implementation_concepts=impl,
        test_terms=test,
        alternative_symbols=sym,
        rationale_tags=qe.rationale_tags[:3],
        source=qe.source,
        truncated=qe.truncated or trunc_impl or trunc_test or trunc_sym
    )
