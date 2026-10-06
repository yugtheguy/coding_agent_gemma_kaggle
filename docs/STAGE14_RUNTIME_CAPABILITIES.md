# STAGE 14 RUNTIME CAPABILITIES

## CONFIRMED (FROM HARNESS_README)

- **Submission Format**: Declarative-only (no arbitrary Python entrypoints are executed). Root agent compiled from `agent.yaml`.
- **Tools Available**: Exactly 9 tools (`run_command`, `submit_patch`, `get_status`, `read_file`, `edit_file`, `write_file`, `get_code_neighbors`, `search_similar_code`, `get_code_subgraph`).
- **Tool Schemas**: Schemas are provided by the competition environment.
- **Hardware/Model**: 4x L4 tensor parallel, running `gemma-4-31b-it-qat-w4a16-ct`.
- **Context Size**: 32768 context length.
- **Environment**: Offline task sandbox.
- **Workspace**: `/workspace` is the root execution path.
- **Scratch Space**: `/tmp` is the recommended path for scratch files (to avoid polluting the `/workspace` diff).
- **Patch Extraction**: Patch extraction behavior is fixed. Any untracked modification in `/workspace` may be included in the diff.
- **Verification Reset**: Phase 2 uses a fresh verification state. Test configs (`pytest.ini`, `conftest.py`, etc.) and test files are reset, meaning test tampering is futile.
- **Free Tools**: `submit_patch` and `get_status` are free (do not cost tool actions).

## UNTESTED IN LIVE AGENT RUN

- **GPU visibility**: (Are we able to see devices via `nvidia-smi`?)
- **Serving process (e.g. vLLM)**: Specifics of internal host latency.
- **Single-request latency**: Real-world generation time on 4x L4 for 32k context.
- **Dependencies**: Real installed packages (e.g., `google_adk` internal version).
