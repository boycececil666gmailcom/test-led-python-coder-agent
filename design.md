# Design Document: AutoRepairAgent (Self-Correction Loop)

This document describes the design, directory structure, and state management for the autonomous code repair agent.

## Agent Identity

* **Name**: `TestCoding`
* **Directory**: [TestCoding](file:///c:/Users/boyce/OneDrive/Desktop/langsmith/TestCoding)

## Directory Structure

```mermaid
graph TD
    classDef dir fill:#efebe9,stroke:#5d4037,stroke-width:2px,color:#3e2723;
    classDef file fill:#eceff1,stroke:#455a64,stroke-width:1px,color:#263238;

    Workspace["📂 langsmith/ (Workspace Root)"]:::dir
    Workspace --> TestCoding["📂 TestCoding/"]:::dir
    Workspace --> design_md["📄 design.md"]:::file
    
    TestCoding --> agent_py["📄 agent.py (Graph instantiation)"]:::file
    TestCoding --> state_py["📄 state.py (AgentState TypedDict)"]:::file
    TestCoding --> nodes_dir["📂 nodes/ (Subpackage)"]:::dir
    
    nodes_dir --> init_py["📄 __init__.py (Interface exposure)"]:::file
    nodes_dir --> node_run_tests_py["📄 node_run_tests.py (pytest run node)"]:::file
    nodes_dir --> node_generate_code_py["📄 node_generate_code.py (LLM logic node)"]:::file
    nodes_dir --> cond_should_continue_py["📄 cond_should_continue.py (Conditional edge logic)"]:::file
```

---

## Terminology Guide

### 1. Code Generator (Code Generation & Modification)
* **Summary**: Takes the test failure logs and current code as input, and uses an LLM to repair bugs in the code.
* **Role**: Writes the corrected/modified code back to the original file.

### 2. Test Runner (pytest Execution)
* **Summary**: Runs pytest against the modified code.
* **Role**: Collects test execution logs and determines if the tests passed or failed.

---

## Architecture & State Workflow

The diagram below details the LangGraph workflow structure. In each node, we clearly distinguish between:
1. **Graph Node Name** (The `str` key registered in the graph).
2. **Implementation Object Name** (The actual Python function or class bound to the node).
3. **Python Type / Signature** (The call signature and return type mapping).
4. **Role** (What the component performs).

```mermaid
flowchart TD
    classDef graphNode fill:#e1f5fe,stroke:#0288d1,stroke-width:2px,color:#01579b;
    classDef conditionalEdge fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#f57f17;
    classDef startEnd fill:#e8f5e9,stroke:#388e3c,stroke-width:2px,color:#1b5e20;
    classDef stateBox fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c;

    subgraph State["State Context"]
        state_schema["State Class: AgentState<br/>Type: typing_extensions.TypedDict<br/>Holds the shared memory of the graph"]:::stateBox
    end

    START(["🚀 START (Sentinel: '__start__')"]):::startEnd --> node_run_tests

    node_run_tests["Node Name: 'node_run_tests'<br/>Impl: node_run_tests() (Function)<br/>Signature: Callable[[AgentState], dict]<br/>Role: Execute pytest & collect logs"]:::graphNode
    
    node_run_tests --> cond_should_continue

    cond_should_continue{"Conditional Edge: cond_should_continue<br/>Impl: cond_should_continue() (Function)<br/>Signature: Callable[[AgentState], str]<br/>Role: Evaluate test_passed & iteration limits"}:::conditionalEdge

    cond_should_continue -- "✅ test_passed == True<br/>(Returns: '__end__')" --> END_SUCCESS(["✅ END: Success (Sentinel: '__end__')"]):::startEnd
    cond_should_continue -- "❌ iterations >= max_iterations<br/>(Returns: '__end__')" --> END_FAIL(["❌ END: Failed (Sentinel: '__end__')"]):::startEnd
    cond_should_continue -- "🔁 Retry Needed<br/>(Returns: 'node_generate_code')" --> node_generate_code

    node_generate_code["Node Name: 'node_generate_code'<br/>Impl: node_generate_code() (Function)<br/>Signature: Callable[[AgentState], dict]<br/>Role: Query LLM for code fix & write to file"]:::graphNode
    
    node_generate_code --> node_run_tests
```

---

## State Fields (`AgentState`)

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `file_path` | `str` | Path to the source code file to be modified |
| `test_path` | `str` | Path to the pytest test file to be executed |
| `code` | `str` | Current source code content |
| `test_logs` | `str` | Output from the most recent pytest execution (e.g., error logs) |
| `test_passed` | `bool` | Flag indicating whether all tests passed |
| `iterations` | `int` | Current iteration count of the self-correction loop |
| `max_iterations` | `int` | Maximum loop limit (prevents infinite loops, default: 3) |
| `messages` | `list` | Chat message history (standard conversation history for LangGraph) |
