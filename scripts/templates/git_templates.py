"""
Git Version Control Templates

Commands: git init, clone, add, commit, push, pull, status, log, diff, branch, checkout, merge, rebase, stash, reset
"""

import random
from .base import BaseTemplateGenerator, Example


class GitTemplates(BaseTemplateGenerator):
    """Generate git operations examples."""

    category = "git"

    TEMPLATES = [
        {"type": "check_status", "difficulty": "easy", "tags": ["status"]},
        {"type": "view_log", "difficulty": "easy", "tags": ["log", "history"]},
        {"type": "show_diff", "difficulty": "easy", "tags": ["diff"]},
        {"type": "create_branch", "difficulty": "easy", "tags": ["branch"]},
        {"type": "stage_and_commit", "difficulty": "medium", "tags": ["add", "commit"]},
        {"type": "push_changes", "difficulty": "medium", "tags": ["push"]},
        {"type": "pull_changes", "difficulty": "medium", "tags": ["pull"]},
        {"type": "stash_changes", "difficulty": "medium", "tags": ["stash"]},
        {"type": "merge_branch", "difficulty": "hard", "tags": ["merge"]},
        {"type": "undo_commit", "difficulty": "hard", "tags": ["reset", "revert"]},
        {"type": "resolve_conflict", "difficulty": "hard", "tags": ["merge", "conflict"]},
        {"type": "clone_and_setup", "difficulty": "medium", "tags": ["clone"]},
    ]

    def generate(self, example_id: str) -> Example:
        template = random.choice(self.TEMPLATES)
        method_name = f"_gen_{template['type']}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(example_id, template)
        return self._gen_check_status(example_id, template)

    def _gen_check_status(self, example_id: str, template: dict) -> Example:
        requests = [
            "What's the git status?",
            "Show me uncommitted changes",
            "git status",
            "Check if there are any changes to commit",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        tool_msg, tool_id = self.create_tool_call_message("git status")
        conversations.append(tool_msg)

        output = self.out.git_status_output(modified=random.randint(1, 4), untracked=random.randint(0, 2))
        conversations.append(self.create_tool_result(tool_id, output))

        branch = self.var.git_branch()
        response = f"You're on branch `{branch}`. "
        if "modified" in output:
            response += "There are modified files that haven't been staged. "
        if "Untracked" in output:
            response += "There are also untracked files. "
        response += "Would you like me to stage and commit these changes?"

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["git status"], "easy", template["tags"])

    def _gen_view_log(self, example_id: str, template: dict) -> Example:
        num_commits = random.choice([3, 5, 10])

        requests = [
            f"Show me the last {num_commits} commits",
            "View git history",
            "git log",
            "What commits were made recently?",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"git log --oneline -n {num_commits}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        output = self.out.git_log_output(num_commits)
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Here are the last {num_commits} commits:\n\n"
        for line in output.strip().split("\n"):
            parts = line.split(" ", 1)
            response += f"- `{parts[0]}` - {parts[1]}\n"

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["git log"], "easy", template["tags"])

    def _gen_show_diff(self, example_id: str, template: dict) -> Example:
        staged = random.choice([True, False])

        requests = [
            "Show me what changed",
            "git diff",
            "What are my current changes?",
            "Show uncommitted changes",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = "git diff" + (" --staged" if staged else "")
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        filepath = f"{self.var.directory()}/{self.var.random_filename()}"
        output = f"""diff --git a/{filepath} b/{filepath}
index abc123..def456 100644
--- a/{filepath}
+++ b/{filepath}
@@ -10,6 +10,8 @@ def some_function():
     existing_code()
+    # New code added
+    new_functionality()
     more_code()
-    removed_line()
"""
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Here are your {'staged' if staged else 'unstaged'} changes:\n\n"
        response += f"**{filepath}:**\n"
        response += "- Added 2 lines (new functionality)\n"
        response += "- Removed 1 line\n\n"
        response += "Would you like to commit these changes?"

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["git diff"], "easy", template["tags"])

    def _gen_create_branch(self, example_id: str, template: dict) -> Example:
        branch_type = random.choice(["feature", "bugfix", "hotfix"])
        branch_name = f"{branch_type}/{random.choice(['user-auth', 'api-v2', 'fix-login', 'add-tests', 'update-deps'])}"

        requests = [
            f"Create a new branch called {branch_name}",
            f"Start a new {branch_type} branch",
            f"git checkout -b {branch_name}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"git checkout -b {branch_name}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        output = f"Switched to a new branch '{branch_name}'"
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Done! Created and switched to new branch `{branch_name}`. You can now start making changes for your {branch_type}."
        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["git checkout"], "easy", template["tags"])

    def _gen_stage_and_commit(self, example_id: str, template: dict) -> Example:
        commit_messages = [
            "Add user authentication feature",
            "Fix bug in payment processing",
            "Update dependencies to latest versions",
            "Refactor database queries for performance",
            "Add unit tests for API endpoints",
        ]
        message = random.choice(commit_messages)

        requests = [
            "Commit all my changes",
            f"Stage and commit with message: {message}",
            "Save my changes to git",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        # First check status
        tool_msg, tool_id = self.create_tool_call_message("git status")
        conversations.append(tool_msg)
        output = self.out.git_status_output(modified=random.randint(1, 3), untracked=random.randint(0, 1))
        conversations.append(self.create_tool_result(tool_id, output))

        response = "I see some changes. Let me stage and commit them."
        conversations.append(self.create_assistant_message(response))

        # Stage
        tool_msg2, tool_id2 = self.create_tool_call_message("git add -A")
        conversations.append(tool_msg2)
        conversations.append(self.create_tool_result(tool_id2, ""))

        # Commit
        tool_msg3, tool_id3 = self.create_tool_call_message(f"git commit -m '{message}'")
        conversations.append(tool_msg3)

        files_changed = random.randint(1, 5)
        insertions = random.randint(10, 100)
        deletions = random.randint(0, 50)
        output3 = f"[{self.var.git_branch()} {self.var.random_commit_hash()}] {message}\n {files_changed} files changed, {insertions} insertions(+), {deletions} deletions(-)"
        conversations.append(self.create_tool_result(tool_id3, output3))

        response2 = f"Committed successfully!\n\n- **Message**: {message}\n- **Files changed**: {files_changed}\n- **Changes**: +{insertions} / -{deletions}\n\nWould you like me to push this to the remote?"
        conversations.append(self.create_assistant_message(response2))

        return self.build_example(example_id, conversations, ["git status", "git add", "git commit"], "medium", template["tags"])

    def _gen_push_changes(self, example_id: str, template: dict) -> Example:
        branch = self.var.git_branch()

        requests = [
            "Push my changes",
            f"Push to {branch}",
            "git push",
            "Upload my commits to GitHub",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"git push origin {branch}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        output = f"""Enumerating objects: 5, done.
Counting objects: 100% (5/5), done.
Delta compression using up to 8 threads
Compressing objects: 100% (3/3), done.
Writing objects: 100% (3/3), 1.23 KiB | 1.23 MiB/s, done.
Total 3 (delta 2), reused 0 (delta 0)
To github.com:user/repo.git
   abc1234..def5678  {branch} -> {branch}"""
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Pushed successfully to `origin/{branch}`! Your changes are now on the remote repository."
        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["git push"], "medium", template["tags"])

    def _gen_pull_changes(self, example_id: str, template: dict) -> Example:
        branch = self.var.git_branch()

        requests = [
            "Pull latest changes",
            f"Update my local {branch}",
            "git pull",
            "Get the latest code",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"git pull origin {branch}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        files = [f"{self.var.directory()}/{self.var.random_filename()}" for _ in range(random.randint(1, 4))]
        output = f"""remote: Enumerating objects: 10, done.
remote: Counting objects: 100% (10/10), done.
remote: Compressing objects: 100% (6/6), done.
Unpacking objects: 100% (6/6), done.
From github.com:user/repo
   abc1234..def5678  {branch} -> origin/{branch}
Updating abc1234..def5678
Fast-forward
 {chr(10).join([f' {f} | {random.randint(1, 50)} {"+" * random.randint(1, 10)}' for f in files])}
 {len(files)} files changed, {random.randint(20, 100)} insertions(+), {random.randint(5, 30)} deletions(-)"""
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Pulled latest changes from `origin/{branch}`. {len(files)} files were updated."
        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["git pull"], "medium", template["tags"])

    def _gen_stash_changes(self, example_id: str, template: dict) -> Example:
        action = random.choice(["save", "pop", "list"])

        if action == "save":
            requests = ["Stash my current changes", "Save changes for later", "git stash"]
            cmd = "git stash"
            output = f"Saved working directory and index state WIP on {self.var.git_branch()}: {self.var.random_commit_hash()} Last commit message"
            response = "Your changes have been stashed. Your working directory is now clean. Use `git stash pop` to restore them later."
        elif action == "pop":
            requests = ["Restore my stashed changes", "Apply stash", "git stash pop"]
            cmd = "git stash pop"
            output = f"""On branch {self.var.git_branch()}
Changes not staged for commit:
  modified:   {self.var.directory()}/{self.var.random_filename()}
Dropped refs/stash@{{0}} (abc123def456)"""
            response = "Restored your stashed changes. The stash has been removed from the stash list."
        else:
            requests = ["Show my stashes", "List stashed changes", "git stash list"]
            cmd = "git stash list"
            output = f"""stash@{{0}}: WIP on {self.var.git_branch()}: {self.var.random_commit_hash()} Feature work
stash@{{1}}: WIP on main: {self.var.random_commit_hash()} Bug fix attempt"""
            response = "You have 2 stashed changesets. Use `git stash pop` to apply the most recent one, or `git stash apply stash@{n}` for a specific one."

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)
        conversations.append(self.create_tool_result(tool_id, output))
        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["git stash"], "medium", template["tags"])

    def _gen_merge_branch(self, example_id: str, template: dict) -> Example:
        source_branch = f"feature/{random.choice(['user-auth', 'api-v2', 'new-feature'])}"
        target_branch = "main"

        requests = [
            f"Merge {source_branch} into {target_branch}",
            f"Complete the merge of {source_branch}",
            f"git merge {source_branch}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        # Switch to target
        tool_msg, tool_id = self.create_tool_call_message(f"git checkout {target_branch}")
        conversations.append(tool_msg)
        output = f"Switched to branch '{target_branch}'"
        conversations.append(self.create_tool_result(tool_id, output))

        # Merge
        tool_msg2, tool_id2 = self.create_tool_call_message(f"git merge {source_branch}")
        conversations.append(tool_msg2)

        output2 = f"""Updating {self.var.random_commit_hash()}..{self.var.random_commit_hash()}
Fast-forward
 {self.var.directory()}/{self.var.random_filename()} | {random.randint(10, 50)} {"+" * 10}
 {self.var.directory()}/{self.var.random_filename()} | {random.randint(5, 20)} {"+" * 5}{"-" * 3}
 2 files changed, {random.randint(30, 80)} insertions(+), {random.randint(5, 20)} deletions(-)"""
        conversations.append(self.create_tool_result(tool_id2, output2))

        response = f"Successfully merged `{source_branch}` into `{target_branch}`. The merge was a fast-forward, no conflicts encountered."
        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["git checkout", "git merge"], "hard", template["tags"])

    def _gen_undo_commit(self, example_id: str, template: dict) -> Example:
        keep_changes = random.choice([True, False])

        requests = [
            "Undo my last commit" + (" but keep the changes" if keep_changes else ""),
            "Reset the last commit",
            "I need to undo my last commit",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        # Show last commit
        tool_msg, tool_id = self.create_tool_call_message("git log --oneline -1")
        conversations.append(tool_msg)
        output = f"{self.var.random_commit_hash()} Last commit message here"
        conversations.append(self.create_tool_result(tool_id, output))

        reset_type = "--soft" if keep_changes else "--hard"
        explanation = "keeping your changes staged" if keep_changes else "discarding all changes"

        response = f"I'll undo the last commit, {explanation}."
        conversations.append(self.create_assistant_message(response))

        tool_msg2, tool_id2 = self.create_tool_call_message(f"git reset {reset_type} HEAD~1")
        conversations.append(tool_msg2)
        conversations.append(self.create_tool_result(tool_id2, ""))

        if keep_changes:
            tool_msg3, tool_id3 = self.create_tool_call_message("git status")
            conversations.append(tool_msg3)
            output3 = self.out.git_status_output(modified=2, untracked=0)
            conversations.append(self.create_tool_result(tool_id3, output3))

        response2 = f"Done! The last commit has been undone. "
        if keep_changes:
            response2 += "Your changes are still staged and ready to be committed again with a different message or after modifications."
        else:
            response2 += "All changes from that commit have been discarded."

        conversations.append(self.create_assistant_message(response2))

        return self.build_example(example_id, conversations, ["git log", "git reset", "git status"], "hard", template["tags"])

    def _gen_resolve_conflict(self, example_id: str, template: dict) -> Example:
        branch = f"feature/{random.choice(['new-feature', 'update'])}"

        requests = [
            f"I have merge conflicts after merging {branch}",
            "Help me resolve git conflicts",
            "There are conflicts I need to fix",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        # Check status
        tool_msg, tool_id = self.create_tool_call_message("git status")
        conversations.append(tool_msg)
        conflict_file = f"{self.var.directory()}/{self.var.random_filename()}"
        output = f"""On branch main
You have unmerged paths.
  (fix conflicts and run "git commit")

Unmerged paths:
  (use "git add <file>..." to mark resolution)
	both modified:   {conflict_file}"""
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"I see there's a conflict in `{conflict_file}`. Let me show you the conflicting sections."
        conversations.append(self.create_assistant_message(response))

        # Show conflict
        tool_msg2, tool_id2 = self.create_tool_call_message(f"cat {conflict_file}")
        conversations.append(tool_msg2)
        output2 = f"""some code here
<<<<<<< HEAD
current_implementation()
=======
new_implementation()
>>>>>>> {branch}
more code"""
        conversations.append(self.create_tool_result(tool_id2, output2))

        response2 = """Found the conflict markers. You need to choose between:
- `current_implementation()` (your current branch)
- `new_implementation()` (incoming from feature branch)

Which version would you like to keep, or should I keep both?"""
        conversations.append(self.create_assistant_message(response2))

        conversations.append(self.create_user_message("Keep the new implementation"))

        # Resolve
        tool_msg3, tool_id3 = self.create_tool_call_message(f"sed -i '/<<<<<<< HEAD/,/=======/d' {conflict_file} && sed -i '/>>>>>>> /d' {conflict_file}")
        conversations.append(tool_msg3)
        conversations.append(self.create_tool_result(tool_id3, ""))

        tool_msg4, tool_id4 = self.create_tool_call_message(f"git add {conflict_file}")
        conversations.append(tool_msg4)
        conversations.append(self.create_tool_result(tool_id4, ""))

        response3 = f"Resolved! I kept the new implementation and marked `{conflict_file}` as resolved. Run `git commit` to complete the merge."
        conversations.append(self.create_assistant_message(response3))

        return self.build_example(example_id, conversations, ["git status", "cat", "sed", "git add"], "hard", template["tags"], has_error_recovery=True)

    def _gen_clone_and_setup(self, example_id: str, template: dict) -> Example:
        repo = f"github.com/{self.var.username()}/{self.var.project_name()}"

        requests = [
            f"Clone {repo}",
            f"Get the code from {repo}",
            f"git clone https://{repo}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"git clone https://{repo}.git"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        project = self.var.project_name()
        output = f"""Cloning into '{project}'...
remote: Enumerating objects: 150, done.
remote: Counting objects: 100% (150/150), done.
remote: Compressing objects: 100% (100/100), done.
Receiving objects: 100% (150/150), 1.5 MiB | 5.0 MiB/s, done.
Resolving deltas: 100% (50/50), done."""
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Cloned successfully into `./{project}/`. Let me check what's in the repository."
        conversations.append(self.create_assistant_message(response))

        tool_msg2, tool_id2 = self.create_tool_call_message(f"ls -la {project}/")
        conversations.append(tool_msg2)
        output2 = self.out.ls_output(num_files=5, show_hidden=True)
        conversations.append(self.create_tool_result(tool_id2, output2))

        response2 = f"Repository cloned to `./{project}/`. Would you like me to install dependencies or set up the development environment?"
        conversations.append(self.create_assistant_message(response2))

        return self.build_example(example_id, conversations, ["git clone", "ls"], "medium", template["tags"])
