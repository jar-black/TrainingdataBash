"""
File Operations Templates

Commands: ls, cd, pwd, cp, mv, rm, mkdir, rmdir, touch, find, locate, ln, stat, file, du, df, tree, basename, dirname, realpath
"""

import random
from typing import List
from .base import BaseTemplateGenerator, Example, Message


class FileOperationsTemplates(BaseTemplateGenerator):
    """Generate file operations examples."""

    category = "file_operations"

    # Task templates with (user_request, commands, difficulty, tags)
    TEMPLATES = [
        # Easy: Single commands
        {
            "type": "list_files",
            "difficulty": "easy",
            "tags": ["ls", "directory"],
        },
        {
            "type": "find_files_by_extension",
            "difficulty": "easy",
            "tags": ["find", "search"],
        },
        {
            "type": "check_disk_space",
            "difficulty": "easy",
            "tags": ["df", "disk"],
        },
        {
            "type": "create_directory",
            "difficulty": "easy",
            "tags": ["mkdir", "directory"],
        },
        {
            "type": "show_file_info",
            "difficulty": "easy",
            "tags": ["stat", "file"],
        },
        # Medium: Multiple commands
        {
            "type": "find_large_files",
            "difficulty": "medium",
            "tags": ["find", "du", "disk-space"],
        },
        {
            "type": "backup_directory",
            "difficulty": "medium",
            "tags": ["cp", "backup"],
        },
        {
            "type": "find_and_delete_old_files",
            "difficulty": "medium",
            "tags": ["find", "rm", "cleanup"],
        },
        {
            "type": "copy_files_by_pattern",
            "difficulty": "medium",
            "tags": ["find", "cp", "pattern"],
        },
        {
            "type": "directory_size_breakdown",
            "difficulty": "medium",
            "tags": ["du", "sort", "analysis"],
        },
        # Hard: Complex workflows
        {
            "type": "find_duplicates",
            "difficulty": "hard",
            "tags": ["find", "md5sum", "duplicates"],
        },
        {
            "type": "organize_files_by_type",
            "difficulty": "hard",
            "tags": ["find", "mv", "organize"],
        },
        {
            "type": "sync_directories",
            "difficulty": "hard",
            "tags": ["rsync", "diff", "sync"],
        },
    ]

    def generate(self, example_id: str) -> Example:
        """Generate a file operations example."""
        template = random.choice(self.TEMPLATES)
        method_name = f"_gen_{template['type']}"

        if hasattr(self, method_name):
            return getattr(self, method_name)(example_id, template)
        else:
            # Fallback to a basic template
            return self._gen_list_files(example_id, template)

    def _gen_list_files(self, example_id: str, template: dict) -> Example:
        """List files in a directory."""
        directory = random.choice([
            f"~/{self.var.project_name()}",
            f"/var/log",
            f"~/{self.var.directory()}",
            ".",
            f"~/{self.var.project_name()}/{self.var.directory()}",
        ])

        show_hidden = random.choice([True, False])
        show_details = random.choice([True, False])

        # Build user request
        requests = [
            f"List all files in {directory}",
            f"Show me what's in {directory}",
            f"What files are in {directory}?",
            f"Can you list the contents of {directory}?",
        ]
        if show_hidden:
            requests = [r + " including hidden files" for r in requests]
        if show_details:
            requests = [r.replace("List", "List with details").replace("Show", "Show details of").replace("What files", "What files with sizes") for r in requests]

        user_request = random.choice(requests)

        # Build command
        flags = ""
        if show_details:
            flags += "l"
        if show_hidden:
            flags += "a"
        if flags:
            flags = "-" + flags + " "

        command = f"ls {flags}{directory}"

        # Build conversation
        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(user_request))

        tool_msg, tool_id = self.create_tool_call_message(command)
        conversations.append(tool_msg)

        output = self.out.ls_output(num_files=random.randint(3, 8), show_hidden=show_hidden)
        conversations.append(self.create_tool_result(tool_id, output))

        # Assistant response
        num_items = len(output.strip().split("\n"))
        response = f"Here are the contents of `{directory}`:\n\n"
        if show_details:
            response += f"Found {num_items} items. The listing shows permissions, owner, size, and modification date for each file."
        else:
            response += f"Found {num_items} items in the directory."

        response += "\n\nWould you like me to do anything with these files?"
        conversations.append(self.create_assistant_message(response))

        return self.build_example(
            example_id=example_id,
            conversations=conversations,
            commands_used=["ls"],
            difficulty="easy",
            tags=template["tags"],
        )

    def _gen_find_files_by_extension(self, example_id: str, template: dict) -> Example:
        """Find files by extension."""
        ext = self.var.code_extension()
        directory = random.choice([".", f"~/{self.var.project_name()}", "/home"])

        requests = [
            f"Find all {ext} files in {directory}",
            f"Search for {ext} files",
            f"List all {ext} files in the project",
            f"Where are the {ext} files?",
        ]
        user_request = random.choice(requests)

        command = f"find {directory} -name '*{ext}' -type f"

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(user_request))

        tool_msg, tool_id = self.create_tool_call_message(command)
        conversations.append(tool_msg)

        output = self.out.find_output(f"*{ext}", num_results=random.randint(3, 10))
        conversations.append(self.create_tool_result(tool_id, output))

        num_files = len(output.strip().split("\n"))
        response = f"I found {num_files} `{ext}` files:\n\n"
        for line in output.strip().split("\n")[:5]:
            response += f"- `{line}`\n"
        if num_files > 5:
            response += f"\n...and {num_files - 5} more files."

        conversations.append(self.create_assistant_message(response))

        return self.build_example(
            example_id=example_id,
            conversations=conversations,
            commands_used=["find"],
            difficulty="easy",
            tags=template["tags"],
        )

    def _gen_check_disk_space(self, example_id: str, template: dict) -> Example:
        """Check disk space."""
        requests = [
            "How much disk space do I have left?",
            "Check my disk usage",
            "Show me disk space",
            "Is the disk full?",
            "df -h please",
        ]
        user_request = random.choice(requests)

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(user_request))

        tool_msg, tool_id = self.create_tool_call_message("df -h")
        conversations.append(tool_msg)

        # Generate realistic df output
        output = """Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1       500G  {}G  {}G  {}%  /
tmpfs           16G   {}M   16G   1% /dev/shm
/dev/sdb1       1.0T  {}G  {}G  {}% /data""".format(
            random.randint(100, 400),
            random.randint(50, 200),
            random.randint(30, 80),
            random.randint(1, 500),
            random.randint(100, 800),
            random.randint(100, 500),
            random.randint(20, 90),
        )
        conversations.append(self.create_tool_result(tool_id, output))

        response = """Here's your disk space summary:

| Filesystem | Size | Used | Available | Use% |
|------------|------|------|-----------|------|
| / (root) | 500G | varies | varies | varies |
| /data | 1.0T | varies | varies | varies |

Your root filesystem has plenty of space available. Would you like me to check which directories are using the most space?"""

        conversations.append(self.create_assistant_message(response))

        return self.build_example(
            example_id=example_id,
            conversations=conversations,
            commands_used=["df"],
            difficulty="easy",
            tags=template["tags"],
        )

    def _gen_create_directory(self, example_id: str, template: dict) -> Example:
        """Create a directory structure."""
        project = self.var.project_name()
        dirs = random.choice([
            f"{project}/src",
            f"{project}/tests",
            f"backup_{self.var.random_date()}",
            f"{project}/{{src,tests,docs,config}}",
        ])

        requests = [
            f"Create a directory called {dirs}",
            f"Make directory {dirs}",
            f"mkdir {dirs}",
            f"I need a new folder: {dirs}",
        ]
        user_request = random.choice(requests)

        command = f"mkdir -p {dirs}"

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(user_request))

        tool_msg, tool_id = self.create_tool_call_message(command)
        conversations.append(tool_msg)
        conversations.append(self.create_tool_result(tool_id, ""))

        # Verify
        tool_msg2, tool_id2 = self.create_tool_call_message(f"ls -la {dirs.split('/')[0] if '/' in dirs else dirs}")
        conversations.append(tool_msg2)

        verify_output = self.out.ls_output(num_files=2, show_hidden=True)
        conversations.append(self.create_tool_result(tool_id2, verify_output))

        response = f"Done! I've created the directory `{dirs}`. The `-p` flag ensures any parent directories are created as needed."
        conversations.append(self.create_assistant_message(response))

        return self.build_example(
            example_id=example_id,
            conversations=conversations,
            commands_used=["mkdir", "ls"],
            difficulty="easy",
            tags=template["tags"],
        )

    def _gen_show_file_info(self, example_id: str, template: dict) -> Example:
        """Show detailed file information."""
        filename = self.var.random_filename()
        filepath = f"./{self.var.random_path()}/{filename}"

        requests = [
            f"Show me information about {filepath}",
            f"What can you tell me about {filepath}?",
            f"Get file details for {filepath}",
            f"stat {filepath}",
        ]
        user_request = random.choice(requests)

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(user_request))

        tool_msg, tool_id = self.create_tool_call_message(f"stat {filepath}")
        conversations.append(tool_msg)

        output = f"""  File: {filepath}
  Size: {random.randint(100, 50000)}       Blocks: {random.randint(8, 128)}          IO Block: 4096   regular file
Device: 801h/{random.randint(1000, 9999)}d  Inode: {random.randint(100000, 999999)}    Links: 1
Access: (0644/-rw-r--r--)  Uid: ( 1000/{self.var.username()})   Gid: ( 1000/{self.var.username()})
Access: {self.var.random_date()} {self.var.random_time()} +0000
Modify: {self.var.random_date()} {self.var.random_time()} +0000
Change: {self.var.random_date()} {self.var.random_time()} +0000"""

        conversations.append(self.create_tool_result(tool_id, output))

        response = f"""Here's the detailed information for `{filepath}`:

| Property | Value |
|----------|-------|
| Type | Regular file |
| Size | varies |
| Permissions | 0644 (rw-r--r--) |
| Owner | {self.var.username()} |
| Last Modified | {self.var.random_date()} |

Would you like to modify the permissions or do anything else with this file?"""

        conversations.append(self.create_assistant_message(response))

        return self.build_example(
            example_id=example_id,
            conversations=conversations,
            commands_used=["stat"],
            difficulty="easy",
            tags=template["tags"],
        )

    def _gen_find_large_files(self, example_id: str, template: dict) -> Example:
        """Find large files in a directory."""
        size_threshold = random.choice(["10M", "50M", "100M", "500M", "1G"])
        directory = random.choice(["/var/log", "~", ".", "/home"])

        requests = [
            f"Find all files larger than {size_threshold} in {directory}",
            f"What files are taking up the most space in {directory}?",
            f"Show me large files over {size_threshold}",
            f"Find big files in {directory}",
        ]
        user_request = random.choice(requests)

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(user_request))

        command = f"find {directory} -type f -size +{size_threshold} -exec ls -lh {{}} \\; 2>/dev/null | sort -k5 -h -r | head -20"

        tool_msg, tool_id = self.create_tool_call_message(command)
        conversations.append(tool_msg)

        # Generate output
        lines = []
        for _ in range(random.randint(3, 8)):
            size = self.var.random_size(random.choice(["M", "G"]))
            path = f"{directory}/{self.var.random_path()}/{self.var.random_filename()}"
            lines.append(f"-rw-r--r-- 1 {self.var.username()} {self.var.username()} {size} {self.var.random_date()} {path}")

        output = "\n".join(lines)
        conversations.append(self.create_tool_result(tool_id, output))

        num_files = len(lines)
        response = f"I found {num_files} files larger than {size_threshold}:\n\n"
        response += "| File | Size |\n|------|------|\n"
        for line in lines[:5]:
            parts = line.split()
            response += f"| `{parts[-1]}` | {parts[4]} |\n"

        response += "\nWould you like me to help you clean up any of these files?"
        conversations.append(self.create_assistant_message(response))

        # Maybe add follow-up
        if random.random() < 0.5:
            conversations.append(self.create_user_message("Yes, delete the largest one"))

            largest_file = lines[0].split()[-1]
            tool_msg2, tool_id2 = self.create_tool_call_message(f"rm {largest_file}")
            conversations.append(tool_msg2)
            conversations.append(self.create_tool_result(tool_id2, ""))

            conversations.append(self.create_assistant_message(f"Done! I've deleted `{largest_file}`. The space should now be freed up."))

        return self.build_example(
            example_id=example_id,
            conversations=conversations,
            commands_used=["find", "ls", "sort", "head"] + (["rm"] if len(conversations) > 6 else []),
            difficulty="medium",
            tags=template["tags"],
            uses_pipes=True,
        )

    def _gen_backup_directory(self, example_id: str, template: dict) -> Example:
        """Backup a directory with date stamp."""
        project = self.var.project_name()
        source = f"~/{project}"
        backup_dir = "~/backups"

        requests = [
            f"Create a backup of {source}",
            f"Backup my {project} folder",
            f"Make a copy of {source} with today's date",
            f"I need to backup {source}",
        ]
        user_request = random.choice(requests)

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(user_request))

        # Create backup directory
        tool_msg, tool_id = self.create_tool_call_message(f"mkdir -p {backup_dir}")
        conversations.append(tool_msg)
        conversations.append(self.create_tool_result(tool_id, ""))

        # Copy with date
        date = self.var.random_date()
        tool_msg2, tool_id2 = self.create_tool_call_message(f"cp -r {source} {backup_dir}/{project}_{date}")
        conversations.append(tool_msg2)
        conversations.append(self.create_tool_result(tool_id2, ""))

        # Verify
        tool_msg3, tool_id3 = self.create_tool_call_message(f"ls -la {backup_dir}/")
        conversations.append(tool_msg3)

        output = f"""total 12
drwxr-xr-x 3 {self.var.username()} {self.var.username()} 4096 {date} .
drwxr-xr-x 8 {self.var.username()} {self.var.username()} 4096 {date} ..
drwxr-xr-x 5 {self.var.username()} {self.var.username()} 4096 {date} {project}_{date}"""

        conversations.append(self.create_tool_result(tool_id3, output))

        response = f"""Done! I've created a backup of your project:

- **Source**: `{source}`
- **Backup**: `{backup_dir}/{project}_{date}`

The backup includes all files and subdirectories. Would you like me to compress it to save space?"""

        conversations.append(self.create_assistant_message(response))

        return self.build_example(
            example_id=example_id,
            conversations=conversations,
            commands_used=["mkdir", "cp", "ls"],
            difficulty="medium",
            tags=template["tags"],
        )

    def _gen_find_and_delete_old_files(self, example_id: str, template: dict) -> Example:
        """Find and delete files older than X days."""
        days = random.choice([7, 14, 30, 60, 90])
        directory = random.choice(["/tmp", "/var/log", "~/.cache", "./logs"])
        pattern = random.choice(["*.log", "*.tmp", "*.bak", "*"])

        requests = [
            f"Delete all {pattern} files older than {days} days in {directory}",
            f"Clean up old files in {directory}",
            f"Remove files not modified in the last {days} days from {directory}",
        ]
        user_request = random.choice(requests)

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(user_request))

        # First, show what would be deleted
        find_cmd = f"find {directory} -name '{pattern}' -type f -mtime +{days}"
        tool_msg, tool_id = self.create_tool_call_message(find_cmd)
        conversations.append(tool_msg)

        files = [f"{directory}/{self.var.random_filename('.log')}" for _ in range(random.randint(3, 8))]
        output = "\n".join(files)
        conversations.append(self.create_tool_result(tool_id, output))

        num_files = len(files)
        response = f"I found {num_files} files older than {days} days that match `{pattern}`:\n\n"
        for f in files[:5]:
            response += f"- `{f}`\n"
        if num_files > 5:
            response += f"- ...and {num_files - 5} more\n"
        response += "\nShall I delete these files?"

        conversations.append(self.create_assistant_message(response))
        conversations.append(self.create_user_message("Yes, delete them"))

        # Delete
        delete_cmd = f"find {directory} -name '{pattern}' -type f -mtime +{days} -delete"
        tool_msg2, tool_id2 = self.create_tool_call_message(delete_cmd)
        conversations.append(tool_msg2)
        conversations.append(self.create_tool_result(tool_id2, ""))

        conversations.append(self.create_assistant_message(f"Done! I've deleted {num_files} old files from `{directory}`. The space has been freed up."))

        return self.build_example(
            example_id=example_id,
            conversations=conversations,
            commands_used=["find"],
            difficulty="medium",
            tags=template["tags"],
        )

    def _gen_copy_files_by_pattern(self, example_id: str, template: dict) -> Example:
        """Copy files matching a pattern to another directory."""
        ext = self.var.code_extension()
        source = f"./{self.var.directory()}"
        dest = f"./backup_{self.var.directory()}"

        requests = [
            f"Copy all {ext} files from {source} to {dest}",
            f"Backup all {ext} files to {dest}",
            f"Move all {ext} files to a backup folder",
        ]
        user_request = random.choice(requests)

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(user_request))

        # Create dest
        tool_msg, tool_id = self.create_tool_call_message(f"mkdir -p {dest}")
        conversations.append(tool_msg)
        conversations.append(self.create_tool_result(tool_id, ""))

        # Find and copy
        cmd = f"find {source} -name '*{ext}' -exec cp {{}} {dest}/ \\;"
        tool_msg2, tool_id2 = self.create_tool_call_message(cmd)
        conversations.append(tool_msg2)
        conversations.append(self.create_tool_result(tool_id2, ""))

        # Verify
        tool_msg3, tool_id3 = self.create_tool_call_message(f"ls {dest}/")
        conversations.append(tool_msg3)

        files = [self.var.random_filename(ext) for _ in range(random.randint(3, 6))]
        output = "\n".join(files)
        conversations.append(self.create_tool_result(tool_id3, output))

        response = f"Done! I've copied {len(files)} `{ext}` files to `{dest}/`:\n\n"
        for f in files:
            response += f"- `{f}`\n"

        conversations.append(self.create_assistant_message(response))

        return self.build_example(
            example_id=example_id,
            conversations=conversations,
            commands_used=["mkdir", "find", "cp", "ls"],
            difficulty="medium",
            tags=template["tags"],
        )

    def _gen_directory_size_breakdown(self, example_id: str, template: dict) -> Example:
        """Show directory size breakdown."""
        directory = random.choice([".", "~", f"~/{self.var.project_name()}", "/var"])

        requests = [
            f"Show me the size of each subdirectory in {directory}",
            f"What's taking up space in {directory}?",
            f"Disk usage breakdown for {directory}",
            f"Which folders are largest in {directory}?",
        ]
        user_request = random.choice(requests)

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(user_request))

        cmd = f"du -sh {directory}/*/ 2>/dev/null | sort -rh | head -10"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        output = self.out.du_output(num_dirs=random.randint(5, 10))
        conversations.append(self.create_tool_result(tool_id, output))

        lines = output.strip().split("\n")
        response = f"Here's the disk usage breakdown for `{directory}`:\n\n"
        response += "| Directory | Size |\n|-----------|------|\n"
        for line in lines[:7]:
            parts = line.split("\t")
            if len(parts) >= 2:
                response += f"| `{parts[1]}` | {parts[0]} |\n"

        response += "\nWould you like me to investigate any of these directories further?"
        conversations.append(self.create_assistant_message(response))

        return self.build_example(
            example_id=example_id,
            conversations=conversations,
            commands_used=["du", "sort", "head"],
            difficulty="medium",
            tags=template["tags"],
            uses_pipes=True,
        )

    def _gen_find_duplicates(self, example_id: str, template: dict) -> Example:
        """Find duplicate files using checksums."""
        directory = random.choice(["~/Downloads", ".", f"~/{self.var.project_name()}"])

        requests = [
            f"Find duplicate files in {directory}",
            f"Are there any duplicate files in {directory}?",
            f"Check for duplicate files",
            f"Find files with the same content in {directory}",
        ]
        user_request = random.choice(requests)

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(user_request))

        cmd = f"find {directory} -type f -exec md5sum {{}} + 2>/dev/null | sort | uniq -w32 -dD"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        # Generate duplicate groups
        groups = []
        for _ in range(random.randint(2, 4)):
            hash = self.var.random_commit_hash(short=False)[:32]
            files = [f"{directory}/{self.var.random_path()}/{self.var.random_filename()}" for _ in range(random.randint(2, 3))]
            for f in files:
                groups.append(f"{hash}  {f}")

        output = "\n".join(groups)
        conversations.append(self.create_tool_result(tool_id, output))

        response = "I found several duplicate files:\n\n"
        current_hash = None
        group_num = 0
        for line in groups:
            hash = line[:32]
            filepath = line[34:]
            if hash != current_hash:
                current_hash = hash
                group_num += 1
                response += f"\n**Group {group_num}:**\n"
            response += f"- `{filepath}`\n"

        response += "\nWould you like me to delete the duplicates (keeping one copy of each)?"
        conversations.append(self.create_assistant_message(response))

        return self.build_example(
            example_id=example_id,
            conversations=conversations,
            commands_used=["find", "md5sum", "sort", "uniq"],
            difficulty="hard",
            tags=template["tags"],
            uses_pipes=True,
        )

    def _gen_organize_files_by_type(self, example_id: str, template: dict) -> Example:
        """Organize files into folders by type."""
        directory = random.choice(["~/Downloads", "~/Desktop", "."])

        requests = [
            f"Organize files in {directory} by type",
            f"Sort files in {directory} into folders by extension",
            f"Create folders for different file types in {directory}",
        ]
        user_request = random.choice(requests)

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(user_request))

        # First, see what's there
        tool_msg, tool_id = self.create_tool_call_message(f"ls {directory}")
        conversations.append(tool_msg)

        files = []
        for ext in [".pdf", ".jpg", ".py", ".txt", ".zip"]:
            for _ in range(random.randint(1, 3)):
                files.append(self.var.random_filename(ext))

        random.shuffle(files)
        output = "\n".join(files)
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"I see {len(files)} files of various types. I'll organize them into folders by extension."
        conversations.append(self.create_assistant_message(response))

        # Create directories and move files
        for ext in [".pdf", ".jpg", ".py", ".txt", ".zip"]:
            folder = ext[1:] + "_files"
            cmd = f"mkdir -p {directory}/{folder} && mv {directory}/*{ext} {directory}/{folder}/ 2>/dev/null"
            tool_msg2, tool_id2 = self.create_tool_call_message(cmd)
            conversations.append(tool_msg2)
            conversations.append(self.create_tool_result(tool_id2, ""))

        # Verify
        tool_msg3, tool_id3 = self.create_tool_call_message(f"ls -la {directory}/")
        conversations.append(tool_msg3)

        output = f"""total 20
drwxr-xr-x 6 user user 4096 Jan 15 14:00 .
drwxr-xr-x 8 user user 4096 Jan 15 14:00 ..
drwxr-xr-x 2 user user 4096 Jan 15 14:00 jpg_files
drwxr-xr-x 2 user user 4096 Jan 15 14:00 pdf_files
drwxr-xr-x 2 user user 4096 Jan 15 14:00 py_files
drwxr-xr-x 2 user user 4096 Jan 15 14:00 txt_files
drwxr-xr-x 2 user user 4096 Jan 15 14:00 zip_files"""

        conversations.append(self.create_tool_result(tool_id3, output))

        response = f"""Done! I've organized your files into the following folders:

- `pdf_files/` - PDF documents
- `jpg_files/` - Images
- `py_files/` - Python scripts
- `txt_files/` - Text files
- `zip_files/` - Archives

All files have been moved to their respective folders."""

        conversations.append(self.create_assistant_message(response))

        return self.build_example(
            example_id=example_id,
            conversations=conversations,
            commands_used=["ls", "mkdir", "mv"],
            difficulty="hard",
            tags=template["tags"],
        )

    def _gen_sync_directories(self, example_id: str, template: dict) -> Example:
        """Sync two directories."""
        source = f"~/{self.var.project_name()}"
        dest = random.choice(["/backup/projects", "~/backup", "/mnt/external/backup"])

        requests = [
            f"Sync {source} to {dest}",
            f"Mirror {source} to {dest}",
            f"Keep {dest} in sync with {source}",
        ]
        user_request = random.choice(requests)

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(user_request))

        # Show what would be synced
        cmd = f"rsync -avhn {source}/ {dest}/"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        files = [self.var.random_filename() for _ in range(random.randint(3, 8))]
        output = f"""sending incremental file list
{chr(10).join(files)}

sent 1,234 bytes  received 123 bytes  2,714.00 bytes/sec
total size is 12,345,678  speedup is 9,087.12 (DRY RUN)"""

        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Here's what would be synced (dry run):\n\n"
        response += f"**Files to transfer:** {len(files)}\n"
        for f in files[:5]:
            response += f"- `{f}`\n"
        response += f"\nTotal size: ~12 MB. Should I proceed with the actual sync?"

        conversations.append(self.create_assistant_message(response))
        conversations.append(self.create_user_message("Yes, do it"))

        # Actual sync
        cmd2 = f"rsync -avh {source}/ {dest}/"
        tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
        conversations.append(tool_msg2)

        output2 = f"""sending incremental file list
{chr(10).join(files)}

sent 1,234 bytes  received 123 bytes  2,714.00 bytes/sec
total size is 12,345,678  speedup is 9,087.12"""

        conversations.append(self.create_tool_result(tool_id2, output2))

        conversations.append(self.create_assistant_message(f"Done! Successfully synced {len(files)} files from `{source}` to `{dest}`. The directories are now in sync."))

        return self.build_example(
            example_id=example_id,
            conversations=conversations,
            commands_used=["rsync"],
            difficulty="hard",
            tags=template["tags"],
        )
