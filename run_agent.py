import os
import argparse
from dotenv import load_dotenv

# Load env variables
load_dotenv()

from src.agent import graph

def main():
    parser = argparse.ArgumentParser(description="Run the Test-Led Python Coder Agent.")
    parser.add_argument(
        "--file", 
        required=True, 
        help="Path to the target Python code file you want the agent to fix."
    )
    parser.add_argument(
        "--test", 
        help="Optional path to an existing pytest file. If not provided, --description must be set."
    )
    parser.add_argument(
        "--description", 
        help="Optional description of the test requirements to generate a test file."
    )
    parser.add_argument(
        "--max-iterations", 
        type=int, 
        default=3, 
        help="Maximum loop iterations for self-correction (default: 3)."
    )

    args = parser.parse_args()

    inputs = {
        "file_path": args.file,
        "test_path": args.test,
        "test_description": args.description,
        "max_iterations": args.max_iterations,
        "iterations": 0,
        "messages": [],
    }

    print(f"Invoking agent on file: {args.file}")
    output = graph.invoke(inputs)

    # Output results
    print("\n" + "=" * 60)
    print("                    AGENT EXECUTION SUMMARY")
    print("=" * 60)
    if not output.get("validation_passed", True):
        print(f"❌ Input Validation Failed: {output.get('error_message')}")
        return

    print(f"Target File: {output.get('file_path')}")
    print(f"Test File: {output.get('test_path')}")
    print(f"Syntax Passed: {output.get('syntax_passed')}")
    print(f"Tests Passed: {output.get('test_passed')}")
    print(f"Total Iterations Run: {output.get('iterations')}")
    print("=" * 60)

if __name__ == "__main__":
    main()
