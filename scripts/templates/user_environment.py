"""
User & Environment Templates

Commands: echo, env, export, source, alias, which, whereis, history
"""

import random
from .base import BaseTemplateGenerator, Example


class UserEnvironmentTemplates(BaseTemplateGenerator):
    """Generate user and environment examples."""

    category = "user_environment"

    TEMPLATES = [
        {"type": "check_env_var", "difficulty": "easy", "tags": ["env", "variable"]},
        {"type": "set_env_var", "difficulty": "easy", "tags": ["export", "variable"]},
        {"type": "find_command", "difficulty": "easy", "tags": ["which", "whereis"]},
        {"type": "show_path", "difficulty": "easy", "tags": ["path", "env"]},
        {"type": "create_alias", "difficulty": "medium", "tags": ["alias", "shortcut"]},
        {"type": "source_config", "difficulty": "medium", "tags": ["source", "config"]},
        {"type": "view_history", "difficulty": "medium", "tags": ["history", "commands"]},
        {"type": "setup_environment", "difficulty": "hard", "tags": ["env", "setup"]},
    ]

    def generate(self, example_id: str) -> Example:
        template = random.choice(self.TEMPLATES)
        method_name = f"_gen_{template['type']}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(example_id, template)
        return self._gen_check_env_var(example_id, template)

    def _gen_check_env_var(self, example_id: str, template: dict) -> Example:
        var_name = random.choice(["HOME", "USER", "PATH", "SHELL", "LANG", "EDITOR", "NODE_ENV", "PYTHONPATH"])

        requests = [
            f"What is my {var_name} set to?",
            f"echo ${var_name}",
            f"Check the {var_name} environment variable",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"echo ${var_name}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        values = {
            "HOME": f"/home/{self.var.username()}",
            "USER": self.var.username(),
            "PATH": "/usr/local/bin:/usr/bin:/bin:/usr/local/sbin",
            "SHELL": random.choice(["/bin/bash", "/bin/zsh"]),
            "LANG": "en_US.UTF-8",
            "EDITOR": random.choice(["vim", "nano", "code"]),
            "NODE_ENV": random.choice(["development", "production"]),
            "PYTHONPATH": f"/home/{self.var.username()}/.local/lib/python3.10",
        }
        output = values.get(var_name, f"value_of_{var_name}")
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"The `{var_name}` environment variable is set to:\n\n```\n{output}\n```"
        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["echo"], "easy", template["tags"])

    def _gen_set_env_var(self, example_id: str, template: dict) -> Example:
        var_name = random.choice(["NODE_ENV", "DEBUG", "API_KEY", "DATABASE_URL", "LOG_LEVEL"])
        var_value = random.choice(["production", "true", "my-secret-key", "postgres://localhost/db", "info"])

        requests = [
            f"Set {var_name} to {var_value}",
            f"export {var_name}={var_value}",
            f"I need {var_name} environment variable set",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"export {var_name}='{var_value}'"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)
        conversations.append(self.create_tool_result(tool_id, ""))

        # Verify
        cmd2 = f"echo ${var_name}"
        tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
        conversations.append(tool_msg2)
        conversations.append(self.create_tool_result(tool_id2, var_value))

        response = f"Set `{var_name}={var_value}` for this session.\n\nNote: This is temporary. To make it permanent, add it to your `~/.bashrc` or `~/.zshrc`."
        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["export", "echo"], "easy", template["tags"])

    def _gen_find_command(self, example_id: str, template: dict) -> Example:
        command = random.choice(["python", "node", "git", "docker", "npm", "pip", "java", "go"])

        requests = [
            f"Where is {command} installed?",
            f"which {command}",
            f"Find the {command} executable",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"which {command}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        paths = {
            "python": "/usr/bin/python3",
            "node": "/usr/bin/node",
            "git": "/usr/bin/git",
            "docker": "/usr/bin/docker",
            "npm": "/usr/bin/npm",
            "pip": f"/home/{self.var.username()}/.local/bin/pip",
            "java": "/usr/bin/java",
            "go": "/usr/local/go/bin/go",
        }
        output = paths.get(command, f"/usr/bin/{command}")
        conversations.append(self.create_tool_result(tool_id, output))

        # Also check version
        cmd2 = f"{command} --version 2>/dev/null || {command} -version 2>/dev/null | head -1"
        tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
        conversations.append(tool_msg2)

        versions = {
            "python": f"Python 3.{random.randint(8, 11)}.{random.randint(0, 10)}",
            "node": f"v{random.randint(16, 20)}.{random.randint(0, 20)}.{random.randint(0, 5)}",
            "git": f"git version 2.{random.randint(30, 40)}.{random.randint(0, 5)}",
            "docker": f"Docker version {random.randint(20, 24)}.{random.randint(0, 10)}.{random.randint(0, 5)}",
        }
        output2 = versions.get(command, f"{command} version 1.0.0")
        conversations.append(self.create_tool_result(tool_id2, output2))

        response = f"`{command}` is installed at `{output}`\n\n**Version**: {output2}"
        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["which", command], "easy", template["tags"])

    def _gen_show_path(self, example_id: str, template: dict) -> Example:
        requests = [
            "Show my PATH",
            "echo $PATH",
            "What directories are in my PATH?",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = "echo $PATH | tr ':' '\\n'"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        paths = [
            f"/home/{self.var.username()}/.local/bin",
            "/usr/local/bin",
            "/usr/bin",
            "/bin",
            "/usr/local/sbin",
            "/usr/sbin",
            f"/home/{self.var.username()}/.npm-global/bin",
        ]
        output = "\n".join(paths)
        conversations.append(self.create_tool_result(tool_id, output))

        response = "Your PATH contains these directories (in order of priority):\n\n"
        for i, p in enumerate(paths, 1):
            response += f"{i}. `{p}`\n"
        response += "\nCommands are searched in this order."

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["echo", "tr"], "easy", template["tags"], uses_pipes=True)

    def _gen_create_alias(self, example_id: str, template: dict) -> Example:
        aliases = [
            ("ll", "ls -la"),
            ("la", "ls -A"),
            ("gs", "git status"),
            ("gp", "git push"),
            ("dc", "docker-compose"),
            ("py", "python3"),
            ("update", "sudo apt update && sudo apt upgrade -y"),
        ]
        alias_name, alias_cmd = random.choice(aliases)

        requests = [
            f"Create an alias '{alias_name}' for '{alias_cmd}'",
            f"alias {alias_name}='{alias_cmd}'",
            f"Make a shortcut called {alias_name}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"alias {alias_name}='{alias_cmd}'"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)
        conversations.append(self.create_tool_result(tool_id, ""))

        # Make it permanent
        cmd2 = f"echo \"alias {alias_name}='{alias_cmd}'\" >> ~/.bashrc"
        tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
        conversations.append(tool_msg2)
        conversations.append(self.create_tool_result(tool_id2, ""))

        response = f"""Created alias `{alias_name}` → `{alias_cmd}`

- Available immediately in this session
- Added to `~/.bashrc` for persistence

You can now use `{alias_name}` instead of typing `{alias_cmd}`."""

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["alias", "echo"], "medium", template["tags"])

    def _gen_source_config(self, example_id: str, template: dict) -> Example:
        config_file = random.choice(["~/.bashrc", "~/.zshrc", ".env", "~/.profile", "venv/bin/activate"])

        requests = [
            f"Load {config_file}",
            f"source {config_file}",
            f"Reload my shell config",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"source {config_file}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)
        conversations.append(self.create_tool_result(tool_id, ""))

        if "venv" in config_file:
            response = f"Activated the virtual environment. Your Python commands will now use the venv."
        elif ".env" in config_file:
            response = f"Loaded environment variables from `.env`. They're now available in this session."
        else:
            response = f"Reloaded `{config_file}`. Any new aliases, functions, or environment variables are now active."

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["source"], "medium", template["tags"])

    def _gen_view_history(self, example_id: str, template: dict) -> Example:
        search_term = random.choice([None, "git", "docker", "ssh", "pip"])

        if search_term:
            requests = [
                f"Show my recent {search_term} commands",
                f"history | grep {search_term}",
                f"What {search_term} commands did I run?",
            ]
            cmd = f"history | grep {search_term} | tail -10"
        else:
            requests = [
                "Show my command history",
                "history",
                "What commands did I run recently?",
            ]
            cmd = "history | tail -15"

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        if search_term:
            commands = [f"{search_term} {random.choice(['status', 'pull', 'push', 'log', 'diff'])}" for _ in range(5)]
        else:
            commands = ["ls -la", "cd projects", "git status", "npm install", "python app.py"]

        output = "\n".join([f"  {1000 + i}  {c}" for i, c in enumerate(commands)])
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Here are your recent{' ' + search_term if search_term else ''} commands:\n\n"
        for c in commands:
            response += f"- `{c}`\n"

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["history", "grep", "tail"], "medium", template["tags"], uses_pipes=True)

    def _gen_setup_environment(self, example_id: str, template: dict) -> Example:
        project_type = random.choice(["python", "node", "go"])

        requests = [
            f"Set up my environment for {project_type} development",
            f"Configure environment variables for {project_type}",
            f"Initialize my {project_type} dev environment",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        if project_type == "python":
            response = "I'll set up a Python development environment with virtual env and common variables."
            conversations.append(self.create_assistant_message(response))

            # Create venv
            cmd = "python3 -m venv venv"
            tool_msg, tool_id = self.create_tool_call_message(cmd)
            conversations.append(tool_msg)
            conversations.append(self.create_tool_result(tool_id, ""))

            # Activate and set vars
            cmd2 = "source venv/bin/activate && export PYTHONDONTWRITEBYTECODE=1 && export PYTHONUNBUFFERED=1"
            tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
            conversations.append(tool_msg2)
            conversations.append(self.create_tool_result(tool_id2, ""))

            final_response = """Python environment ready:

- Virtual environment: `./venv` (activated)
- `PYTHONDONTWRITEBYTECODE=1` - No .pyc files
- `PYTHONUNBUFFERED=1` - Unbuffered output

Install dependencies with: `pip install -r requirements.txt`"""

        elif project_type == "node":
            response = "I'll set up a Node.js development environment."
            conversations.append(self.create_assistant_message(response))

            cmd = "export NODE_ENV=development && export DEBUG='app:*'"
            tool_msg, tool_id = self.create_tool_call_message(cmd)
            conversations.append(tool_msg)
            conversations.append(self.create_tool_result(tool_id, ""))

            cmd2 = "npm install"
            tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
            conversations.append(tool_msg2)
            conversations.append(self.create_tool_result(tool_id2, f"added {random.randint(50, 200)} packages in 5s"))

            final_response = """Node.js environment ready:

- `NODE_ENV=development`
- `DEBUG=app:*` - Debug logging enabled
- Dependencies installed

Run with: `npm start` or `npm run dev`"""

        else:  # go
            response = "I'll set up a Go development environment."
            conversations.append(self.create_assistant_message(response))

            cmd = "export GOPATH=$HOME/go && export PATH=$PATH:$GOPATH/bin"
            tool_msg, tool_id = self.create_tool_call_message(cmd)
            conversations.append(tool_msg)
            conversations.append(self.create_tool_result(tool_id, ""))

            cmd2 = "go mod tidy"
            tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
            conversations.append(tool_msg2)
            conversations.append(self.create_tool_result(tool_id2, ""))

            final_response = """Go environment ready:

- `GOPATH=$HOME/go`
- Go binaries added to PATH
- Dependencies synced with `go mod tidy`

Build with: `go build` or run with: `go run .`"""

        conversations.append(self.create_assistant_message(final_response))

        return self.build_example(example_id, conversations, ["export", "source"], "hard", template["tags"])
