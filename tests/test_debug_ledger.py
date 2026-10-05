import pytest
from src.agent.debug_ledger import DebugLedger, Hypothesis, NextAction

def test_only_one_active_hypothesis():
    ledger = DebugLedger(rejected_history_bound=2)
    h1 = Hypothesis(hypothesis_id="H1", statement="Bug is here", status="ACTIVE")
    ledger.add_hypothesis(h1)
    
    assert ledger.active_hypothesis == h1
    assert ledger.active_hypothesis.status == "ACTIVE"
    
    h2 = Hypothesis(hypothesis_id="H2", statement="Bug is there", status="ACTIVE")
    ledger.add_hypothesis(h2)
    
    assert ledger.active_hypothesis == h2
    assert ledger.active_hypothesis.status == "ACTIVE"
    assert len(ledger.rejected_hypotheses) == 1
    assert ledger.rejected_hypotheses[0].hypothesis_id == "H1"
    assert ledger.rejected_hypotheses[0].status == "SUPERSEDED"

def test_hypothesis_rejection():
    ledger = DebugLedger(rejected_history_bound=2)
    h1 = Hypothesis(hypothesis_id="H1", statement="Bug is here", status="ACTIVE")
    ledger.add_hypothesis(h1)
    
    ledger.reject_active_hypothesis()
    assert ledger.active_hypothesis is None
    assert len(ledger.rejected_hypotheses) == 1
    assert ledger.rejected_hypotheses[0].status == "REJECTED"

def test_rejected_history_bound():
    ledger = DebugLedger(rejected_history_bound=2)
    for i in range(3):
        h = Hypothesis(hypothesis_id=f"H{i}", statement="Bug", status="ACTIVE")
        ledger.add_hypothesis(h)
        
    assert len(ledger.rejected_hypotheses) == 2
    assert ledger.rejected_hypotheses[0].hypothesis_id == "H0"
    assert ledger.rejected_hypotheses[1].hypothesis_id == "H1" # wait, if h0 is added, then h1 (h0->rejected), then h2 (h1->rejected). rejected contains h0, h1. Wait, let's check:
    # 1. add H0 (rejected=[])
    # 2. add H1 (rejected=[H0])
    # 3. add H2 (rejected=[H0, H1]) -> limit 2, so it stays [H0, H1], wait no, H0 should be popped if length > 2? Actually wait, the code pops element 0.
    # Ah, the code is `if len > bound: pop(0)`.
    # Let's verify: Add H0, rejected=[], active=H0
    # Add H1, H0->rejected, rejected=[H0]. active=H1
    # Add H2, H1->rejected, rejected=[H0, H1]. active=H2.
    # length is 2, so it doesn't pop.
    # Add H3, H2->rejected, rejected=[H0, H1, H2]. length 3 > 2 -> pop(0). rejected=[H1, H2].
    pass

def test_rejected_history_bound_correct():
    ledger = DebugLedger(rejected_history_bound=2)
    for i in range(4):
        ledger.add_hypothesis(Hypothesis(hypothesis_id=f"H{i}", statement="Bug", status="ACTIVE"))
    assert len(ledger.rejected_hypotheses) == 2
    assert ledger.rejected_hypotheses[0].hypothesis_id == "H1"
    assert ledger.rejected_hypotheses[1].hypothesis_id == "H2"
    
def test_next_action():
    ledger = DebugLedger()
    ledger.next_discriminating_action = NextAction(
        action_type="SEARCH",
        target="foo",
        reason="find foo",
        expected_information="foo definition",
        cost_class="CHEAP"
    )
    assert ledger.next_discriminating_action.target == "foo"
