"""
Archive & Compression Templates

Commands: tar, gzip, gunzip, zip, unzip, xz
"""

import random
from .base import BaseTemplateGenerator, Example


class ArchiveTemplates(BaseTemplateGenerator):
    """Generate archive and compression examples."""

    category = "archive"

    TEMPLATES = [
        {"type": "create_tar", "difficulty": "easy", "tags": ["tar", "archive"]},
        {"type": "extract_tar", "difficulty": "easy", "tags": ["tar", "extract"]},
        {"type": "compress_gzip", "difficulty": "easy", "tags": ["gzip", "compress"]},
        {"type": "create_zip", "difficulty": "easy", "tags": ["zip", "archive"]},
        {"type": "extract_zip", "difficulty": "easy", "tags": ["unzip", "extract"]},
        {"type": "list_archive", "difficulty": "medium", "tags": ["tar", "zip", "list"]},
        {"type": "tar_gz_combined", "difficulty": "medium", "tags": ["tar", "gzip"]},
        {"type": "extract_specific", "difficulty": "medium", "tags": ["tar", "extract", "selective"]},
        {"type": "compress_directory", "difficulty": "hard", "tags": ["tar", "gzip", "backup"]},
    ]

    def generate(self, example_id: str) -> Example:
        template = random.choice(self.TEMPLATES)
        method_name = f"_gen_{template['type']}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(example_id, template)
        return self._gen_create_tar(example_id, template)

    def _gen_create_tar(self, example_id: str, template: dict) -> Example:
        directory = self.var.project_name()
        archive_name = f"{directory}.tar"

        requests = [
            f"Create a tar archive of {directory}",
            f"tar {directory}",
            f"Archive the {directory} folder",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"tar -cvf {archive_name} {directory}/"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        files = [f"{directory}/{self.var.random_filename()}" for _ in range(random.randint(3, 6))]
        output = "\n".join(files)
        conversations.append(self.create_tool_result(tool_id, output))

        # Show size
        cmd2 = f"ls -lh {archive_name}"
        tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
        conversations.append(tool_msg2)

        size = self.var.random_size("M")
        output2 = f"-rw-r--r-- 1 {self.var.username()} {self.var.username()} {size} {self.var.random_date()} {archive_name}"
        conversations.append(self.create_tool_result(tool_id2, output2))

        response = f"Created `{archive_name}` ({size}) containing {len(files)} files."
        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["tar", "ls"], "easy", template["tags"])

    def _gen_extract_tar(self, example_id: str, template: dict) -> Example:
        archive_name = f"{self.var.project_name()}.tar.gz"

        requests = [
            f"Extract {archive_name}",
            f"Untar {archive_name}",
            f"tar -xf {archive_name}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"tar -xvf {archive_name}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        directory = archive_name.replace(".tar.gz", "")
        files = [f"{directory}/{self.var.random_filename()}" for _ in range(random.randint(3, 6))]
        output = "\n".join(files)
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Extracted {len(files)} files from `{archive_name}` to `./{directory}/`"
        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["tar"], "easy", template["tags"])

    def _gen_compress_gzip(self, example_id: str, template: dict) -> Example:
        filename = random.choice(["access.log", "data.json", "backup.sql", "output.txt"])

        requests = [
            f"Compress {filename}",
            f"gzip {filename}",
            f"Shrink {filename} to save space",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        # Show original size
        cmd = f"ls -lh {filename}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        orig_size = random.randint(50, 500)
        output = f"-rw-r--r-- 1 {self.var.username()} {self.var.username()} {orig_size}M {self.var.random_date()} {filename}"
        conversations.append(self.create_tool_result(tool_id, output))

        # Compress
        cmd2 = f"gzip -v {filename}"
        tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
        conversations.append(tool_msg2)

        compression = random.uniform(60, 90)
        new_size = int(orig_size * (100 - compression) / 100)
        output2 = f"{filename}:    {compression:.1f}% -- replaced with {filename}.gz"
        conversations.append(self.create_tool_result(tool_id2, output2))

        response = f"Compressed `{filename}` → `{filename}.gz`\n\n- Original: {orig_size}M\n- Compressed: ~{new_size}M\n- Savings: {compression:.1f}%"
        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["ls", "gzip"], "easy", template["tags"])

    def _gen_create_zip(self, example_id: str, template: dict) -> Example:
        directory = self.var.project_name()
        zip_name = f"{directory}.zip"

        requests = [
            f"Create a zip file of {directory}",
            f"zip {directory}",
            f"Make a zip archive of {directory}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"zip -r {zip_name} {directory}/"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        files = [f"{directory}/{self.var.random_filename()}" for _ in range(random.randint(3, 8))]
        output_lines = [f"  adding: {f} (deflated {random.randint(30, 80)}%)" for f in files]
        output = "\n".join(output_lines)
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Created `{zip_name}` with {len(files)} files (all compressed with deflate)."
        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["zip"], "easy", template["tags"])

    def _gen_extract_zip(self, example_id: str, template: dict) -> Example:
        zip_name = f"{self.var.project_name()}.zip"

        requests = [
            f"Extract {zip_name}",
            f"Unzip {zip_name}",
            f"unzip {zip_name}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"unzip {zip_name}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        directory = zip_name.replace(".zip", "")
        files = [f"{directory}/{self.var.random_filename()}" for _ in range(random.randint(3, 6))]
        output_lines = [f"Archive:  {zip_name}"] + [f"  inflating: {f}" for f in files]
        output = "\n".join(output_lines)
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Extracted {len(files)} files from `{zip_name}`."
        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["unzip"], "easy", template["tags"])

    def _gen_list_archive(self, example_id: str, template: dict) -> Example:
        is_tar = random.choice([True, False])
        archive_name = f"{self.var.project_name()}.{'tar.gz' if is_tar else 'zip'}"

        requests = [
            f"Show what's inside {archive_name}",
            f"List contents of {archive_name}",
            f"What files are in {archive_name}?",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        if is_tar:
            cmd = f"tar -tvf {archive_name}"
            files = [f"-rw-r--r-- {self.var.username()}/{self.var.username()} {random.randint(100, 50000):>8} {self.var.random_date()} {self.var.random_path()}/{self.var.random_filename()}" for _ in range(random.randint(4, 8))]
        else:
            cmd = f"unzip -l {archive_name}"
            files = [f"  {random.randint(100, 50000):>8}  {self.var.random_date()} {self.var.random_time()[:5]}   {self.var.random_path()}/{self.var.random_filename()}" for _ in range(random.randint(4, 8))]

        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        output = "\n".join(files)
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"`{archive_name}` contains {len(files)} files:\n\n"
        for f in files[:5]:
            filename = f.split()[-1]
            response += f"- `{filename}`\n"
        if len(files) > 5:
            response += f"- ...and {len(files) - 5} more"

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["tar" if is_tar else "unzip"], "medium", template["tags"])

    def _gen_tar_gz_combined(self, example_id: str, template: dict) -> Example:
        directory = self.var.project_name()
        archive_name = f"{directory}_{self.var.random_date()}.tar.gz"

        requests = [
            f"Create a compressed tar archive of {directory}",
            f"tar.gz {directory}",
            f"Create a gzipped tarball of {directory}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"tar -czvf {archive_name} {directory}/"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        files = [f"{directory}/{self.var.random_filename()}" for _ in range(random.randint(4, 8))]
        output = "\n".join(files)
        conversations.append(self.create_tool_result(tool_id, output))

        cmd2 = f"ls -lh {archive_name}"
        tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
        conversations.append(tool_msg2)

        size = self.var.random_size("M")
        output2 = f"-rw-r--r-- 1 {self.var.username()} {self.var.username()} {size} {self.var.random_date()} {archive_name}"
        conversations.append(self.create_tool_result(tool_id2, output2))

        response = f"Created compressed archive `{archive_name}` ({size}) with {len(files)} files."
        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["tar", "ls"], "medium", template["tags"])

    def _gen_extract_specific(self, example_id: str, template: dict) -> Example:
        archive_name = f"{self.var.project_name()}.tar.gz"
        specific_file = f"{self.var.project_name()}/{self.var.directory()}/{self.var.random_filename()}"

        requests = [
            f"Extract only {specific_file} from {archive_name}",
            f"Get just the {specific_file.split('/')[-1]} from the archive",
            f"Extract a specific file from {archive_name}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        # List first
        cmd = f"tar -tvf {archive_name} | grep {specific_file.split('/')[-1]}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        output = f"-rw-r--r-- {self.var.username()}/{self.var.username()} {random.randint(100, 5000):>8} {self.var.random_date()} {specific_file}"
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Found the file. Let me extract it."
        conversations.append(self.create_assistant_message(response))

        cmd2 = f"tar -xvf {archive_name} {specific_file}"
        tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
        conversations.append(tool_msg2)

        output2 = specific_file
        conversations.append(self.create_tool_result(tool_id2, output2))

        response2 = f"Extracted `{specific_file}` from the archive."
        conversations.append(self.create_assistant_message(response2))

        return self.build_example(example_id, conversations, ["tar", "grep"], "medium", template["tags"], uses_pipes=True)

    def _gen_compress_directory(self, example_id: str, template: dict) -> Example:
        directory = self.var.project_name()
        date = self.var.random_date()
        archive_name = f"backup_{directory}_{date}.tar.gz"

        requests = [
            f"Create a backup archive of {directory} with today's date",
            f"Compress and backup {directory}",
            f"Make a dated backup of {directory}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        # Check size first
        cmd = f"du -sh {directory}/"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        orig_size = f"{random.randint(50, 500)}M"
        output = f"{orig_size}\t{directory}/"
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Directory is {orig_size}. Creating compressed backup..."
        conversations.append(self.create_assistant_message(response))

        # Create archive
        cmd2 = f"tar -czvf {archive_name} {directory}/ 2>/dev/null"
        tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
        conversations.append(tool_msg2)

        files = [f"{directory}/{self.var.random_filename()}" for _ in range(random.randint(5, 10))]
        output2 = "\n".join(files)
        conversations.append(self.create_tool_result(tool_id2, output2))

        # Show result
        cmd3 = f"ls -lh {archive_name}"
        tool_msg3, tool_id3 = self.create_tool_call_message(cmd3)
        conversations.append(tool_msg3)

        compressed_size = f"{random.randint(10, 100)}M"
        output3 = f"-rw-r--r-- 1 {self.var.username()} {self.var.username()} {compressed_size} {date} {archive_name}"
        conversations.append(self.create_tool_result(tool_id3, output3))

        response2 = f"""Backup complete!

| Property | Value |
|----------|-------|
| Archive | `{archive_name}` |
| Original | {orig_size} |
| Compressed | {compressed_size} |
| Files | {len(files)} |

To restore: `tar -xzvf {archive_name}`"""

        conversations.append(self.create_assistant_message(response2))

        return self.build_example(example_id, conversations, ["du", "tar", "ls"], "hard", template["tags"])
