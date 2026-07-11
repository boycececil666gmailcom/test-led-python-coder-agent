import os
from TestCoding.state import AgentState

def node_human_review(state: AgentState) -> dict:
    """Pause execution and prompt the user to approve or give feedback on the generated test script."""
    test_path = state.get("test_path")
    
    # Read and print the generated test code
    test_code = ""
    if test_path and os.path.exists(test_path):
        with open(test_path, "r", encoding="utf-8") as f:
            test_code = f.read()

    print("\n" + "=" * 60)
    print("                    GENERATED TEST SCRIPT REVIEW")
    print("=" * 60)
    print(f"Path: {test_path}\n")
    print(test_code)
    print("=" * 60)

    # Prompt loop for user input
    while True:
        user_input = input(
            "\nDo you want to run this test? (y/Enter to approve, 'exit' to abort, or type your feedback to modify the test): "
        ).strip()
        
        if user_input.lower() in ["y", "yes", ""]:
            print("Test approved. Proceeding with execution...")
            return {"review_feedback": None}
        elif user_input.lower() == "exit":
            print("Execution aborted by user.")
            return {"review_feedback": "exit"}
        elif user_input:
            print(f"Feedback received: '{user_input}'. Regenerating test...")
            return {"review_feedback": user_input}
        else:
            print("Please enter 'y'/Enter, 'exit', or type some feedback to modify.")
