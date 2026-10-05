from src.localization.query_expansion import (
    QueryExpansion, validate_and_truncate_expansion
)

def test_validate_and_truncate():
    qe = QueryExpansion(
        implementation_concepts=["a", "b", "c", "d", "e", "f", "g"], # 7
        test_terms=["t1", "t2", "t3", "t4"], # 4
        alternative_symbols=["s1", "s2", "s3"], # 3
        rationale_tags=["r1", "r2", "r3", "r4"] # 4
    )
    
    clean = validate_and_truncate_expansion(qe)
    
    assert len(clean.implementation_concepts) == 5
    assert len(clean.test_terms) == 3
    assert len(clean.alternative_symbols) == 3
    assert len(clean.rationale_tags) == 3
    assert clean.truncated is True

def test_validate_empty_and_malformed():
    qe = QueryExpansion(
        implementation_concepts=["", "   ", "```python\ncode\n```", "valid"]
    )
    
    clean = validate_and_truncate_expansion(qe)
    assert clean.implementation_concepts == ["valid"]
