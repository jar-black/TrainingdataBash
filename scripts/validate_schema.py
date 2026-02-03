#!/usr/bin/env python3
"""
Validate training examples against the JSON schema.
"""

import json
import sys
from pathlib import Path
from typing import List, Tuple

try:
    import jsonschema
    from jsonschema import validate, ValidationError
except ImportError:
    print("Installing jsonschema...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "jsonschema", "-q"])
    import jsonschema
    from jsonschema import validate, ValidationError


def load_schema(schema_path: str) -> dict:
    """Load the JSON schema."""
    with open(schema_path, 'r') as f:
        return json.load(f)


def validate_jsonl_file(file_path: str, schema: dict) -> Tuple[int, int, List[str]]:
    """
    Validate all examples in a JSONL file.

    Returns:
        Tuple of (valid_count, invalid_count, error_messages)
    """
    valid = 0
    invalid = 0
    errors = []

    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                example = json.loads(line)
                validate(instance=example, schema=schema)
                valid += 1
            except json.JSONDecodeError as e:
                invalid += 1
                errors.append(f"  Line {line_num}: JSON parse error - {e}")
            except ValidationError as e:
                invalid += 1
                errors.append(f"  Line {line_num} (id={example.get('id', 'unknown')}): {e.message}")

    return valid, invalid, errors


def main():
    """Main validation function."""
    project_root = Path(__file__).parent.parent
    schema_path = project_root / "schema" / "tool_call_schema.json"
    data_dir = project_root / "data" / "raw"

    print("=" * 60)
    print("Bash Tool-Calling Dataset Schema Validator")
    print("=" * 60)

    # Load schema
    print(f"\nLoading schema from: {schema_path}")
    schema = load_schema(schema_path)
    print("Schema loaded successfully!\n")

    # Find all JSONL files
    jsonl_files = list(data_dir.rglob("*.jsonl"))

    if not jsonl_files:
        print("No JSONL files found in data/raw/")
        return 1

    print(f"Found {len(jsonl_files)} JSONL file(s) to validate:\n")

    total_valid = 0
    total_invalid = 0
    all_passed = True

    for file_path in sorted(jsonl_files):
        rel_path = file_path.relative_to(project_root)
        print(f"Validating: {rel_path}")

        valid, invalid, errors = validate_jsonl_file(file_path, schema)
        total_valid += valid
        total_invalid += invalid

        if invalid > 0:
            all_passed = False
            print(f"  ❌ {valid} valid, {invalid} invalid")
            for error in errors:
                print(error)
        else:
            print(f"  ✓ {valid} examples valid")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total examples validated: {total_valid + total_invalid}")
    print(f"  Valid:   {total_valid}")
    print(f"  Invalid: {total_invalid}")

    if all_passed:
        print("\n✓ All examples passed validation!")
        return 0
    else:
        print("\n❌ Some examples failed validation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
