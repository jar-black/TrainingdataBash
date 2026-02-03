#!/usr/bin/env python3
"""
Merge all generated JSONL files into train and validation sets.
"""

import json
import random
import argparse
from pathlib import Path
from typing import List


def load_jsonl(filepath: Path) -> List[dict]:
    """Load examples from a JSONL file."""
    examples = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                examples.append(json.loads(line))
    return examples


def save_jsonl(filepath: Path, examples: List[dict]):
    """Save examples to a JSONL file."""
    with open(filepath, 'w') as f:
        for example in examples:
            f.write(json.dumps(example) + '\n')


def main():
    parser = argparse.ArgumentParser(description="Merge JSONL files into train/val splits")
    parser.add_argument("--input-dir", default="data/generated",
                        help="Directory containing generated JSONL files")
    parser.add_argument("--output-dir", default="data/processed",
                        help="Output directory for merged files")
    parser.add_argument("--train-split", type=float, default=0.95,
                        help="Fraction of data for training (default: 0.95)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")

    args = parser.parse_args()
    random.seed(args.seed)

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all JSONL files
    jsonl_files = list(input_dir.glob("*.jsonl"))

    if not jsonl_files:
        print(f"No JSONL files found in {input_dir}")
        return 1

    print(f"Found {len(jsonl_files)} JSONL files")

    # Load all examples
    all_examples = []
    for filepath in jsonl_files:
        if filepath.name in ("train_dataset.jsonl", "val_dataset.jsonl"):
            continue  # Skip already merged files
        examples = load_jsonl(filepath)
        print(f"  {filepath.name}: {len(examples)} examples")
        all_examples.extend(examples)

    print(f"\nTotal examples: {len(all_examples)}")

    # Shuffle
    random.shuffle(all_examples)

    # Split
    split_idx = int(len(all_examples) * args.train_split)
    train_examples = all_examples[:split_idx]
    val_examples = all_examples[split_idx:]

    # Save
    train_file = output_dir / "train_dataset.jsonl"
    val_file = output_dir / "val_dataset.jsonl"

    save_jsonl(train_file, train_examples)
    save_jsonl(val_file, val_examples)

    print(f"\nSaved:")
    print(f"  Training:   {len(train_examples)} examples -> {train_file}")
    print(f"  Validation: {len(val_examples)} examples -> {val_file}")

    # Stats
    print("\n--- Statistics ---")
    categories = {}
    difficulties = {}

    for ex in all_examples:
        meta = ex.get("metadata", {})
        cat = meta.get("category", "unknown")
        diff = meta.get("difficulty", "unknown")

        categories[cat] = categories.get(cat, 0) + 1
        difficulties[diff] = difficulties.get(diff, 0) + 1

    print("\nBy category:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")

    print("\nBy difficulty:")
    for diff, count in sorted(difficulties.items()):
        print(f"  {diff}: {count}")

    return 0


if __name__ == "__main__":
    exit(main())
