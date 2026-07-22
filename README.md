# Test-Led Python Coder Agent

Autonomous test-driven code generation and repair agent built with LangGraph.

---

## 1. Text Summarization

### Business Focus
* **Value Proposition**: Enables development and QA teams to automate Python code repair using human-verified, test-driven specifications. It shifts code verification away from reviewing AI-generated implementation details to approving functional test criteria.
* **Target Outcomes**: Reduces manual debugging overhead, enforces test-driven development (TDD) best practices, and prevents regression by operating in a self-correcting loop until all automated tests pass.
* **Core Functionality**:
  * **Dual Entry Modes**: Supports execution directly against pre-existing `pytest` test suites or via prompt descriptions.
  * **Human-in-the-Loop Review**: Allows interactive terminal review, revision feedback, or approval of generated test scripts before code repair begins.
  * **Bounded Self-Correction**: Automatically generates, syntax-checks, and repairs code against test errors up to a specified maximum iteration limit.

### Tech Focus
* **Technology Stack**: Python 3.10+, [LangGraph](https://github.com/langchain-ai/langgraph) (`StateGraph`), LangChain Core (`BaseMessage`), Pytest runner via Python `subprocess`, Python AST (`ast.parse`), and `python-dotenv`.
* **Architecture & Capabilities**: Modular graph-based state machine leveraging a central `AgentState` (`TypedDict`). Features AST syntax validation, isolated test execution, and dynamic conditional routing (`cond_route_entry`, `cond_after_review`, `cond_after_syntax_check`, `cond_should_continue`).

---

## 2. Business Flow Mermaid Diagram

```mermaid
flowchart TD
    classDef startEnd fill:#e8f5e9,stroke:#388e3c,stroke-width:2px,color:#1b5e20;
    classDef process fill:#e1f5fe,stroke:#0288d1,stroke-width:2px,color:#01579b;
    classDef review fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#f57f17;

    START(["🚀 Start Request"]):::startEnd --> ValidateInput["Validate Target Files & Parameters"]:::process

    ValidateInput --> CheckMode{"Valid Requirements?"}:::decision
    CheckMode -- "No" --> Reject["❌ Reject Request"]:::startEnd

    CheckMode -- "Yes: Existing Test Provided" --> SyntaxCheck["Verify Code Syntax"]:::process
    CheckMode -- "Yes: Description Provided" --> GenTest["Generate Test Script"]:::process

    GenTest --> HumanReview["Interactive User Test Review"]:::review

    HumanReview --> ReviewDecision{"User Choice"}:::decision
    ReviewDecision -- "Abort" --> Cancel["❌ Cancel Process"]:::startEnd
    ReviewDecision -- "Feedback Provided" --> GenTest
    ReviewDecision -- "Approved" --> SyntaxCheck

    SyntaxCheck --> RunTest["Run Automated Test Suite"]:::process

    RunTest --> TestOutcome{"All Tests Passing?"}:::decision
    TestOutcome -- "Yes" --> Success["✅ Deliver Verified Code"]:::startEnd
    TestOutcome -- "No (Under Iteration Limit)" --> FixCode["AI Generates Code Repair"]:::process
    TestOutcome -- "No (Max Iterations Reached)" --> StopLimit["⚠️ Terminate at Limit"]:::startEnd

    FixCode --> SyntaxCheck
```

---

## 3. Technical Architecture Mermaid Diagram

```mermaid
flowchart TD
    classDef stateBox fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c;
    classDef nodeBox fill:#e1f5fe,stroke:#0288d1,stroke-width:2px,color:#01579b;
    classDef condBox fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#f57f17;
    classDef startEnd fill:#e8f5e9,stroke:#388e3c,stroke-width:2px,color:#1b5e20;

    subgraph Memory["State Definition: src/state.py"]
        AgentState["Class: AgentState(TypedDict)<br/>Fields: file_path, test_path, code, test_logs,<br/>test_passed, syntax_passed, validation_passed,<br/>iterations, max_iterations, messages, review_feedback"]:::stateBox
    end

    START(["START"]):::startEnd --> node_validate_inputs

    subgraph GraphOrchestrator["Graph Definition: src/agent.py (StateGraph(AgentState))"]
        node_validate_inputs["node_validate_inputs(state: AgentState)<br/>[src/nodes/node_validate_inputs.py]"]:::nodeBox
        cond_route_entry{"cond_route_entry(state: AgentState)<br/>[src/nodes/cond_route_entry.py]"}:::condBox

        node_generate_test["node_generate_test(state: AgentState)<br/>[src/nodes/node_generate_test.py]"]:::nodeBox
        node_human_review["node_human_review(state: AgentState)<br/>[src/nodes/node_human_review.py]"]:::nodeBox
        cond_after_review{"cond_after_review(state: AgentState)<br/>[src/nodes/cond_after_review.py]"}:::condBox

        node_check_syntax["node_check_syntax(state: AgentState)<br/>[src/nodes/node_check_syntax.py]"]:::nodeBox
        cond_after_syntax_check{"cond_after_syntax_check(state: AgentState)<br/>[src/nodes/cond_after_syntax_check.py]"}:::condBox

        node_run_tests["node_run_tests(state: AgentState)<br/>[src/nodes/node_run_tests.py]"]:::nodeBox
        cond_should_continue{"cond_should_continue(state: AgentState)<br/>[src/nodes/cond_should_continue.py]"}:::condBox

        node_generate_code["node_generate_code(state: AgentState)<br/>[src/nodes/node_generate_code.py]"]:::nodeBox
    end

    node_validate_inputs --> cond_route_entry
    cond_route_entry -- "END" --> END_FAIL(["END"]):::startEnd
    cond_route_entry -- "node_generate_test" --> node_generate_test
    cond_route_entry -- "node_check_syntax" --> node_check_syntax

    node_generate_test --> node_human_review
    node_human_review --> cond_after_review
    cond_after_review -- "END" --> END_FAIL
    cond_after_review -- "node_generate_test" --> node_generate_test
    cond_after_review -- "node_check_syntax" --> node_check_syntax

    node_check_syntax --> cond_after_syntax_check
    cond_after_syntax_check -- "node_generate_code" --> node_generate_code
    cond_after_syntax_check -- "node_run_tests" --> node_run_tests

    node_generate_code --> node_check_syntax

    node_run_tests --> cond_should_continue
    cond_should_continue -- "END" --> END_SUCCESS(["END"]):::startEnd
    cond_should_continue -- "node_generate_code" --> node_generate_code
```

---

## 4. Technical & Business Logic Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor Caller as Caller / User
    participant Graph as src.agent.graph (StateGraph)
    participant Validate as node_validate_inputs()
    participant GenTest as node_generate_test()
    participant Review as node_human_review()
    participant Syntax as node_check_syntax()
    participant GenCode as node_generate_code()
    participant RunTests as node_run_tests()
    participant State as state: AgentState

    Caller->>Graph: graph.invoke(state: AgentState)
    Graph->>Validate: node_validate_inputs(state)
    Validate->>State: Update validation_passed & error_message

    rect rgb(255, 235, 238)
        alt validation_passed == False
            Validate-->>Graph: cond_route_entry() returns "END"
            Graph-->>Caller: Terminate with validation error
        end
    end

    rect rgb(255, 248, 225)
        alt has test_description (Test Generation Route)
            Graph->>GenTest: node_generate_test(state)
            GenTest->>State: Write generated test file & set test_path
            
            loop Human Review Loop
                Graph->>Review: node_human_review(state)
                Review->>Caller: Console prompt for approval/rejection feedback
                Caller-->>Review: User inputs 'y', 'exit', or feedback notes
                Review->>State: Update review_feedback
                
                alt cond_after_review() returns "END"
                    Review-->>Graph: Abort graph execution
                    Graph-->>Caller: Terminate workflow
                else cond_after_review() returns "node_generate_test"
                    Review->>GenTest: Regenerate test script using review_feedback
                end
            end
        end
    end

    rect rgb(232, 245, 233)
        loop Self-Correction Repair Loop (iterations < max_iterations)
            Graph->>Syntax: node_check_syntax(state)
            Syntax->>State: Update syntax_passed

            alt cond_after_syntax_check() returns "node_generate_code" (Syntax Error)
                Graph->>GenCode: node_generate_code(state)
                GenCode->>State: Update code & increment iterations
            else cond_after_syntax_check() returns "node_run_tests" (Syntax Valid)
                Graph->>RunTests: node_run_tests(state)
                RunTests->>State: Update test_logs & test_passed

                alt cond_should_continue() returns "END" (Tests Passed or Max Iterations Reached)
                    RunTests-->>Graph: Finish execution
                    Graph-->>Caller: Return final AgentState
                else cond_should_continue() returns "node_generate_code" (Tests Failed)
                    Graph->>GenCode: node_generate_code(state) using test_logs
                    GenCode->>State: Write code repair & increment iterations
                end
            end
        end
    end
