class TaskInput:
    def __init__(self, task_id: str, issue_text: str, repository_path: str, optional_hints: str = "", metadata: dict = None):
        self.task_id = task_id
        self.issue_text = issue_text
        self.repository_path = repository_path
        self.optional_hints = optional_hints
        self.metadata = metadata or {}

class ControllerBackends:
    def __init__(self, query_provider=None, semantic_backend=None, graph_backend=None,
                 localization_provider=None, diagnosis_provider=None, patch_provider=None, submission_backend=None,
                 source_backend=None, command_backend=None):
        self.query_provider = query_provider
        self.semantic_backend = semantic_backend
        self.graph_backend = graph_backend
        self.localization_provider = localization_provider
        self.diagnosis_provider = diagnosis_provider
        self.patch_provider = patch_provider
        self.submission_backend = submission_backend
        self.source_backend = source_backend
        self.command_backend = command_backend
