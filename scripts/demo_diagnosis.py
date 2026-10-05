import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.localization.localization_result import FocusedRead
from src.diagnosis.source_acquisition import FakeSourceBackend, acquire_focused_source
from src.diagnosis.diagnosis_provider import MockDiagnosisProvider, DiagnosisResult, RootCauseLocation, NextAction, ActionType, ActionCost
from src.agent.diagnosis_controller import DiagnosisController
from src.agent.state import AgentState, SearchEvidence

def main():
    print("========================================")
    print("MOCK DIAGNOSIS DEMO - STAGE 8")
    print("========================================\n")
    
    # Fake source file
    source_content = "def test_foo():\n    assert foo() == 1\n"
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "foo.py").write_text(source_content)
        backend = FakeSourceBackend(root)
        
        reads = [FocusedRead("foo.py", 1, 10, "Because foo")]
        snippets = acquire_focused_source(backend, reads)
        
        print("Focused reads acquired:")
        for s in snippets:
            print(f"  {s.path}:{s.line_start}-{s.line_end} ({s.reason})")
        print()
        
        res = DiagnosisResult(
            observation="Observed foo returning wrong value.",
            hypothesis_statement="foo is incorrectly implemented.",
            supporting_evidence_ids=["E01"],
            disconfirming_evidence_ids=[],
            root_cause_location=RootCauseLocation("foo.py", "foo", 1, 2),
            invariant="foo() must return 1",
            confidence="HIGH",
            recommended_action=NextAction(ActionType.PATCH, ActionCost.CHEAP, "Patch foo"),
            patch_readiness="READY"
        )
        provider = MockDiagnosisProvider(res)
        controller = DiagnosisController(provider)
        
        state = AgentState()
        state.budget.hard_model_turns = 5
        state.search_evidence = [SearchEvidence("E001", "LEXICAL", "foo", confidence="STRONG")]
        
        controller.run_diagnosis(state, snippets)
        
        print("Initial Hypothesis:")
        h = state.debug.active_hypothesis
        print(f"  [{h.hypothesis_id}] {h.statement} (Status: {h.status}, Confidence: {h.confidence})")
        print(f"  Location: {h.location}")
        print(f"  Next Action: {res.recommended_action.action_type.name} - {res.recommended_action.description}\n")
        
        # New contradictory hypothesis
        res2 = DiagnosisResult(
            observation="Observed foo is fine, but bar is wrong.",
            hypothesis_statement="bar is incorrectly implemented.",
            supporting_evidence_ids=["E02"],
            disconfirming_evidence_ids=["E01"],
            root_cause_location=RootCauseLocation("bar.py", "bar", 1, 2),
            invariant="bar() must work",
            confidence="HIGH",
            recommended_action=NextAction(ActionType.PATCH, ActionCost.CHEAP, "Patch bar"),
            patch_readiness="READY"
        )
        provider.mock_result = res2
        controller.run_diagnosis(state, snippets)
        
        print("After Contradiction:")
        h2 = state.debug.active_hypothesis
        print(f"  New Active: [{h2.hypothesis_id}] {h2.statement} (Status: {h2.status})")
        rej = state.debug.rejected_hypotheses[0]
        print(f"  Rejected: [{rej.hypothesis_id}] {rej.statement} (Status: {rej.status})\n")
        
if __name__ == "__main__":
    main()
