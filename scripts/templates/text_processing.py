"""
Text Processing Templates

Commands: cat, head, tail, grep, sed, awk, cut, sort, uniq, wc, diff, tr, tee, less, more
"""

import random
from .base import BaseTemplateGenerator, Example


class TextProcessingTemplates(BaseTemplateGenerator):
    """Generate text processing examples."""

    category = "text_processing"

    TEMPLATES = [
        {"type": "search_pattern", "difficulty": "easy", "tags": ["grep", "search"]},
        {"type": "count_lines", "difficulty": "easy", "tags": ["wc", "count"]},
        {"type": "view_file_head", "difficulty": "easy", "tags": ["head", "view"]},
        {"type": "view_file_tail", "difficulty": "easy", "tags": ["tail", "logs"]},
        {"type": "sort_file", "difficulty": "easy", "tags": ["sort"]},
        {"type": "find_replace", "difficulty": "medium", "tags": ["sed", "replace"]},
        {"type": "extract_column", "difficulty": "medium", "tags": ["awk", "cut", "csv"]},
        {"type": "unique_lines", "difficulty": "medium", "tags": ["sort", "uniq"]},
        {"type": "compare_files", "difficulty": "medium", "tags": ["diff", "compare"]},
        {"type": "analyze_csv", "difficulty": "medium", "tags": ["awk", "csv", "analysis"]},
        {"type": "log_analysis", "difficulty": "hard", "tags": ["grep", "awk", "logs"]},
        {"type": "complex_text_transform", "difficulty": "hard", "tags": ["sed", "awk", "tr"]},
    ]

    def generate(self, example_id: str) -> Example:
        template = random.choice(self.TEMPLATES)
        method_name = f"_gen_{template['type']}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(example_id, template)
        return self._gen_search_pattern(example_id, template)

    def _gen_search_pattern(self, example_id: str, template: dict) -> Example:
        pattern = random.choice(["TODO", "FIXME", "ERROR", "import", "def ", "class ", "function"])
        directory = random.choice([".", f"./{self.var.directory()}", f"~/{self.var.project_name()}"])
        ext = self.var.code_extension()

        requests = [
            f"Search for '{pattern}' in all {ext} files",
            f"Find all occurrences of '{pattern}'",
            f"Grep for '{pattern}' in the codebase",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"grep -rn '{pattern}' {directory} --include='*{ext}'"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        output = self.out.grep_output(pattern, random.randint(3, 8))
        conversations.append(self.create_tool_result(tool_id, output))

        num_matches = len(output.strip().split("\n"))
        response = f"Found {num_matches} occurrences of `{pattern}`:\n\n"
        for line in output.strip().split("\n")[:5]:
            response += f"- `{line}`\n"
        if num_matches > 5:
            response += f"\n...and {num_matches - 5} more matches."

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["grep"], "easy", template["tags"])

    def _gen_count_lines(self, example_id: str, template: dict) -> Example:
        filepath = f"./{self.var.random_path()}/{self.var.random_filename()}"

        requests = [
            f"Count the lines in {filepath}",
            f"How many lines are in {filepath}?",
            f"wc -l {filepath}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"wc -l {filepath}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        lines = random.randint(50, 2000)
        output = f"  {lines} {filepath}"
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"The file `{filepath}` has **{lines} lines**."
        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["wc"], "easy", template["tags"])

    def _gen_view_file_head(self, example_id: str, template: dict) -> Example:
        filepath = f"./{self.var.random_filename()}"
        num_lines = random.choice([5, 10, 20, 50])

        requests = [
            f"Show me the first {num_lines} lines of {filepath}",
            f"Preview {filepath}",
            f"head -n {num_lines} {filepath}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"head -n {num_lines} {filepath}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        output_lines = [f"# Line {i}: some content here" for i in range(1, num_lines + 1)]
        output = "\n".join(output_lines)
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Here are the first {num_lines} lines of `{filepath}`:\n\n```\n{output[:500]}...\n```"
        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["head"], "easy", template["tags"])

    def _gen_view_file_tail(self, example_id: str, template: dict) -> Example:
        filepath = random.choice(["/var/log/syslog", "./app.log", f"./{self.var.project_name()}.log"])
        num_lines = random.choice([10, 20, 50, 100])
        follow = random.choice([True, False])

        requests = [
            f"Show me the last {num_lines} lines of {filepath}",
            f"Check the recent entries in {filepath}",
            f"tail {filepath}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"tail -n {num_lines} {filepath}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        output_lines = []
        for i in range(num_lines):
            timestamp = f"{self.var.random_date()} {self.var.random_time()}"
            level = random.choice(["INFO", "DEBUG", "WARN", "ERROR"])
            output_lines.append(f"[{timestamp}] {level}: Log message {i}")
        output = "\n".join(output_lines[-10:])
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Here are the last {num_lines} lines of `{filepath}`:\n\n```\n{output}\n```\n\nWould you like me to search for specific patterns in the logs?"
        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["tail"], "easy", template["tags"])

    def _gen_sort_file(self, example_id: str, template: dict) -> Example:
        filepath = f"./{self.var.random_filename('.txt')}"
        reverse = random.choice([True, False])
        numeric = random.choice([True, False])

        requests = [
            f"Sort the contents of {filepath}",
            f"Sort {filepath}" + (" in reverse" if reverse else ""),
            f"Alphabetically sort lines in {filepath}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        flags = ""
        if reverse:
            flags += "r"
        if numeric:
            flags += "n"
        if flags:
            flags = "-" + flags + " "

        cmd = f"sort {flags}{filepath}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        items = ["apple", "banana", "cherry", "date", "elderberry", "fig", "grape"]
        if reverse:
            items = sorted(items, reverse=True)
        else:
            items = sorted(items)
        output = "\n".join(items)
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Here's the sorted content of `{filepath}`:\n\n```\n{output}\n```"
        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["sort"], "easy", template["tags"])

    def _gen_find_replace(self, example_id: str, template: dict) -> Example:
        filepath = f"./{self.var.random_path()}/{self.var.random_filename()}"
        old_text = random.choice(["localhost", "http://", "DEBUG", "old_function", "var ", "TODO"])
        new_text = random.choice(["0.0.0.0", "https://", "INFO", "new_function", "const ", "DONE"])

        requests = [
            f"Replace '{old_text}' with '{new_text}' in {filepath}",
            f"Change all '{old_text}' to '{new_text}'",
            f"sed replace {old_text} -> {new_text} in {filepath}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        # First show what will be replaced
        cmd = f"grep -n '{old_text}' {filepath}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        matches = [f"{random.randint(1, 100)}:    {old_text}_something" for _ in range(random.randint(2, 5))]
        output = "\n".join(matches)
        conversations.append(self.create_tool_result(tool_id, output))

        num_matches = len(matches)
        response = f"Found {num_matches} occurrences of `{old_text}`. Shall I replace them all?"
        conversations.append(self.create_assistant_message(response))
        conversations.append(self.create_user_message("Yes"))

        # Do the replacement
        cmd2 = f"sed -i 's/{old_text}/{new_text}/g' {filepath}"
        tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
        conversations.append(tool_msg2)
        conversations.append(self.create_tool_result(tool_id2, ""))

        response2 = f"Done! Replaced {num_matches} occurrences of `{old_text}` with `{new_text}` in `{filepath}`."
        conversations.append(self.create_assistant_message(response2))

        return self.build_example(example_id, conversations, ["grep", "sed"], "medium", template["tags"])

    def _gen_extract_column(self, example_id: str, template: dict) -> Example:
        filepath = random.choice(["data.csv", "users.csv", "sales.csv", "report.csv"])
        column = random.randint(1, 5)

        requests = [
            f"Extract column {column} from {filepath}",
            f"Show me just the {['first', 'second', 'third', 'fourth', 'fifth'][column-1]} column of {filepath}",
            f"Get column {column} from the CSV",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        # First peek at file
        cmd = f"head -3 {filepath}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        headers = ["id", "name", "email", "amount", "date"]
        output = ",".join(headers) + "\n"
        output += "1,John,john@example.com,100.50,2024-01-01\n"
        output += "2,Jane,jane@example.com,250.00,2024-01-02"
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"I see the CSV has columns: {', '.join(headers)}. Let me extract column {column} ({headers[column-1]})."
        conversations.append(self.create_assistant_message(response))

        cmd2 = f"cut -d',' -f{column} {filepath}"
        tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
        conversations.append(tool_msg2)

        col_data = [headers[column-1]] + [f"value_{i}" for i in range(1, 6)]
        output2 = "\n".join(col_data)
        conversations.append(self.create_tool_result(tool_id2, output2))

        response2 = f"Here's column {column} (`{headers[column-1]}`) from `{filepath}`:\n\n```\n{output2}\n```"
        conversations.append(self.create_assistant_message(response2))

        return self.build_example(example_id, conversations, ["head", "cut"], "medium", template["tags"])

    def _gen_unique_lines(self, example_id: str, template: dict) -> Example:
        filepath = f"./{self.var.random_filename('.txt')}"

        requests = [
            f"Show unique lines in {filepath}",
            f"Remove duplicate lines from {filepath}",
            f"Get distinct values from {filepath}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"sort {filepath} | uniq -c | sort -rn"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        items = [("apple", 5), ("banana", 3), ("cherry", 2), ("date", 1)]
        output = "\n".join([f"   {count} {item}" for item, count in items])
        conversations.append(self.create_tool_result(tool_id, output))

        response = "Here are the unique lines with their occurrence counts:\n\n"
        response += "| Value | Count |\n|-------|-------|\n"
        for item, count in items:
            response += f"| {item} | {count} |\n"

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["sort", "uniq"], "medium", template["tags"], uses_pipes=True)

    def _gen_compare_files(self, example_id: str, template: dict) -> Example:
        file1 = f"./{self.var.random_filename()}"
        file2 = f"./{self.var.random_filename()}"

        requests = [
            f"Compare {file1} and {file2}",
            f"Show differences between {file1} and {file2}",
            f"diff {file1} {file2}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"diff {file1} {file2}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        output = f"""3c3
< old line content
---
> new line content
7a8
> added line
12d12
< removed line"""
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"""Here are the differences between the files:

**Changes:**
- Line 3: Content was modified
- Line 8: A new line was added
- Line 12: A line was removed

Would you like me to show a side-by-side comparison?"""

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["diff"], "medium", template["tags"])

    def _gen_analyze_csv(self, example_id: str, template: dict) -> Example:
        filepath = random.choice(["sales.csv", "data.csv", "transactions.csv"])

        requests = [
            f"Analyze {filepath} and show me summary statistics",
            f"What's the total and average from {filepath}?",
            f"Summarize the data in {filepath}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        # First look at structure
        cmd = f"head -5 {filepath}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        output = """product,quantity,price,date
Widget A,10,29.99,2024-01-01
Widget B,5,49.99,2024-01-02
Gadget X,3,199.99,2024-01-03
Widget A,8,29.99,2024-01-04"""
        conversations.append(self.create_tool_result(tool_id, output))

        response = "I see this is a sales CSV with product, quantity, price, and date columns. Let me calculate some statistics."
        conversations.append(self.create_assistant_message(response))

        # Calculate totals
        cmd2 = f"tail -n +2 {filepath} | awk -F',' '{{sum += $2 * $3; count++}} END {{print \"Total: $\" sum; print \"Rows: \" count; print \"Avg: $\" sum/count}}'"
        tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
        conversations.append(tool_msg2)

        output2 = f"Total: ${random.uniform(5000, 50000):.2f}\nRows: {random.randint(100, 1000)}\nAvg: ${random.uniform(50, 500):.2f}"
        conversations.append(self.create_tool_result(tool_id2, output2))

        response2 = f"Here's the summary for `{filepath}`:\n\n{output2}\n\nWould you like me to break this down by product or date?"
        conversations.append(self.create_assistant_message(response2))

        return self.build_example(example_id, conversations, ["head", "tail", "awk"], "medium", template["tags"], uses_pipes=True)

    def _gen_log_analysis(self, example_id: str, template: dict) -> Example:
        logfile = random.choice(["/var/log/syslog", "/var/log/auth.log", "./app.log", "./server.log"])

        requests = [
            f"Find all errors in {logfile} from today",
            f"Analyze errors in {logfile}",
            f"Show me error statistics from {logfile}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        # Search for errors
        cmd = f"grep -i 'error' {logfile} | tail -20"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        errors = []
        error_types = ["Connection refused", "Timeout", "Permission denied", "File not found", "Invalid input"]
        for _ in range(random.randint(5, 10)):
            timestamp = f"{self.var.random_date()} {self.var.random_time()}"
            error_type = random.choice(error_types)
            errors.append(f"[{timestamp}] ERROR: {error_type}")
        output = "\n".join(errors)
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Found {len(errors)} error entries. Let me categorize them."
        conversations.append(self.create_assistant_message(response))

        # Count by type
        cmd2 = f"grep -i 'error' {logfile} | awk -F'ERROR: ' '{{print $2}}' | sort | uniq -c | sort -rn"
        tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
        conversations.append(tool_msg2)

        counts = [(random.randint(5, 50), e) for e in error_types[:4]]
        output2 = "\n".join([f"   {c} {e}" for c, e in sorted(counts, reverse=True)])
        conversations.append(self.create_tool_result(tool_id2, output2))

        response2 = "Error breakdown:\n\n| Error Type | Count |\n|------------|-------|\n"
        for count, error in sorted(counts, reverse=True):
            response2 += f"| {error} | {count} |\n"
        response2 += "\nThe most common error is at the top. Would you like me to investigate any specific error type?"

        conversations.append(self.create_assistant_message(response2))

        return self.build_example(example_id, conversations, ["grep", "tail", "awk", "sort", "uniq"], "hard", template["tags"], uses_pipes=True)

    def _gen_complex_text_transform(self, example_id: str, template: dict) -> Example:
        filepath = f"./{self.var.random_filename('.txt')}"

        transform_type = random.choice(["lowercase", "remove_whitespace", "extract_emails", "format_json"])

        if transform_type == "lowercase":
            request = f"Convert all text in {filepath} to lowercase"
            cmd = f"tr '[:upper:]' '[:lower:]' < {filepath}"
            output = "this is some lowercase text\nmore lowercase content"
            explanation = "converted all uppercase characters to lowercase"
        elif transform_type == "remove_whitespace":
            request = f"Remove extra whitespace from {filepath}"
            cmd = f"cat {filepath} | tr -s ' ' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//'"
            output = "cleaned text without extra spaces\nnormalized whitespace"
            explanation = "removed extra spaces and trimmed lines"
        elif transform_type == "extract_emails":
            request = f"Extract all email addresses from {filepath}"
            cmd = f"grep -oE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{{2,}}' {filepath}"
            output = "user@example.com\nadmin@company.org\ntest@test.io"
            explanation = "extracted email addresses using regex"
        else:
            request = f"Format the JSON in {filepath} nicely"
            cmd = f"cat {filepath} | python3 -m json.tool"
            output = '{{\n  "name": "test",\n  "value": 123\n}}'
            explanation = "formatted JSON with proper indentation"

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(request))

        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Done! I've {explanation}:\n\n```\n{output}\n```"
        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["tr", "sed", "grep", "cat"], "hard", template["tags"], uses_pipes=True)
