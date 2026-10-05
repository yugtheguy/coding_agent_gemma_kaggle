import pytest
from src.controller.controller_backends import ControllerBackends
from src.controller.controller_config import ControllerConfig
from src.controller.task_controller import TaskController
from src.localization.semantic_backend import FakeSemanticBackend

def test_harness_mode_rejects_mock_bindings():
    config = ControllerConfig(mode="harness", fail_on_missing_harness_binding=True)
    backends = ControllerBackends(semantic_backend=FakeSemanticBackend(mapping={}))
    
    with pytest.raises(Exception, match="INFRA_HARNESS_BINDING_ERROR: semantic_backend is mock"):
        TaskController(backends=backends, config=config)

def test_harness_mode_accepts_real_bindings():
    from src.localization.semantic_backend import HarnessSemanticBackend
    config = ControllerConfig(mode="harness", fail_on_missing_harness_binding=True)
    backends = ControllerBackends(semantic_backend=HarnessSemanticBackend())
    
    # Should not raise
    TaskController(backends=backends, config=config)
