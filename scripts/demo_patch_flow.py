import sys
import tempfile
import subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.patching.patch_backend import LocalEditBackend
from src.patching.patch_result import PatchProposal
from src.agent.patch_controller import MockPatchProvider, PatchController
from src.agent.state import AgentState
from src.agent.debug_ledger import Hypothesis
from src.patching.test_selection import VerificationTarget

def main():
    print("========================================")
    print("MOCK PATCH FLOW DEMO - STAGE 9")
    print("========================================\n")
    
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        
        subprocess.run("git init", cwd=str(root), shell=True, capture_output=True)
        subprocess.run("git config user.email 'test@test.com'", cwd=str(root), shell=True, capture_output=True)
        subprocess.run("git config user.name 'Test'", cwd=str(root), shell=True, capture_output=True)
        
        (root / "foo.py").write_text("def foo():\n    return 0\n")
        subprocess.run("git add foo.py", cwd=str(root), shell=True, capture_output=True)
        subprocess.run("git commit -m 'init'", cwd=str(root), shell=True, capture_output=True)
        
        proposal1 = PatchProposal(
            path="foo.py",
            target_symbol="foo",
            edit_type="REPLACE",
            old_text="return 0",
            new_text="return 1",
            reason_summary="Fix return value",
            expected_invariant_restored="foo returns 1",
            expected_behavior_change="Fix",
            risk_notes=""
        )
        
        class DemoBackend(LocalEditBackend):
            def run_command(self, command):
                if command == "pytest":
                    return "1 passed"
                return super().run_command(command)
                
        backend = DemoBackend(root)
        provider = MockPatchProvider(proposal1)
        controller = PatchController(provider, backend)
        
        state = AgentState()
        state.budget.hard_model_turns = 5
        h = Hypothesis("H001", "hyp", "ACTIVE", [], [], "foo.py:1-2", "HIGH")
        state.debug.active_hypothesis = h
        state.patch_readiness = "READY"
        state.invariant = "foo() == 1"
        
        target = VerificationTarget("pytest", "EXISTING_TEST", "Test foo", "pass", "CHEAP")
        
        print("SCENARIO A: Clean Patch")
        print("Executing patch...")
        status = controller.run_patch_and_verify(state, target)
        print(f"Result: {status}")
        print(f"File content:\n{(root / 'foo.py').read_text()}")
        
        print("\nSCENARIO D: Syntax Failure")
        state.budget.patch_attempts_used = 0 
        proposal2 = PatchProposal(
            path="foo.py",
            target_symbol="foo",
            edit_type="REPLACE",
            old_text="return 1",
            new_text="return 2  ++",
            reason_summary="Syntax error",
            expected_invariant_restored="",
            expected_behavior_change="",
            risk_notes=""
        )
        provider.proposal = proposal2
        
        status2 = controller.run_patch_and_verify(state, target)
        print(f"Result: {status2}")
        print(f"File content after rollback:\n{(root / 'foo.py').read_text()}")
        
if __name__ == "__main__":
    main()
