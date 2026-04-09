import ast
import os
from typing import Dict, List, Any


def get_function_complexity(node: ast.AST) -> int:
    """
    Calculates the cyclomatic complexity of a function node.
    Complexity starts at 1 and increases for every decision point.
    """
    complexity = 1
    for child in ast.walk(node):
        # Decision points in Python AST
        if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor, 
                               ast.IfExp, ast.With, ast.AsyncWith,
                               ast.ExceptHandler)):
            complexity += 1
        elif isinstance(child, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            # and/or operations: each additional value adds complexity
            complexity += len(child.values) - 1
    return complexity


def analyze_directory_complexity(dir_path: str) -> List[Dict[str, Any]]:
    """
    Analyzes all Python files in a directory (recursively) and returns a list of
    summaries for each function found, including its location, lines of code, and complexity.
    """
    results = []

    for root, _, files in os.walk(dir_path):
        for file in files:
            if not file.endswith('.py'):
                continue

            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # Lines of code (including docstrings and comments)
                        loc = 1
                        if hasattr(node, 'end_lineno') and node.end_lineno:
                            loc = node.end_lineno - node.lineno + 1
                        
                        results.append({
                            "file": os.path.relpath(file_path, dir_path),
                            "function": node.name,
                            "line_start": node.lineno,
                            "loc": loc,
                            "complexity": get_function_complexity(node)
                        })
            except (SyntaxError, UnicodeDecodeError, PermissionError):
                # Skip files that cannot be parsed or read
                continue

    return results


def test_tool():
    """
    Simple test function to verify complexity and LOC analysis.
    """
    test_code = """
def simple_func(x):
    return x + 1

def complex_func(x):
    if x > 0:
        for i in range(x):
            print(i)
    elif x < 0:
        return -x
    else:
        return 0
    return [i for i in range(5) if i % 2 == 0]
"""
    # Create a temporary test file
    test_file = "complexity_test_sample.py"
    with open(test_file, "w") as f:
        f.write(test_code)

    try:
        # Analyze current directory
        analysis = analyze_directory_complexity(".")
        
        # Filter for our test file
        test_results = [r for r in analysis if r["file"] == test_file]
        
        print(f"Analysis of {test_file}:")
        for res in test_results:
            print(f"  Function: {res['function']}")
            print(f"    LOC: {res['loc']}")
            print(f"    Complexity: {res['complexity']}")
            
        # Basic assertions
        simple = next(r for r in test_results if r["function"] == "simple_func")
        complex_ = next(r for r in test_results if r["function"] == "complex_func")
        
        assert simple["complexity"] == 1
        assert complex_["complexity"] > 1
        print("\nTest passed successfully!")

    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


if __name__ == "__main__":
    test_tool()