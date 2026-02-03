#!/usr/bin/env python3
"""
Bash Tool-Calling Dataset Generator

Generates training examples for teaching LLMs to use bash tool calling.
"""

import json
import random
import uuid
import argparse
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from abc import ABC, abstractmethod
import re
from datetime import datetime, timedelta


@dataclass
class ToolCall:
    """Represents a tool call."""
    id: str
    type: str = "function"
    function: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def create_bash_call(cls, command: str) -> "ToolCall":
        return cls(
            id=f"call_{uuid.uuid4().hex[:8]}",
            type="function",
            function={
                "name": "bash",
                "arguments": json.dumps({"command": command})
            }
        )


@dataclass
class Message:
    """Represents a conversation message."""
    role: str
    content: Optional[str] = None
    tool_calls: Optional[List[Dict]] = None
    tool_call_id: Optional[str] = None

    def to_dict(self) -> Dict:
        result = {"role": self.role}
        if self.content is not None:
            result["content"] = self.content
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls
            result["content"] = None
        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id
        return result


@dataclass
class Example:
    """Represents a training example."""
    id: str
    conversations: List[Message]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "conversations": [msg.to_dict() for msg in self.conversations],
            "metadata": self.metadata
        }


class VariableGenerator:
    """Generates random variables for templates."""

    def __init__(self, config: Dict):
        self.config = config
        self.vars = config.get("variables", {})

    def username(self) -> str:
        return random.choice(self.vars.get("usernames", ["user"]))

    def project_name(self) -> str:
        return random.choice(self.vars.get("project_names", ["myproject"]))

    def directory(self) -> str:
        return random.choice(self.vars.get("directories", ["src"]))

    def git_branch(self) -> str:
        return random.choice(self.vars.get("git_branches", ["main"]))

    def python_package(self) -> str:
        return random.choice(self.vars.get("package_names", {}).get("python", ["requests"]))

    def node_package(self) -> str:
        return random.choice(self.vars.get("package_names", {}).get("node", ["express"]))

    def code_extension(self) -> str:
        return random.choice(self.vars.get("file_extensions", {}).get("code", [".py"]))

    def config_extension(self) -> str:
        return random.choice(self.vars.get("file_extensions", {}).get("config", [".yaml"]))

    def random_filename(self, ext: str = None) -> str:
        names = ["main", "app", "index", "utils", "helpers", "config", "server", "client", "test", "data"]
        ext = ext or self.code_extension()
        return random.choice(names) + ext

    def random_path(self, depth: int = None) -> str:
        depth = depth or random.randint(1, 3)
        parts = [random.choice(self.vars.get("directories", ["src"])) for _ in range(depth)]
        return "/".join(parts)

    def random_size(self, unit: str = "M") -> str:
        if unit == "K":
            return f"{random.randint(1, 999)}K"
        elif unit == "M":
            return f"{random.randint(1, 500)}M"
        elif unit == "G":
            return f"{random.uniform(0.1, 10):.1f}G"
        return f"{random.randint(1, 100)}{unit}"

    def random_date(self, days_ago_max: int = 30) -> str:
        days = random.randint(0, days_ago_max)
        date = datetime.now() - timedelta(days=days)
        return date.strftime("%Y-%m-%d")

    def random_time(self) -> str:
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        return f"{hour:02d}:{minute:02d}:{second:02d}"

    def random_ip(self) -> str:
        return f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"

    def random_port(self) -> int:
        return random.choice([80, 443, 3000, 5000, 8000, 8080, 8443, 9000, 5432, 3306, 6379, 27017])

    def random_pid(self) -> int:
        return random.randint(1000, 65535)

    def random_commit_hash(self, short: bool = True) -> str:
        full = uuid.uuid4().hex[:40]
        return full[:7] if short else full


class OutputGenerator:
    """Generates realistic command outputs."""

    def __init__(self, var_gen: VariableGenerator):
        self.var = var_gen

    def ls_output(self, num_files: int = 5, show_hidden: bool = False) -> str:
        lines = []
        if show_hidden:
            lines.append("total " + str(random.randint(20, 200)))
            lines.append(f"drwxr-xr-x  {random.randint(2,10)} {self.var.username()} {self.var.username()}  4096 {self.var.random_date()} {self.var.random_time()[:5]} .")
            lines.append(f"drwxr-xr-x  {random.randint(2,10)} {self.var.username()} {self.var.username()}  4096 {self.var.random_date()} {self.var.random_time()[:5]} ..")

        for _ in range(num_files):
            is_dir = random.random() < 0.3
            perms = "drwxr-xr-x" if is_dir else "-rw-r--r--"
            links = random.randint(1, 5) if is_dir else 1
            size = random.randint(100, 50000)
            name = self.var.directory() if is_dir else self.var.random_filename()
            lines.append(f"{perms}  {links} {self.var.username()} {self.var.username()} {size:>6} {self.var.random_date()} {self.var.random_time()[:5]} {name}")

        return "\n".join(lines)

    def find_output(self, pattern: str = "*.py", num_results: int = 5) -> str:
        ext = pattern.replace("*", "")
        results = []
        for _ in range(num_results):
            path = self.var.random_path(random.randint(1, 3))
            filename = self.var.random_filename(ext)
            results.append(f"./{path}/{filename}")
        return "\n".join(results)

    def grep_output(self, pattern: str, num_matches: int = 4) -> str:
        lines = []
        for i in range(num_matches):
            path = f"./{self.var.random_path()}/{self.var.random_filename()}"
            line_num = random.randint(1, 200)
            lines.append(f"{path}:{line_num}:    # {pattern} - some matching content here")
        return "\n".join(lines)

    def du_output(self, num_dirs: int = 5) -> str:
        lines = []
        for _ in range(num_dirs):
            size = self.var.random_size(random.choice(["K", "M", "G"]))
            path = f"./{self.var.random_path()}"
            lines.append(f"{size}\t{path}")
        return "\n".join(sorted(lines, key=lambda x: -self._parse_size(x.split()[0])))

    def _parse_size(self, size_str: str) -> float:
        multipliers = {"K": 1, "M": 1024, "G": 1024*1024}
        num = float(size_str[:-1])
        unit = size_str[-1]
        return num * multipliers.get(unit, 1)

    def ps_output(self, num_procs: int = 5) -> str:
        lines = ["  PID TTY          TIME CMD"]
        commands = ["bash", "python", "node", "vim", "top", "ssh", "git", "docker"]
        for _ in range(num_procs):
            pid = self.var.random_pid()
            tty = random.choice(["pts/0", "pts/1", "pts/2", "?"])
            time = f"00:{random.randint(0,59):02d}:{random.randint(0,59):02d}"
            cmd = random.choice(commands)
            lines.append(f"{pid:>5} {tty:<8} {time} {cmd}")
        return "\n".join(lines)

    def git_status_output(self, modified: int = 2, untracked: int = 1) -> str:
        lines = [f"On branch {self.var.git_branch()}"]
        if modified > 0:
            lines.append("Changes not staged for commit:")
            lines.append('  (use "git add <file>..." to update what will be committed)')
            lines.append("")
            for _ in range(modified):
                lines.append(f"\tmodified:   {self.var.random_path()}/{self.var.random_filename()}")
        if untracked > 0:
            lines.append("")
            lines.append("Untracked files:")
            lines.append('  (use "git add <file>..." to include in what will be committed)')
            lines.append("")
            for _ in range(untracked):
                lines.append(f"\t{self.var.random_path()}/{self.var.random_filename()}")
        return "\n".join(lines)

    def git_log_output(self, num_commits: int = 3) -> str:
        lines = []
        messages = [
            "Fix bug in authentication",
            "Add new feature",
            "Update dependencies",
            "Refactor code",
            "Add tests",
            "Update documentation",
            "Fix typo",
            "Improve performance",
        ]
        for _ in range(num_commits):
            hash = self.var.random_commit_hash()
            msg = random.choice(messages)
            lines.append(f"{hash} {msg}")
        return "\n".join(lines)

    def curl_download_output(self, size_mb: float = 5.0) -> str:
        return f"""  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 {size_mb:.1f}M  100 {size_mb:.1f}M    0     0  {random.uniform(1,10):.1f}M      0 --:--:-- --:--:-- --:--:-- {random.uniform(1,10):.1f}M"""

    def pip_install_output(self, package: str) -> str:
        version = f"{random.randint(1,5)}.{random.randint(0,20)}.{random.randint(0,10)}"
        return f"""Collecting {package}
  Downloading {package}-{version}-py3-none-any.whl ({random.randint(10, 500)} kB)
Installing collected packages: {package}
Successfully installed {package}-{version}"""

    def error_permission_denied(self, path: str) -> str:
        return f"Permission denied: '{path}'"

    def error_file_not_found(self, path: str) -> str:
        return f"No such file or directory: '{path}'"


class TaskTemplate(ABC):
    """Base class for task templates."""

    def __init__(self, var_gen: VariableGenerator, out_gen: OutputGenerator):
        self.var = var_gen
        self.out = out_gen

    @abstractmethod
    def generate(self) -> Example:
        """Generate an example from this template."""
        pass

    def get_system_prompt(self, config: Dict) -> str:
        prompts = config.get("system_prompts", [
            "You are a helpful assistant with access to a bash tool for executing commands on a Linux system."
        ])
        return random.choice(prompts)

    def create_tool_call_message(self, command: str) -> tuple:
        """Create assistant message with tool call and return (message, tool_call_id)."""
        tool_call = ToolCall.create_bash_call(command)
        msg = Message(
            role="assistant",
            content=None,
            tool_calls=[asdict(tool_call)]
        )
        return msg, tool_call.id

    def create_tool_result(self, tool_call_id: str, output: str) -> Message:
        """Create tool result message."""
        return Message(role="tool", content=output, tool_call_id=tool_call_id)


# Import all category templates
from templates import (
    FileOperationsTemplates,
    TextProcessingTemplates,
    GitTemplates,
    SystemInfoTemplates,
    NetworkTemplates,
    ArchiveTemplates,
    PackageManagementTemplates,
    PermissionsTemplates,
    UserEnvironmentTemplates,
    MixedComplexTemplates,
)


class DatasetGenerator:
    """Main dataset generator."""

    def __init__(self, config_path: str):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        self.var_gen = VariableGenerator(self.config)
        self.out_gen = OutputGenerator(self.var_gen)

        # Initialize template generators for each category
        self.templates = {
            "file_operations": FileOperationsTemplates(self.var_gen, self.out_gen, self.config),
            "text_processing": TextProcessingTemplates(self.var_gen, self.out_gen, self.config),
            "git": GitTemplates(self.var_gen, self.out_gen, self.config),
            "system_info": SystemInfoTemplates(self.var_gen, self.out_gen, self.config),
            "network": NetworkTemplates(self.var_gen, self.out_gen, self.config),
            "archive": ArchiveTemplates(self.var_gen, self.out_gen, self.config),
            "package_management": PackageManagementTemplates(self.var_gen, self.out_gen, self.config),
            "permissions": PermissionsTemplates(self.var_gen, self.out_gen, self.config),
            "user_environment": UserEnvironmentTemplates(self.var_gen, self.out_gen, self.config),
            "mixed_complex": MixedComplexTemplates(self.var_gen, self.out_gen, self.config),
        }

    def generate_category(self, category: str, count: int) -> List[Example]:
        """Generate examples for a specific category."""
        if category not in self.templates:
            raise ValueError(f"Unknown category: {category}")

        template_gen = self.templates[category]
        examples = []

        for i in range(count):
            try:
                example = template_gen.generate(f"{category}_{i:05d}")
                examples.append(example)
            except Exception as e:
                print(f"Error generating {category} example {i}: {e}")
                continue

        return examples

    def generate_all(self, output_dir: str):
        """Generate all examples according to distribution config."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        distribution = self.config.get("distribution", {})
        all_examples = []

        for category, count in distribution.items():
            print(f"Generating {count} examples for {category}...")
            examples = self.generate_category(category, count)
            all_examples.extend(examples)

            # Save category-specific file
            cat_file = output_path / f"{category}.jsonl"
            with open(cat_file, 'w') as f:
                for ex in examples:
                    f.write(json.dumps(ex.to_dict()) + "\n")
            print(f"  Saved {len(examples)} to {cat_file}")

        # Shuffle all examples
        random.shuffle(all_examples)

        # Split into train/validation
        train_split = self.config.get("dataset", {}).get("train_split", 0.95)
        split_idx = int(len(all_examples) * train_split)

        train_examples = all_examples[:split_idx]
        val_examples = all_examples[split_idx:]

        # Save merged files
        train_file = output_path / "train_dataset.jsonl"
        val_file = output_path / "val_dataset.jsonl"

        with open(train_file, 'w') as f:
            for ex in train_examples:
                f.write(json.dumps(ex.to_dict()) + "\n")

        with open(val_file, 'w') as f:
            for ex in val_examples:
                f.write(json.dumps(ex.to_dict()) + "\n")

        print(f"\nGeneration complete!")
        print(f"  Train: {len(train_examples)} examples -> {train_file}")
        print(f"  Val:   {len(val_examples)} examples -> {val_file}")
        print(f"  Total: {len(all_examples)} examples")

        return all_examples


def main():
    parser = argparse.ArgumentParser(description="Generate bash tool-calling dataset")
    parser.add_argument("--config", default="configs/generation_config.yaml",
                        help="Path to generation config")
    parser.add_argument("--output", default="data/generated",
                        help="Output directory")
    parser.add_argument("--category", help="Generate only specific category")
    parser.add_argument("--count", type=int, help="Override count for category")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")

    args = parser.parse_args()

    random.seed(args.seed)

    generator = DatasetGenerator(args.config)

    if args.category:
        count = args.count or generator.config["distribution"].get(args.category, 100)
        examples = generator.generate_category(args.category, count)
        output_path = Path(args.output)
        output_path.mkdir(parents=True, exist_ok=True)
        with open(output_path / f"{args.category}.jsonl", 'w') as f:
            for ex in examples:
                f.write(json.dumps(ex.to_dict()) + "\n")
        print(f"Generated {len(examples)} examples for {args.category}")
    else:
        generator.generate_all(args.output)


if __name__ == "__main__":
    main()
