import tempfile
from pathlib import Path
from src.agent.state import AgentState
from src.agent.debug_ledger import Hypothesis
from src.patching.patch_result import PatchProposal
from src.patching.patch_backend import LocalEditBackend
from src.agent.patch_controller import MockPatchProvider, PatchController
from src.patching.test_selection import VerificationTarget

def setup_controller(root: Path, proposal: PatchProposal):
    backend = LocalEditBackend(root)
    provider = MockPatchProvider(proposal)
    return PatchController(provider, backend)
    
def test_patch_controller_clean_patch():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "foo.py").write_text("def foo():\n    return 0\n")
        
        # Need to initialize git for git diff --numstat
        import subprocess
        subprocess.run("git init", cwd=str(root), shell=True, capture_output=True)
        subprocess.run("git config user.email 'test@test.com'", cwd=str(root), shell=True, capture_output=True)
        subprocess.run("git config user.name 'Test'", cwd=str(root), shell=True, capture_output=True)
        subprocess.run("git add foo.py", cwd=str(root), shell=True, capture_output=True)
        subprocess.run("git commit -m 'init'", cwd=str(root), shell=True, capture_output=True)
        
        proposal = PatchProposal("foo.py", "foo", "REPLACE", "return 0", "return 1", "", "", "", "")
        controller = setup_controller(root, proposal)
        
        state = AgentState()
        state.budget.hard_model_turns = 5
        h = Hypothesis("H001", "hyp", "ACTIVE", [], [], "foo.py:1-2", "HIGH")
        state.debug.active_hypothesis = h
        
        status = controller.run_patch_and_verify(state)
        assert status == "VERIFY_REGRESSION"
        assert (root / "foo.py").read_text() == "def foo():\n    return 1\n"
        
def test_patch_controller_syntax_error():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "foo.py").write_text("def foo():\n    return 0\n")
        import subprocess
        subprocess.run("git init", cwd=str(root), shell=True, capture_output=True)
        subprocess.run("git config user.email 'test@test.com'", cwd=str(root), shell=True, capture_output=True)
        subprocess.run("git config user.name 'Test'", cwd=str(root), shell=True, capture_output=True)
        subprocess.run("git add foo.py", cwd=str(root), shell=True, capture_output=True)
        subprocess.run("git commit -m 'init'", cwd=str(root), shell=True, capture_output=True)
        
        proposal = PatchProposal("foo.py", "foo", "REPLACE", "return 0", "return 1  ++", "", "", "", "")
        controller = setup_controller(root, proposal)
        
        state = AgentState()
        state.budget.hard_model_turns = 5
        h = Hypothesis("H001", "hyp", "ACTIVE", [], [], "foo.py:1-2", "HIGH")
        state.debug.active_hypothesis = h
        
        status = controller.run_patch_and_verify(state)
        assert status == "SYNTAX_FAILED"
        assert (root / "foo.py").read_text() == "def foo():\n    return 0\n"

def test_patch_controller_target_failure():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "foo.py").write_text("def foo():\n    return 0\n")
        import subprocess
        subprocess.run("git init", cwd=str(root), shell=True, capture_output=True)
        subprocess.run("git config user.email 'test@test.com'", cwd=str(root), shell=True, capture_output=True)
        subprocess.run("git config user.name 'Test'", cwd=str(root), shell=True, capture_output=True)
        subprocess.run("git add foo.py", cwd=str(root), shell=True, capture_output=True)
        subprocess.run("git commit -m 'init'", cwd=str(root), shell=True, capture_output=True)
        
        proposal = PatchProposal("foo.py", "foo", "REPLACE", "return 0", "return 1", "", "", "", "")
        controller = setup_controller(root, proposal)
        
        state = AgentState()
        state.budget.hard_model_turns = 5
        h = Hypothesis("H001", "hyp", "ACTIVE", [], [], "foo.py:1-2", "HIGH")
        state.debug.active_hypothesis = h
        
        class MockFailingBackend(LocalEditBackend):
            def run_command(self, command):
                if command.startswith("python -m py_compile"):
                    return "" 
                if command == "git diff --numstat":
                    return "1\t1\tfoo.py"
                if command == "git diff --check":
                    return ""
                return "FAILURES: same original assertion"
                
        controller.backend = MockFailingBackend(root)
        
        target = VerificationTarget("pytest", "EXISTING_TEST", "", "", "CHEAP")
        status = controller.run_patch_and_verify(state, target)
        
        assert status == "TARGET_FAILED_SAME_REASON"
