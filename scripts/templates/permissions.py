"""
File Permissions & Ownership Templates

Commands: chmod, chown, chgrp, umask, id
"""

import random
from .base import BaseTemplateGenerator, Example


class PermissionsTemplates(BaseTemplateGenerator):
    """Generate permissions and ownership examples."""

    category = "permissions"

    TEMPLATES = [
        {"type": "make_executable", "difficulty": "easy", "tags": ["chmod", "executable"]},
        {"type": "change_permissions", "difficulty": "easy", "tags": ["chmod"]},
        {"type": "check_permissions", "difficulty": "easy", "tags": ["ls", "permissions"]},
        {"type": "change_owner", "difficulty": "medium", "tags": ["chown", "ownership"]},
        {"type": "recursive_chmod", "difficulty": "medium", "tags": ["chmod", "recursive"]},
        {"type": "fix_permissions", "difficulty": "hard", "tags": ["chmod", "chown", "fix"]},
        {"type": "secure_file", "difficulty": "hard", "tags": ["chmod", "security"]},
    ]

    def generate(self, example_id: str) -> Example:
        template = random.choice(self.TEMPLATES)
        method_name = f"_gen_{template['type']}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(example_id, template)
        return self._gen_make_executable(example_id, template)

    def _gen_make_executable(self, example_id: str, template: dict) -> Example:
        script = random.choice(["deploy.sh", "start.sh", "backup.sh", "run.py", "build.sh"])

        requests = [
            f"Make {script} executable",
            f"chmod +x {script}",
            f"I can't run {script}, fix permissions",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        # Check current permissions
        cmd = f"ls -l {script}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        output = f"-rw-r--r-- 1 {self.var.username()} {self.var.username()} 1234 {self.var.random_date()} {script}"
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"The script doesn't have execute permission. Let me fix that."
        conversations.append(self.create_assistant_message(response))

        # Make executable
        cmd2 = f"chmod +x {script}"
        tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
        conversations.append(tool_msg2)
        conversations.append(self.create_tool_result(tool_id2, ""))

        # Verify
        cmd3 = f"ls -l {script}"
        tool_msg3, tool_id3 = self.create_tool_call_message(cmd3)
        conversations.append(tool_msg3)

        output3 = f"-rwxr-xr-x 1 {self.var.username()} {self.var.username()} 1234 {self.var.random_date()} {script}"
        conversations.append(self.create_tool_result(tool_id3, output3))

        response2 = f"`{script}` is now executable. You can run it with `./{script}`"
        conversations.append(self.create_assistant_message(response2))

        return self.build_example(example_id, conversations, ["ls", "chmod"], "easy", template["tags"])

    def _gen_change_permissions(self, example_id: str, template: dict) -> Example:
        filepath = f"./{self.var.random_filename()}"
        perm_mode = random.choice(["644", "755", "600", "700", "664"])

        perm_descriptions = {
            "644": "owner read/write, group/others read-only",
            "755": "owner full access, group/others read and execute",
            "600": "owner read/write only (private)",
            "700": "owner full access only (private)",
            "664": "owner and group read/write, others read-only",
        }

        requests = [
            f"Set permissions on {filepath} to {perm_mode}",
            f"chmod {perm_mode} {filepath}",
            f"Change {filepath} permissions to {perm_descriptions[perm_mode]}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"chmod {perm_mode} {filepath}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)
        conversations.append(self.create_tool_result(tool_id, ""))

        cmd2 = f"ls -l {filepath}"
        tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
        conversations.append(tool_msg2)

        perm_strings = {
            "644": "-rw-r--r--",
            "755": "-rwxr-xr-x",
            "600": "-rw-------",
            "700": "-rwx------",
            "664": "-rw-rw-r--",
        }
        output2 = f"{perm_strings[perm_mode]} 1 {self.var.username()} {self.var.username()} 1234 {self.var.random_date()} {filepath}"
        conversations.append(self.create_tool_result(tool_id2, output2))

        response = f"Set `{filepath}` permissions to `{perm_mode}` ({perm_descriptions[perm_mode]})."
        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["chmod", "ls"], "easy", template["tags"])

    def _gen_check_permissions(self, example_id: str, template: dict) -> Example:
        filepath = f"./{self.var.random_path()}/{self.var.random_filename()}"

        requests = [
            f"Check permissions on {filepath}",
            f"What are the permissions of {filepath}?",
            f"Show me who can access {filepath}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"ls -la {filepath}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        perms = random.choice(["-rw-r--r--", "-rwxr-xr-x", "-rw-------", "-rwxrwxr-x"])
        owner = self.var.username()
        group = random.choice([owner, "www-data", "developers"])
        output = f"{perms} 1 {owner} {group} 4567 {self.var.random_date()} {filepath}"
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"""Permissions for `{filepath}`:

| Property | Value |
|----------|-------|
| Permissions | `{perms}` |
| Owner | {owner} ({"read/write" if "w" in perms[1:3] else "read-only"}) |
| Group | {group} ({"read/write" if "w" in perms[4:6] else "read-only"}) |
| Others | {"read-only" if perms[7] == 'r' else "no access"} |"""

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["ls"], "easy", template["tags"])

    def _gen_change_owner(self, example_id: str, template: dict) -> Example:
        filepath = random.choice(["/var/www/html", f"./{self.var.project_name()}", "/etc/myapp"])
        new_owner = random.choice(["www-data", "nginx", self.var.username(), "deploy"])
        new_group = random.choice(["www-data", "nginx", "developers", new_owner])

        requests = [
            f"Change owner of {filepath} to {new_owner}",
            f"chown {new_owner}:{new_group} {filepath}",
            f"Make {new_owner} the owner of {filepath}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"sudo chown -R {new_owner}:{new_group} {filepath}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)
        conversations.append(self.create_tool_result(tool_id, ""))

        cmd2 = f"ls -la {filepath}"
        tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
        conversations.append(tool_msg2)

        output2 = f"""total 12
drwxr-xr-x 3 {new_owner} {new_group} 4096 {self.var.random_date()} .
drwxr-xr-x 5 root root 4096 {self.var.random_date()} ..
-rw-r--r-- 1 {new_owner} {new_group} 1234 {self.var.random_date()} index.html"""
        conversations.append(self.create_tool_result(tool_id2, output2))

        response = f"Changed ownership of `{filepath}` (and all contents) to `{new_owner}:{new_group}`."
        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["chown", "ls"], "medium", template["tags"])

    def _gen_recursive_chmod(self, example_id: str, template: dict) -> Example:
        directory = f"./{self.var.project_name()}"
        dir_perms = "755"
        file_perms = "644"

        requests = [
            f"Set proper permissions for the web directory {directory}",
            f"Fix permissions recursively on {directory}",
            f"Set directories to 755 and files to 644 in {directory}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        response = "I'll set directories to 755 and files to 644, which is standard for web content."
        conversations.append(self.create_assistant_message(response))

        # Directories
        cmd = f"find {directory} -type d -exec chmod {dir_perms} {{}} \\;"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)
        conversations.append(self.create_tool_result(tool_id, ""))

        # Files
        cmd2 = f"find {directory} -type f -exec chmod {file_perms} {{}} \\;"
        tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
        conversations.append(tool_msg2)
        conversations.append(self.create_tool_result(tool_id2, ""))

        # Verify
        cmd3 = f"ls -la {directory}/"
        tool_msg3, tool_id3 = self.create_tool_call_message(cmd3)
        conversations.append(tool_msg3)

        output3 = f"""total 20
drwxr-xr-x 4 {self.var.username()} {self.var.username()} 4096 {self.var.random_date()} .
drwxr-xr-x 8 {self.var.username()} {self.var.username()} 4096 {self.var.random_date()} ..
drwxr-xr-x 2 {self.var.username()} {self.var.username()} 4096 {self.var.random_date()} css
-rw-r--r-- 1 {self.var.username()} {self.var.username()} 1234 {self.var.random_date()} index.html
drwxr-xr-x 2 {self.var.username()} {self.var.username()} 4096 {self.var.random_date()} js"""
        conversations.append(self.create_tool_result(tool_id3, output3))

        response2 = f"""Permissions updated for `{directory}`:

- **Directories**: 755 (rwxr-xr-x) - owner full, others can read/execute
- **Files**: 644 (rw-r--r--) - owner read/write, others read-only

This is the standard permission setup for web content."""

        conversations.append(self.create_assistant_message(response2))

        return self.build_example(example_id, conversations, ["find", "chmod", "ls"], "medium", template["tags"])

    def _gen_fix_permissions(self, example_id: str, template: dict) -> Example:
        filepath = random.choice(["/var/www/html", f"./{self.var.project_name()}", "~/public_html"])

        requests = [
            f"I'm getting permission denied errors on {filepath}",
            f"Fix the permissions on {filepath}",
            f"Can't access {filepath}, permission denied",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        # Check current state
        cmd = f"ls -la {filepath}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        output = f"""total 16
drw------- 3 root root 4096 {self.var.random_date()} .
drwxr-xr-x 5 root root 4096 {self.var.random_date()} ..
-rw------- 1 root root 1234 {self.var.random_date()} index.html"""
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"I see the problem - the directory and files are owned by root with restrictive permissions. Let me fix this."
        conversations.append(self.create_assistant_message(response))

        # Fix ownership
        user = self.var.username()
        cmd2 = f"sudo chown -R {user}:{user} {filepath}"
        tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
        conversations.append(tool_msg2)
        conversations.append(self.create_tool_result(tool_id2, ""))

        # Fix permissions
        cmd3 = f"sudo chmod -R 755 {filepath}"
        tool_msg3, tool_id3 = self.create_tool_call_message(cmd3)
        conversations.append(tool_msg3)
        conversations.append(self.create_tool_result(tool_id3, ""))

        # Verify
        cmd4 = f"ls -la {filepath}"
        tool_msg4, tool_id4 = self.create_tool_call_message(cmd4)
        conversations.append(tool_msg4)

        output4 = f"""total 16
drwxr-xr-x 3 {user} {user} 4096 {self.var.random_date()} .
drwxr-xr-x 5 {user} {user} 4096 {self.var.random_date()} ..
-rwxr-xr-x 1 {user} {user} 1234 {self.var.random_date()} index.html"""
        conversations.append(self.create_tool_result(tool_id4, output4))

        response2 = f"""Fixed! The issues were:
1. **Ownership**: Was `root:root`, now `{user}:{user}`
2. **Permissions**: Were `700/600`, now `755`

You should now have full access to `{filepath}`."""

        conversations.append(self.create_assistant_message(response2))

        return self.build_example(example_id, conversations, ["ls", "chown", "chmod"], "hard", template["tags"], has_error_recovery=True)

    def _gen_secure_file(self, example_id: str, template: dict) -> Example:
        filename = random.choice([".env", "credentials.json", "private_key.pem", "secrets.yaml", "config.ini"])

        requests = [
            f"Secure {filename} so only I can read it",
            f"Make {filename} private",
            f"Restrict access to {filename}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        # Check current
        cmd = f"ls -la {filename}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        output = f"-rw-r--r-- 1 {self.var.username()} {self.var.username()} 256 {self.var.random_date()} {filename}"
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Currently `{filename}` is readable by everyone (644). I'll make it private (600)."
        conversations.append(self.create_assistant_message(response))

        cmd2 = f"chmod 600 {filename}"
        tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
        conversations.append(tool_msg2)
        conversations.append(self.create_tool_result(tool_id2, ""))

        cmd3 = f"ls -la {filename}"
        tool_msg3, tool_id3 = self.create_tool_call_message(cmd3)
        conversations.append(tool_msg3)

        output3 = f"-rw------- 1 {self.var.username()} {self.var.username()} 256 {self.var.random_date()} {filename}"
        conversations.append(self.create_tool_result(tool_id3, output3))

        response2 = f"""`{filename}` is now secured:

- **Before**: `-rw-r--r--` (644) - Everyone could read
- **After**: `-rw-------` (600) - Only you can read/write

No other users on the system can access this file now."""

        conversations.append(self.create_assistant_message(response2))

        return self.build_example(example_id, conversations, ["ls", "chmod"], "hard", template["tags"])
