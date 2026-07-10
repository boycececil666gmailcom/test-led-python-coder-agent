# Design Document


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

## Architecture & State Workflow


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


## Data Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as User/Caller
    participant Graph as LangGraph Engine
    participant State as AgentState (Memory)
    participant Tests as node_run_tests (Pytest)
    participant Edge as cond_should_continue (Router)
    participant LLM as node_generate_code (LLM)

    User->>Graph: invoke(inputs: file_path, test_path, max_iterations)
    Graph->>State: Initialize state fields
    Note over State: Set iterations = 0

    loop Self-Correction Loop (Up to max_iterations)
        Graph->>Tests: Execute node
        Tests->>State: Read test_path & file_path
        Tests->>Tests: Run pytest command
        Tests->>State: Update test_logs & test_passed
        Graph->>Edge: Route evaluation
        Edge->>State: Read test_passed & iterations

        alt test_passed == True OR iterations >= max_iterations
            Edge->>Graph: Transition to __end__
            Graph->>User: Return final State (Success/Failure)
        else test_passed == False AND iterations < max_iterations
            Edge->>Graph: Transition to node_generate_code
            Graph->>LLM: Execute node
            LLM->>State: Read file_path, code & test_logs
            LLM->>LLM: Query LLM for code fix
            LLM->>LLM: Write corrected code to file
            LLM->>State: Update code & increment iterations
            LLM->>Graph: Transition back to node_run_tests
        end
    end
```