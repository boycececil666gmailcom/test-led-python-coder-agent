# Test-Led Python Coder Agent

This project implements an autonomous test-driven code repair agent using LangGraph.

## Core Design Principles

### 1. Python-Specific Scope
This agent is built **exclusively for Python coding** and does not support other programming languages.
* **Why?** It relies heavily on local Python-specific AST syntax validators ([node_check_syntax.py](file:///c:/Users/boyce/OneDrive/Desktop/auto-coder-langgraph/TestCoding/nodes/node_check_syntax.py)) and the `pytest` runner.
* **Extensibility**: While adding support for other execution environments (such as JavaScript/Jest or Rust/Cargo) is straightforward, we restrict the scope to Python to keep the codebase highly focused and manageable.

### 2. Test-Driven & Review-Led Coding
This project is built around the concept of **Human-Reviewed, Test-Driven AI Coding**:
* The human user is not expected to review the implementation code produced by the LLM.
* Instead, the human user reviews and approves the **test script** (either provided directly or generated from a natural language description). 
* Once the test suite is approved, the AI executes in a closed self-correction loop until it passes the tests. We focus on the functional outcome (passing tests) verified by the human-led test definitions.

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

    START(["🚀 START (Sentinel: '__start__')"]):::startEnd --> node_validate_inputs

    node_validate_inputs["node_validate_inputs (Role: Validate file path and inputs)"]:::graphNode

    node_validate_inputs --> cond_route_entry

    cond_route_entry{"cond_route_entry (Role: Route based on verification)"}:::conditionalEdge

    cond_route_entry -- "❌ Invalid Input<br/>(Returns: 'END')" --> END_FAIL(["❌ END: Failed (Sentinel: 'END')"]):::startEnd
    cond_route_entry -- "✅ Has test_path<br/>(Returns: 'node_check_syntax')" --> node_check_syntax
    cond_route_entry -- "📝 Has description<br/>(Returns: 'node_generate_test')" --> node_generate_test

    node_generate_test["node_generate_test (Role: Generate pytest script from prompt description)"]:::graphNode
    
    node_generate_test --> node_human_review

    node_human_review["node_human_review (Role: Pause for terminal user review)"]:::graphNode

    node_human_review --> cond_after_review

    cond_after_review{"cond_after_review (Role: Route based on review feedback)"}:::conditionalEdge

    cond_after_review -- "✅ Approved<br/>(Returns: 'node_check_syntax')" --> node_check_syntax
    cond_after_review -- "❌ Canceled<br/>(Returns: 'END')" --> END_FAIL
    cond_after_review -- "🔁 feedback<br/>(Returns: 'node_generate_test')" --> node_generate_test

    node_check_syntax["node_check_syntax (Role: Validate syntax structure)"]:::graphNode

    node_check_syntax --> cond_after_syntax_check{"cond_after_syntax_check (Role: Route based on syntax result)"}:::conditionalEdge

    cond_after_syntax_check -- "❌ Failed<br/>(Returns: 'node_generate_code')" --> node_generate_code
    cond_after_syntax_check -- "✅ Passed<br/>(Returns: 'node_run_tests')" --> node_run_tests

    node_run_tests["node_run_tests (Role: Run tests & collect logs)"]:::graphNode
    
    node_run_tests --> cond_should_continue

    cond_should_continue{"cond_should_continue (Role: Evaluate test_passed & limits)"}:::conditionalEdge

    cond_should_continue -- "✅ Passed<br/>(Returns: '__end__')" --> END_SUCCESS(["✅ END: Success (Sentinel: '__end__')"]):::startEnd
    cond_should_continue -- "❌ Failed & Iterations Exceeded<br/>(Returns: '__end__')" --> END_SUCCESS
    cond_should_continue -- "🔁 Retry Needed<br/>(Returns: 'node_generate_code')" --> node_generate_code

    node_generate_code["node_generate_code (Role: Write code fix based on error logs)"]:::graphNode
    
    node_generate_code --> node_check_syntax
```

## Data Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as User/Caller
    participant Engine as LangGraph Orchestrator
    participant Validator as Validator Node
    participant LLM as Ollama (Local LLM)
    participant Runner as Test Runner Module

    User->>Engine: invoke(file_path, test_path / description, max_iterations)
    Engine->>Validator: Run Validate Inputs Node
    Note over Validator: Verify target file exists & test specs are provided

    alt validation_passed == False
        Validator-->>User: Exits immediately with validation error message
    else validation_passed == True
        alt Has test_description (Test Gen Mode)
            loop Human-in-the-Loop Review Loop
                Engine->>LLM: Generate pytest script from description
                Engine->>User: Display generated test & wait for console input()
                User-->>Engine: Enter Approval ('y'), Abort ('exit'), or Rejection Feedback
            end
        end

        loop Self-Correction Loop (up to max_iterations)
            Engine->>Engine: Run Syntax Verification Node
            alt syntax_passed == False
                Engine->>LLM: Query LLM to resolve syntax issues
            else syntax_passed == True
                Engine->>Runner: Execute Test Runner (pytest)
                Runner-->>Engine: Return test_logs & test_passed
                alt test_passed == True
                    Note over Engine: Finish successfully
                else test_passed == False
                    Engine->>LLM: Query LLM to correct logic bugs based on test logs
                end
            end
        end
    end
```

## Directory Structure

```mermaid
graph TD
    classDef dir fill:#efebe9,stroke:#5d4037,stroke-width:2px,color:#3e2723;
    classDef file fill:#eceff1,stroke:#455a64,stroke-width:1px,color:#263238;

    Workspace["📂 auto-coder-langgraph/ (Workspace Root)"]:::dir
    Workspace --> TestCoding["📂 TestCoding/"]:::dir
    
    TestCoding --> agent_py["📄 agent.py (Graph instantiation)"]:::file
    TestCoding --> state_py["📄 state.py (AgentState TypedDict)"]:::file
    TestCoding --> nodes_dir["📂 nodes/ (Subpackage)"]:::dir
    
    nodes_dir --> init_py["📄 __init__.py (Interface exposure)"]:::file
    nodes_dir --> node_run_tests_py["📄 node_run_tests.py (pytest run node)"]:::file
    nodes_dir --> node_generate_code_py["📄 node_generate_code.py (LLM logic node)"]:::file
    nodes_dir --> node_check_syntax_py["📄 node_check_syntax.py (Syntax verification node)"]:::file
    nodes_dir --> node_validate_inputs_py["📄 node_validate_inputs.py (Input check node)"]:::file
    nodes_dir --> node_generate_test_py["📄 node_generate_test.py (Test generator node)"]:::file
    nodes_dir --> node_human_review_py["📄 node_human_review.py (Console review node)"]:::file
    nodes_dir --> cond_should_continue_py["📄 cond_should_continue.py (Syntax & execution condition edges)"]:::file
    nodes_dir --> cond_route_entry_py["📄 cond_route_entry.py (Entry router edge)"]:::file
    nodes_dir --> cond_after_review_py["📄 cond_after_review.py (Review router edge)"]:::file
```

## State Fields (`AgentState`)

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `file_path` | `str` | Path to the source code file to be modified |
| `test_path` | `str` | Path to the pytest test file to be executed |
| `code` | `str` | Current source code content |
| `test_logs` | `str` | Output from the most recent pytest execution (e.g., error logs) |
| `test_passed` | `bool` | Flag indicating whether all tests passed |
| `syntax_passed` | `bool` | Flag indicating whether code syntax parsing succeeded |
| `iterations` | `int` | Current iteration count of the self-correction loop |
| `max_iterations` | `int` | Maximum loop limit (prevents infinite loops, default: 3) |
| `messages` | `list` | Chat message history (standard conversation history for LangGraph) |
| `test_description` | `str` | Prompt description used to generate test scripts |
| `validation_passed` | `bool` | Flag indicating if initial requirements are valid |
| `error_message` | `str` | Logs description of errors during validation |
| `review_feedback` | `str` | Review notes provided by the user on test script rejection |


