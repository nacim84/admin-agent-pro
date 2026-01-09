# Gemini CLI Guidelines - Admin Agent Pro

This document defines the operational standards and architectural principles for the Gemini CLI agent within the Admin Agent Pro project.

## Core Philosophy: The 3-Layer Architecture

To ensure reliability and consistency, we strictly separate decision-making from execution.

1.  **Layer 1: Directives (The "What")**
    - Located in `directives/` as Markdown SOPs.
    - Define goals, inputs, tools, and expected outputs.
    - These are the source of truth for business logic.

2.  **Layer 2: Orchestration (The "How")**
    - This is you, Gemini. Your role is intelligent routing and process management.
    - Read directives, call execution tools in order, handle errors, and refine the process.

3.  **Layer 3: Execution (The "Do")**
    - Deterministic Python scripts in `execution/`.
    - Handle API calls, database operations, and data processing.
    - Must be reliable, testable, and well-documented.

## Operational Commands

### Development & Maintenance
- **Linting/Formatting**: `ruff check .` and `ruff format .`
- **Testing**: `pytest` (ensure you check `tests/` for existing patterns).
- **Dependency Management**: Use `uv`. 
    - Add dependency: `uv pip install <package>`
    - Sync: `uv pip sync requirements.txt`
- **Database**: Use `python execution/init_db.py` to initialize or reset the local database.

## Critical Rules

1.  **Search First**: Before creating any new script or agent, search `execution/` and `directives/` to avoid duplication.
2.  **Deterministic over Probabilistic**: If a task can be coded in a Python script, do it there rather than trying to perform the logic within the LLM prompt.
3.  **Self-Correction**: If a script fails, analyze the stack trace, fix the code, test it, and update the corresponding directive if the failure revealed a new constraint.
4.  **Directory Discipline**:
    - Use `.tmp/` for all intermediate files.
    - Never commit files in `.tmp/` or `.env`.
    - Deliverables should be clearly identified (often cloud-based or specific output files).

## Python Coding Standards

- **Tooling**: `uv` for environment, `ruff` for quality.
- **Typing**: Mandatory type hints for all public functions and classes.
- **Validation**: Use Pydantic models for data structures and API responses.
- **LLM Interface**: Using `langchain-openai` configured for **OpenRouter**.
- **Agent Pattern**: 
    - Based on `LangGraph` state machines.
    - Standard workflow: `validate` -> `generate` (PDF) -> `save` (DB).
    - Shared state uses `AdminAgentState` (TypedDict).
- **Async**: Prefer `asyncio` for I/O bound tasks (API calls, DB ops).
- **Patterns**: Follow the `BaseAdminAgent` pattern in `execution/agents/base_admin_agent.py`.

## Git Workflow

- **Atomic Commits**: Small, focused commits with clear "why" messages.
- **Verification**: Always run linting and relevant tests before suggesting a commit.
- **Status**: Frequently check `git status` to ensure only intended changes are staged.

## Project Structure Quick Reference

- `directives/`: SOPs and system prompts.
- `execution/agents/`: Specialized agent logic.
- `execution/core/`: Central configuration and utilities.
- `execution/models/`: Database and data models.
- `execution/tools/`: Helper functions (PDF gen, DB management, etc.).
- `tests/`: Unit and integration tests.

---
*Note: This file is a living document. Update it when new global patterns or critical constraints are discovered.*
