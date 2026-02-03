"""
Mixed & Complex Task Templates

Multi-step workflows that combine multiple command categories.
"""

import random
from .base import BaseTemplateGenerator, Example


class MixedComplexTemplates(BaseTemplateGenerator):
    """Generate complex multi-step workflow examples."""

    category = "mixed_complex"

    TEMPLATES = [
        {"type": "deploy_application", "difficulty": "hard", "tags": ["deploy", "git", "process"]},
        {"type": "debug_service", "difficulty": "hard", "tags": ["debug", "logs", "process"]},
        {"type": "setup_project", "difficulty": "hard", "tags": ["setup", "git", "npm", "pip"]},
        {"type": "cleanup_system", "difficulty": "medium", "tags": ["cleanup", "disk", "files"]},
        {"type": "backup_database", "difficulty": "hard", "tags": ["backup", "database", "archive"]},
        {"type": "monitor_resources", "difficulty": "medium", "tags": ["monitor", "system", "process"]},
        {"type": "error_recovery_workflow", "difficulty": "hard", "tags": ["error", "recovery"]},
        {"type": "build_and_test", "difficulty": "hard", "tags": ["build", "test", "ci"]},
    ]

    def generate(self, example_id: str) -> Example:
        template = random.choice(self.TEMPLATES)
        method_name = f"_gen_{template['type']}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(example_id, template)
        return self._gen_deploy_application(example_id, template)

    def _gen_deploy_application(self, example_id: str, template: dict) -> Example:
        project = self.var.project_name()

        requests = [
            f"Deploy the latest version of {project} to production",
            f"Update the production server with the latest code",
            f"Deploy {project}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        # Pull latest
        response1 = "I'll deploy the latest version. First, let me pull the latest code."
        conversations.append(self.create_assistant_message(response1))

        cmd = f"cd ~/{project} && git pull origin main"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        output = f"""Already on 'main'
From github.com:user/{project}
 * branch            main       -> FETCH_HEAD
Updating abc1234..def5678
Fast-forward
 src/app.py | 15 +++++++++++++++
 2 files changed, 15 insertions(+)"""
        conversations.append(self.create_tool_result(tool_id, output))

        # Install dependencies
        cmd2 = f"cd ~/{project} && pip install -r requirements.txt -q"
        tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
        conversations.append(tool_msg2)
        conversations.append(self.create_tool_result(tool_id2, ""))

        # Restart service
        cmd3 = f"sudo systemctl restart {project}"
        tool_msg3, tool_id3 = self.create_tool_call_message(cmd3)
        conversations.append(tool_msg3)
        conversations.append(self.create_tool_result(tool_id3, ""))

        # Check status
        cmd4 = f"sudo systemctl status {project} | head -10"
        tool_msg4, tool_id4 = self.create_tool_call_message(cmd4)
        conversations.append(tool_msg4)

        output4 = f"""● {project}.service - {project.title()} Application
     Loaded: loaded (/etc/systemd/system/{project}.service; enabled)
     Active: active (running) since {self.var.random_date()} {self.var.random_time()}
   Main PID: {self.var.random_pid()} (python3)
      Tasks: 4 (limit: 4915)
     Memory: 128.5M
     CGroup: /system.slice/{project}.service
             └─{self.var.random_pid()} /usr/bin/python3 app.py"""
        conversations.append(self.create_tool_result(tool_id4, output4))

        response2 = f"""Deployment complete!

**Steps completed:**
1. ✓ Pulled latest code from `main`
2. ✓ Updated dependencies
3. ✓ Restarted `{project}` service
4. ✓ Verified service is running

The application is now live with the latest changes."""

        conversations.append(self.create_assistant_message(response2))

        return self.build_example(example_id, conversations, ["git", "pip", "systemctl"], "hard", template["tags"], uses_pipes=True)

    def _gen_debug_service(self, example_id: str, template: dict) -> Example:
        service = random.choice(["api-server", "backend", "webapp", "worker"])

        requests = [
            f"The {service} is not responding, help me debug it",
            f"Debug why {service} is down",
            f"{service} seems to be having issues",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        response1 = f"Let me investigate the `{service}` issue. I'll check if it's running first."
        conversations.append(self.create_assistant_message(response1))

        # Check if running
        cmd = f"pgrep -la {service}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)
        conversations.append(self.create_tool_result(tool_id, ""))

        response2 = f"The service isn't running. Let me check systemd status for more details."
        conversations.append(self.create_assistant_message(response2))

        cmd2 = f"sudo systemctl status {service}"
        tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
        conversations.append(tool_msg2)

        output2 = f"""● {service}.service - {service.title()} Service
     Loaded: loaded (/etc/systemd/system/{service}.service; enabled)
     Active: failed (Result: exit-code) since {self.var.random_date()} {self.var.random_time()}
    Process: {self.var.random_pid()} ExecStart=/usr/bin/python3 /app/main.py (code=exited, status=1/FAILURE)
   Main PID: {self.var.random_pid()} (code=exited, status=1/FAILURE)"""
        conversations.append(self.create_tool_result(tool_id2, output2))

        # Check logs
        cmd3 = f"sudo journalctl -u {service} --no-pager -n 20"
        tool_msg3, tool_id3 = self.create_tool_call_message(cmd3)
        conversations.append(tool_msg3)

        output3 = f"""-- Logs begin at {self.var.random_date()} --
{self.var.random_date()} {self.var.random_time()} {service}[{self.var.random_pid()}]: Starting {service}...
{self.var.random_date()} {self.var.random_time()} {service}[{self.var.random_pid()}]: Error: Cannot connect to database at localhost:5432
{self.var.random_date()} {self.var.random_time()} {service}[{self.var.random_pid()}]: Connection refused
{self.var.random_date()} {self.var.random_time()} systemd[1]: {service}.service: Main process exited, code=exited, status=1/FAILURE"""
        conversations.append(self.create_tool_result(tool_id3, output3))

        response3 = "Found the issue - the service can't connect to the database. Let me check if PostgreSQL is running."
        conversations.append(self.create_assistant_message(response3))

        cmd4 = "sudo systemctl status postgresql"
        tool_msg4, tool_id4 = self.create_tool_call_message(cmd4)
        conversations.append(tool_msg4)

        output4 = """● postgresql.service - PostgreSQL RDBMS
     Active: inactive (dead)"""
        conversations.append(self.create_tool_result(tool_id4, output4))

        cmd5 = "sudo systemctl start postgresql"
        tool_msg5, tool_id5 = self.create_tool_call_message(cmd5)
        conversations.append(tool_msg5)
        conversations.append(self.create_tool_result(tool_id5, ""))

        cmd6 = f"sudo systemctl start {service}"
        tool_msg6, tool_id6 = self.create_tool_call_message(cmd6)
        conversations.append(tool_msg6)
        conversations.append(self.create_tool_result(tool_id6, ""))

        cmd7 = f"sudo systemctl status {service} | head -5"
        tool_msg7, tool_id7 = self.create_tool_call_message(cmd7)
        conversations.append(tool_msg7)

        output7 = f"""● {service}.service - {service.title()} Service
     Active: active (running) since {self.var.random_date()} {self.var.random_time()}"""
        conversations.append(self.create_tool_result(tool_id7, output7))

        response4 = f"""Issue resolved!

**Root cause:** PostgreSQL database was not running, causing `{service}` to fail on startup.

**Fix applied:**
1. Started PostgreSQL: `systemctl start postgresql`
2. Started {service}: `systemctl start {service}`

Both services are now running. Consider adding a dependency in the systemd unit file so PostgreSQL starts before {service}."""

        conversations.append(self.create_assistant_message(response4))

        return self.build_example(example_id, conversations, ["pgrep", "systemctl", "journalctl"], "hard", template["tags"], has_error_recovery=True, uses_pipes=True)

    def _gen_setup_project(self, example_id: str, template: dict) -> Example:
        project = self.var.project_name()
        project_type = random.choice(["python", "node"])

        requests = [
            f"Set up a new {project_type} project called {project}",
            f"Create a new {project_type} project",
            f"Initialize {project} as a {project_type} project",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        # Create directory
        cmd = f"mkdir -p {project} && cd {project}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)
        conversations.append(self.create_tool_result(tool_id, ""))

        if project_type == "python":
            # Git init
            cmd2 = f"cd {project} && git init"
            tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
            conversations.append(tool_msg2)
            conversations.append(self.create_tool_result(tool_id2, f"Initialized empty Git repository in /home/user/{project}/.git/"))

            # Create venv
            cmd3 = f"cd {project} && python3 -m venv venv"
            tool_msg3, tool_id3 = self.create_tool_call_message(cmd3)
            conversations.append(tool_msg3)
            conversations.append(self.create_tool_result(tool_id3, ""))

            # Create files
            cmd4 = f"cd {project} && touch requirements.txt main.py && echo '# {project}' > README.md"
            tool_msg4, tool_id4 = self.create_tool_call_message(cmd4)
            conversations.append(tool_msg4)
            conversations.append(self.create_tool_result(tool_id4, ""))

            # Create .gitignore
            cmd5 = f"cd {project} && echo -e 'venv/\\n__pycache__/\\n*.pyc\\n.env' > .gitignore"
            tool_msg5, tool_id5 = self.create_tool_call_message(cmd5)
            conversations.append(tool_msg5)
            conversations.append(self.create_tool_result(tool_id5, ""))

            response = f"""Created Python project `{project}`:

```
{project}/
├── .git/
├── .gitignore
├── README.md
├── main.py
├── requirements.txt
└── venv/
```

**Next steps:**
1. Activate venv: `source {project}/venv/bin/activate`
2. Add dependencies to `requirements.txt`
3. Start coding in `main.py`"""

        else:  # node
            cmd2 = f"cd {project} && git init && npm init -y"
            tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
            conversations.append(tool_msg2)
            conversations.append(self.create_tool_result(tool_id2, "Wrote to package.json"))

            cmd3 = f"cd {project} && touch index.js && echo '# {project}' > README.md"
            tool_msg3, tool_id3 = self.create_tool_call_message(cmd3)
            conversations.append(tool_msg3)
            conversations.append(self.create_tool_result(tool_id3, ""))

            cmd4 = f"cd {project} && echo -e 'node_modules/\\n.env\\n*.log' > .gitignore"
            tool_msg4, tool_id4 = self.create_tool_call_message(cmd4)
            conversations.append(tool_msg4)
            conversations.append(self.create_tool_result(tool_id4, ""))

            response = f"""Created Node.js project `{project}`:

```
{project}/
├── .git/
├── .gitignore
├── README.md
├── index.js
└── package.json
```

**Next steps:**
1. Install dependencies: `npm install express`
2. Start coding in `index.js`
3. Run with: `node index.js`"""

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["mkdir", "git", "touch", "echo"], "hard", template["tags"])

    def _gen_cleanup_system(self, example_id: str, template: dict) -> Example:
        requests = [
            "Clean up disk space on this system",
            "Free up some disk space",
            "The disk is getting full, help me clean up",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        # Check current usage
        cmd = "df -h /"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        used_pct = random.randint(75, 95)
        output = f"""Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1       100G  {used_pct}G  {100-used_pct}G  {used_pct}% /"""
        conversations.append(self.create_tool_result(tool_id, output))

        response1 = f"Disk is at {used_pct}% usage. Let me clean up several areas."
        conversations.append(self.create_assistant_message(response1))

        # Clean apt cache
        cmd2 = "sudo apt autoremove -y && sudo apt clean"
        tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
        conversations.append(tool_msg2)
        conversations.append(self.create_tool_result(tool_id2, f"Removing {random.randint(5, 20)} unused packages..."))

        # Clean old logs
        cmd3 = "sudo journalctl --vacuum-time=7d"
        tool_msg3, tool_id3 = self.create_tool_call_message(cmd3)
        conversations.append(tool_msg3)
        conversations.append(self.create_tool_result(tool_id3, f"Vacuuming done, freed {random.randint(100, 500)}M"))

        # Clean temp files
        cmd4 = "sudo rm -rf /tmp/* /var/tmp/* 2>/dev/null; echo 'Cleaned temp files'"
        tool_msg4, tool_id4 = self.create_tool_call_message(cmd4)
        conversations.append(tool_msg4)
        conversations.append(self.create_tool_result(tool_id4, "Cleaned temp files"))

        # Check new usage
        cmd5 = "df -h /"
        tool_msg5, tool_id5 = self.create_tool_call_message(cmd5)
        conversations.append(tool_msg5)

        new_used = used_pct - random.randint(5, 15)
        output5 = f"""Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1       100G  {new_used}G  {100-new_used}G  {new_used}% /"""
        conversations.append(self.create_tool_result(tool_id5, output5))

        freed = used_pct - new_used
        response2 = f"""Cleanup complete! Freed approximately {freed}GB.

**Actions taken:**
- Removed unused apt packages
- Cleaned apt cache
- Removed old journal logs (>7 days)
- Cleared temp files

**Disk usage:** {used_pct}% → {new_used}%"""

        conversations.append(self.create_assistant_message(response2))

        return self.build_example(example_id, conversations, ["df", "apt", "journalctl", "rm"], "medium", template["tags"])

    def _gen_backup_database(self, example_id: str, template: dict) -> Example:
        db_name = random.choice(["production_db", "app_database", "main_db"])
        backup_dir = "/backups/databases"

        requests = [
            f"Create a backup of the {db_name} database",
            f"Backup {db_name} to {backup_dir}",
            f"I need a database dump of {db_name}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        # Create backup directory
        cmd = f"sudo mkdir -p {backup_dir}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)
        conversations.append(self.create_tool_result(tool_id, ""))

        # Create dump
        date = self.var.random_date()
        backup_file = f"{backup_dir}/{db_name}_{date}.sql"
        cmd2 = f"sudo -u postgres pg_dump {db_name} > {backup_file}"
        tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
        conversations.append(tool_msg2)
        conversations.append(self.create_tool_result(tool_id2, ""))

        # Compress
        cmd3 = f"gzip {backup_file}"
        tool_msg3, tool_id3 = self.create_tool_call_message(cmd3)
        conversations.append(tool_msg3)
        conversations.append(self.create_tool_result(tool_id3, ""))

        # Verify
        cmd4 = f"ls -lh {backup_file}.gz"
        tool_msg4, tool_id4 = self.create_tool_call_message(cmd4)
        conversations.append(tool_msg4)

        size = f"{random.randint(10, 500)}M"
        output4 = f"-rw-r--r-- 1 root root {size} {date} {backup_file}.gz"
        conversations.append(self.create_tool_result(tool_id4, output4))

        response = f"""Database backup complete!

**Backup details:**
- Database: `{db_name}`
- File: `{backup_file}.gz`
- Size: {size} (compressed)

**To restore:**
```bash
gunzip {backup_file}.gz
sudo -u postgres psql {db_name} < {backup_file}
```"""

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["mkdir", "pg_dump", "gzip", "ls"], "hard", template["tags"])

    def _gen_monitor_resources(self, example_id: str, template: dict) -> Example:
        requests = [
            "Show me a system resource overview",
            "What's the current system status?",
            "Monitor system resources",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        # CPU
        cmd = "uptime"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        load = [random.uniform(0.5, 3.0) for _ in range(3)]
        output = f" 14:30:00 up 15 days, 3:45,  2 users,  load average: {load[0]:.2f}, {load[1]:.2f}, {load[2]:.2f}"
        conversations.append(self.create_tool_result(tool_id, output))

        # Memory
        cmd2 = "free -h"
        tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
        conversations.append(tool_msg2)

        total_mem = random.choice([16, 32, 64])
        used_mem = random.uniform(total_mem * 0.3, total_mem * 0.8)
        output2 = f"""              total        used        free
Mem:           {total_mem}Gi       {used_mem:.1f}Gi       {total_mem - used_mem:.1f}Gi
Swap:         2.0Gi       0.1Gi       1.9Gi"""
        conversations.append(self.create_tool_result(tool_id2, output2))

        # Disk
        cmd3 = "df -h / /data 2>/dev/null | tail -n +2"
        tool_msg3, tool_id3 = self.create_tool_call_message(cmd3)
        conversations.append(tool_msg3)

        output3 = f"""/dev/sda1       200G  {random.randint(50, 150)}G  {random.randint(30, 100)}G  {random.randint(40, 80)}%  /
/dev/sdb1       500G  {random.randint(100, 400)}G  {random.randint(50, 200)}G  {random.randint(30, 70)}%  /data"""
        conversations.append(self.create_tool_result(tool_id3, output3))

        # Top processes
        cmd4 = "ps aux --sort=-%cpu | head -5"
        tool_msg4, tool_id4 = self.create_tool_call_message(cmd4)
        conversations.append(tool_msg4)

        output4 = f"""USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
{self.var.username()}  {self.var.random_pid()}  {random.uniform(5, 25):.1f}  {random.uniform(2, 8):.1f} 2456780 672340 ?      Sl   10:00   5:23 python3 app.py
{self.var.username()}  {self.var.random_pid()}  {random.uniform(2, 10):.1f}  {random.uniform(1, 5):.1f} 1234560 368540 ?      Sl   10:05   2:15 node server.js
root      {self.var.random_pid()}  {random.uniform(0.5, 3):.1f}  {random.uniform(0.5, 2):.1f}  456780 171234 ?      Ss   09:00   0:45 nginx"""
        conversations.append(self.create_tool_result(tool_id4, output4))

        mem_pct = (used_mem / total_mem) * 100
        response = f"""## System Status

**Load Average:** {load[0]:.2f}, {load[1]:.2f}, {load[2]:.2f} (1, 5, 15 min)
**Uptime:** 15 days

**Memory:** {used_mem:.1f}G / {total_mem}G ({mem_pct:.0f}% used)

**Top Processes by CPU:**
1. python3 app.py
2. node server.js
3. nginx

**Status:** {'⚠️ Load is elevated' if load[0] > 2 else '✓ System healthy'}"""

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["uptime", "free", "df", "ps"], "medium", template["tags"], uses_pipes=True)

    def _gen_error_recovery_workflow(self, example_id: str, template: dict) -> Example:
        operation = random.choice(["disk_full", "service_crash", "permission_issue"])

        if operation == "disk_full":
            requests = ["The disk is full and the application crashed", "No space left on device error"]

            conversations = [self.create_system_message()]
            conversations.append(self.create_user_message(random.choice(requests)))

            cmd = "df -h /"
            tool_msg, tool_id = self.create_tool_call_message(cmd)
            conversations.append(tool_msg)
            output = "/dev/sda1       100G  100G     0 100% /"
            conversations.append(self.create_tool_result(tool_id, output))

            response1 = "Disk is 100% full. Let me find and clean up the largest files."
            conversations.append(self.create_assistant_message(response1))

            cmd2 = "sudo find /var/log -name '*.log' -size +100M -exec ls -lh {} \\; 2>/dev/null | head -5"
            tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
            conversations.append(tool_msg2)
            output2 = f"""-rw-r--r-- 1 root root 5.2G {self.var.random_date()} /var/log/syslog.1
-rw-r--r-- 1 root root 2.1G {self.var.random_date()} /var/log/app.log"""
            conversations.append(self.create_tool_result(tool_id2, output2))

            cmd3 = "sudo truncate -s 0 /var/log/syslog.1 /var/log/app.log"
            tool_msg3, tool_id3 = self.create_tool_call_message(cmd3)
            conversations.append(tool_msg3)
            conversations.append(self.create_tool_result(tool_id3, ""))

            cmd4 = "df -h /"
            tool_msg4, tool_id4 = self.create_tool_call_message(cmd4)
            conversations.append(tool_msg4)
            output4 = "/dev/sda1       100G   92G    8G  92% /"
            conversations.append(self.create_tool_result(tool_id4, output4))

            response2 = """Recovered 8GB of disk space by truncating large log files!

**Actions taken:**
- Identified large log files (syslog.1: 5.2G, app.log: 2.1G)
- Truncated logs to 0 bytes (preserving file handles)
- Disk now at 92% instead of 100%

Consider setting up log rotation to prevent this in the future."""

        else:  # permission_issue
            requests = ["Getting permission denied when trying to run the application", "Can't start app due to permissions"]

            conversations = [self.create_system_message()]
            conversations.append(self.create_user_message(random.choice(requests)))

            cmd = "./app.py"
            tool_msg, tool_id = self.create_tool_call_message(cmd)
            conversations.append(tool_msg)
            output = "bash: ./app.py: Permission denied"
            conversations.append(self.create_tool_result(tool_id, output))

            cmd2 = "ls -la app.py"
            tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
            conversations.append(tool_msg2)
            output2 = f"-rw-r--r-- 1 {self.var.username()} {self.var.username()} 1234 {self.var.random_date()} app.py"
            conversations.append(self.create_tool_result(tool_id2, output2))

            response1 = "The file doesn't have execute permission. Let me fix that."
            conversations.append(self.create_assistant_message(response1))

            cmd3 = "chmod +x app.py"
            tool_msg3, tool_id3 = self.create_tool_call_message(cmd3)
            conversations.append(tool_msg3)
            conversations.append(self.create_tool_result(tool_id3, ""))

            cmd4 = "./app.py"
            tool_msg4, tool_id4 = self.create_tool_call_message(cmd4)
            conversations.append(tool_msg4)
            output4 = "Application started successfully on port 8080"
            conversations.append(self.create_tool_result(tool_id4, output4))

            response2 = """Fixed! The issue was missing execute permission.

**Problem:** File had `rw-r--r--` (644) - no execute bit
**Solution:** Added execute permission with `chmod +x`

The application is now running on port 8080."""

        conversations.append(self.create_assistant_message(response2))

        return self.build_example(example_id, conversations, ["df", "find", "truncate", "chmod"], "hard", template["tags"], has_error_recovery=True)

    def _gen_build_and_test(self, example_id: str, template: dict) -> Example:
        project = self.var.project_name()

        requests = [
            f"Build and test {project}",
            f"Run the full CI pipeline locally",
            f"Build, test, and lint the code",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        response1 = "I'll run the full build pipeline: install dependencies, lint, test, and build."
        conversations.append(self.create_assistant_message(response1))

        # Install
        cmd = "npm install"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)
        output = f"added {random.randint(100, 300)} packages in 5s"
        conversations.append(self.create_tool_result(tool_id, output))

        # Lint
        cmd2 = "npm run lint"
        tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
        conversations.append(tool_msg2)
        output2 = f"✓ {random.randint(20, 50)} files linted, 0 errors, 0 warnings"
        conversations.append(self.create_tool_result(tool_id2, output2))

        # Test
        cmd3 = "npm test"
        tool_msg3, tool_id3 = self.create_tool_call_message(cmd3)
        conversations.append(tool_msg3)

        tests_passed = random.randint(30, 100)
        output3 = f"""PASS  src/tests/unit.test.js
PASS  src/tests/integration.test.js

Test Suites: 5 passed, 5 total
Tests:       {tests_passed} passed, {tests_passed} total
Snapshots:   0 total
Time:        {random.uniform(5, 15):.2f}s"""
        conversations.append(self.create_tool_result(tool_id3, output3))

        # Build
        cmd4 = "npm run build"
        tool_msg4, tool_id4 = self.create_tool_call_message(cmd4)
        conversations.append(tool_msg4)

        output4 = f"""Creating an optimized production build...
Compiled successfully.

File sizes after gzip:
  {random.randint(50, 200)} KB  build/static/js/main.js
  {random.randint(10, 50)} KB   build/static/css/main.css"""
        conversations.append(self.create_tool_result(tool_id4, output4))

        response2 = f"""Build pipeline complete!

| Stage | Status |
|-------|--------|
| Install | ✓ {random.randint(100, 300)} packages |
| Lint | ✓ No errors |
| Test | ✓ {tests_passed} tests passed |
| Build | ✓ Production build ready |

The build artifacts are in `./build/`"""

        conversations.append(self.create_assistant_message(response2))

        return self.build_example(example_id, conversations, ["npm"], "hard", template["tags"])
