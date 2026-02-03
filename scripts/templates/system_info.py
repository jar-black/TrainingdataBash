"""
System Info & Process Management Templates

Commands: ps, top, htop, kill, killall, pkill, pgrep, bg, fg, nohup, uname, hostname, uptime, whoami, who, w, date, cal, free, lscpu
"""

import random
from .base import BaseTemplateGenerator, Example


class SystemInfoTemplates(BaseTemplateGenerator):
    """Generate system info and process management examples."""

    category = "system_info"

    TEMPLATES = [
        {"type": "check_processes", "difficulty": "easy", "tags": ["ps", "processes"]},
        {"type": "system_info", "difficulty": "easy", "tags": ["uname", "system"]},
        {"type": "memory_usage", "difficulty": "easy", "tags": ["free", "memory"]},
        {"type": "disk_usage", "difficulty": "easy", "tags": ["df", "disk"]},
        {"type": "uptime_check", "difficulty": "easy", "tags": ["uptime"]},
        {"type": "find_process", "difficulty": "medium", "tags": ["pgrep", "ps", "search"]},
        {"type": "kill_process", "difficulty": "medium", "tags": ["kill", "process"]},
        {"type": "cpu_info", "difficulty": "medium", "tags": ["lscpu", "cpu"]},
        {"type": "system_load", "difficulty": "medium", "tags": ["top", "load"]},
        {"type": "run_background", "difficulty": "hard", "tags": ["nohup", "background"]},
        {"type": "resource_hog", "difficulty": "hard", "tags": ["top", "ps", "kill"]},
    ]

    def generate(self, example_id: str) -> Example:
        template = random.choice(self.TEMPLATES)
        method_name = f"_gen_{template['type']}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(example_id, template)
        return self._gen_check_processes(example_id, template)

    def _gen_check_processes(self, example_id: str, template: dict) -> Example:
        requests = [
            "Show me running processes",
            "What processes are running?",
            "ps aux",
            "List all processes",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = "ps aux --sort=-%mem | head -15"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        output = f"""USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.1 169576 13256 ?        Ss   Jan01   0:05 /sbin/init
{self.var.username()}    {self.var.random_pid()}  2.5  8.2 2456780 672340 ?      Sl   10:00   5:23 /usr/bin/python3 app.py
{self.var.username()}    {self.var.random_pid()}  1.2  4.5 1234560 368540 ?      Sl   10:05   2:15 node server.js
root      {self.var.random_pid()}  0.5  2.1 456780 171234 ?      Ss   09:00   0:45 /usr/sbin/nginx
mysql     {self.var.random_pid()}  0.8  3.2 987650 262144 ?      Ssl  Jan01  12:34 /usr/sbin/mysqld"""

        conversations.append(self.create_tool_result(tool_id, output))

        response = """Here are the top processes by memory usage:

| User | PID | CPU% | MEM% | Command |
|------|-----|------|------|---------|
| user | varies | 2.5% | 8.2% | python3 app.py |
| user | varies | 1.2% | 4.5% | node server.js |
| root | varies | 0.5% | 2.1% | nginx |
| mysql | varies | 0.8% | 3.2% | mysqld |

The Python app is using the most memory. Would you like more details about any process?"""

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["ps"], "easy", template["tags"], uses_pipes=True)

    def _gen_system_info(self, example_id: str, template: dict) -> Example:
        requests = [
            "What system am I running?",
            "Show system information",
            "uname -a",
            "What's my OS version?",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = "uname -a"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        output = f"Linux {self.var.username()}-workstation 5.15.0-91-generic #101-Ubuntu SMP x86_64 GNU/Linux"
        conversations.append(self.create_tool_result(tool_id, output))

        response = """Here's your system information:

| Property | Value |
|----------|-------|
| OS | Linux (GNU/Linux) |
| Kernel | 5.15.0-91-generic |
| Architecture | x86_64 (64-bit) |
| Distribution | Ubuntu |

Would you like more detailed information about CPU, memory, or disk?"""

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["uname"], "easy", template["tags"])

    def _gen_memory_usage(self, example_id: str, template: dict) -> Example:
        requests = [
            "How much memory is being used?",
            "Check RAM usage",
            "free -h",
            "Show memory stats",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = "free -h"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        total = random.choice([8, 16, 32, 64])
        used = random.uniform(total * 0.3, total * 0.8)
        output = f"""              total        used        free      shared  buff/cache   available
Mem:           {total}Gi       {used:.1f}Gi       {total - used - 2:.1f}Gi       512Mi        2.0Gi       {total - used:.1f}Gi
Swap:         2.0Gi       0.5Gi       1.5Gi"""

        conversations.append(self.create_tool_result(tool_id, output))

        pct_used = (used / total) * 100
        response = f"""Memory usage summary:

| Type | Total | Used | Available |
|------|-------|------|-----------|
| RAM | {total} GB | {used:.1f} GB ({pct_used:.0f}%) | {total - used:.1f} GB |
| Swap | 2 GB | 0.5 GB | 1.5 GB |

{'Memory usage is healthy.' if pct_used < 70 else 'Memory usage is getting high. Consider closing some applications.'}"""

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["free"], "easy", template["tags"])

    def _gen_disk_usage(self, example_id: str, template: dict) -> Example:
        requests = [
            "Check disk space",
            "How much disk space is left?",
            "df -h",
            "Show storage usage",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = "df -h"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        pct = random.randint(30, 85)
        output = f"""Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1       500G  {pct * 5}G  {(100-pct) * 5}G  {pct}% /
/dev/sdb1       1.0T  400G  600G  40% /data
tmpfs            16G  512M   16G   4% /dev/shm"""

        conversations.append(self.create_tool_result(tool_id, output))

        response = f"""Disk usage summary:

| Mount | Size | Used | Available | Use% |
|-------|------|------|-----------|------|
| / | 500 GB | {pct * 5} GB | {(100-pct) * 5} GB | {pct}% |
| /data | 1.0 TB | 400 GB | 600 GB | 40% |

{'Root partition has plenty of space.' if pct < 70 else 'Root partition is getting full. Consider cleaning up.'}"""

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["df"], "easy", template["tags"])

    def _gen_uptime_check(self, example_id: str, template: dict) -> Example:
        requests = [
            "How long has the system been running?",
            "Check uptime",
            "uptime",
            "When was the last reboot?",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = "uptime"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        days = random.randint(1, 90)
        hours = random.randint(0, 23)
        users = random.randint(1, 5)
        load = [random.uniform(0.1, 2.0) for _ in range(3)]
        output = f" 14:30:00 up {days} days, {hours}:{random.randint(0,59):02d},  {users} users,  load average: {load[0]:.2f}, {load[1]:.2f}, {load[2]:.2f}"

        conversations.append(self.create_tool_result(tool_id, output))

        response = f"""System uptime:

- **Uptime**: {days} days, {hours} hours
- **Users logged in**: {users}
- **Load average**: {load[0]:.2f}, {load[1]:.2f}, {load[2]:.2f} (1, 5, 15 min)

{'System load is normal.' if load[0] < 1.5 else 'System load is elevated.'}"""

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["uptime"], "easy", template["tags"])

    def _gen_find_process(self, example_id: str, template: dict) -> Example:
        process_name = random.choice(["python", "node", "java", "nginx", "mysql", "postgres", "docker"])

        requests = [
            f"Find all {process_name} processes",
            f"Is {process_name} running?",
            f"pgrep {process_name}",
            f"Show me {process_name} processes",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"pgrep -la {process_name}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        pids = [self.var.random_pid() for _ in range(random.randint(1, 4))]
        output = "\n".join([f"{pid} {process_name} {'--some-flag' if random.random() > 0.5 else ''}" for pid in pids])
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Found {len(pids)} `{process_name}` process(es):\n\n"
        for line in output.strip().split("\n"):
            parts = line.split(" ", 1)
            response += f"- PID {parts[0]}: `{parts[1]}`\n"
        response += "\nWould you like to see more details or stop any of these?"

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["pgrep"], "medium", template["tags"])

    def _gen_kill_process(self, example_id: str, template: dict) -> Example:
        process_name = random.choice(["python", "node", "chrome", "firefox"])
        pid = self.var.random_pid()

        requests = [
            f"Kill the {process_name} process",
            f"Stop process {pid}",
            f"Terminate {process_name}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        # Find process first
        cmd = f"pgrep -la {process_name}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        output = f"{pid} {process_name} app.py"
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Found `{process_name}` running with PID {pid}. Shall I terminate it?"
        conversations.append(self.create_assistant_message(response))
        conversations.append(self.create_user_message("Yes"))

        cmd2 = f"kill {pid}"
        tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
        conversations.append(tool_msg2)
        conversations.append(self.create_tool_result(tool_id2, ""))

        # Verify
        cmd3 = f"pgrep {process_name}"
        tool_msg3, tool_id3 = self.create_tool_call_message(cmd3)
        conversations.append(tool_msg3)
        conversations.append(self.create_tool_result(tool_id3, ""))

        response2 = f"Process {pid} (`{process_name}`) has been terminated successfully."
        conversations.append(self.create_assistant_message(response2))

        return self.build_example(example_id, conversations, ["pgrep", "kill"], "medium", template["tags"])

    def _gen_cpu_info(self, example_id: str, template: dict) -> Example:
        requests = [
            "Show CPU information",
            "What processor do I have?",
            "lscpu",
            "CPU details please",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = "lscpu"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        cores = random.choice([4, 8, 12, 16])
        output = f"""Architecture:            x86_64
CPU op-mode(s):          32-bit, 64-bit
CPU(s):                  {cores}
Thread(s) per core:      2
Core(s) per socket:      {cores // 2}
Socket(s):               1
Model name:              Intel(R) Core(TM) i7-{random.randint(10, 13)}700 CPU @ {random.uniform(2.5, 4.0):.2f}GHz
CPU MHz:                 {random.randint(800, 4000)}
CPU max MHz:             {random.randint(4000, 5000)}.0000
L1d cache:               256 KiB
L2 cache:                2 MiB
L3 cache:                16 MiB"""

        conversations.append(self.create_tool_result(tool_id, output))

        response = f"""CPU Information:

| Property | Value |
|----------|-------|
| Architecture | x86_64 (64-bit) |
| CPU Cores | {cores} ({cores // 2} physical, 2 threads each) |
| Model | Intel Core i7 |
| L3 Cache | 16 MiB |

This is a capable multi-core processor suitable for development work."""

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["lscpu"], "medium", template["tags"])

    def _gen_system_load(self, example_id: str, template: dict) -> Example:
        requests = [
            "What's the system load?",
            "Show me top processes",
            "Is the system busy?",
            "top",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = "top -bn1 | head -20"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        load = [random.uniform(0.5, 3.0) for _ in range(3)]
        cpu_user = random.uniform(10, 60)
        cpu_sys = random.uniform(5, 20)
        mem_total = random.choice([16, 32, 64]) * 1024
        mem_used = int(mem_total * random.uniform(0.4, 0.8))

        output = f"""top - 14:30:00 up 10 days,  2:30,  3 users,  load average: {load[0]:.2f}, {load[1]:.2f}, {load[2]:.2f}
Tasks: 250 total,   2 running, 248 sleeping,   0 stopped,   0 zombie
%Cpu(s): {cpu_user:.1f} us, {cpu_sys:.1f} sy,  0.0 ni, {100-cpu_user-cpu_sys:.1f} id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
MiB Mem : {mem_total:>8} total, {mem_total - mem_used:>8} free, {mem_used:>8} used,  2048 buff/cache
MiB Swap:     2048 total,     1536 free,      512 used. {mem_total - mem_used + 1024:>8} avail Mem

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
{self.var.random_pid()} {self.var.username():<9} 20   0 2456780 672340  12340 S  15.0   4.1   5:23.45 python3
{self.var.random_pid()} {self.var.username():<9} 20   0 1234560 368540   8760 S   8.0   2.2   2:15.30 node
{self.var.random_pid()} root      20   0  456780 171234   5432 S   2.0   1.0   0:45.12 nginx"""

        conversations.append(self.create_tool_result(tool_id, output))

        response = f"""System Load Summary:

**Load Average**: {load[0]:.2f}, {load[1]:.2f}, {load[2]:.2f} (1, 5, 15 min)
**CPU**: {cpu_user:.1f}% user, {cpu_sys:.1f}% system, {100-cpu_user-cpu_sys:.1f}% idle
**Memory**: {mem_used} MiB used / {mem_total} MiB total

**Top Processes:**
| Process | CPU% | MEM% |
|---------|------|------|
| python3 | 15.0% | 4.1% |
| node | 8.0% | 2.2% |
| nginx | 2.0% | 1.0% |

{'System is under normal load.' if load[0] < 2 else 'System load is elevated - consider investigating.'}"""

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["top"], "medium", template["tags"], uses_pipes=True)

    def _gen_run_background(self, example_id: str, template: dict) -> Example:
        script = random.choice(["backup.sh", "sync.py", "process_data.py", "build.sh"])

        requests = [
            f"Run {script} in the background",
            f"Start {script} and let it run even if I disconnect",
            f"nohup {script}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"nohup ./{script} > {script}.log 2>&1 &"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        pid = self.var.random_pid()
        output = f"[1] {pid}"
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"""Started `{script}` in the background:

- **PID**: {pid}
- **Log file**: `{script}.log`
- **Status**: Running (will continue even if you disconnect)

You can:
- Check progress: `tail -f {script}.log`
- Check if running: `ps -p {pid}`
- Stop it: `kill {pid}`"""

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["nohup"], "hard", template["tags"])

    def _gen_resource_hog(self, example_id: str, template: dict) -> Example:
        requests = [
            "Something is using all my CPU/memory",
            "Find what's slowing down my system",
            "Which process is hogging resources?",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        # Check top CPU
        cmd = "ps aux --sort=-%cpu | head -5"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        bad_pid = self.var.random_pid()
        bad_process = random.choice(["chrome", "java", "python3", "webpack"])
        output = f"""USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
{self.var.username()}    {bad_pid}  95.2 12.5 3456780 1024000 ?     R    10:00  45:23 {bad_process} --runaway
{self.var.username()}    {self.var.random_pid()}   2.5  4.2 1234560 343000 ?      Sl   10:05   2:15 node server.js
root      {self.var.random_pid()}   0.5  1.1  456780 89000 ?       Ss   09:00   0:45 nginx"""

        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Found the culprit: `{bad_process}` (PID {bad_pid}) is using **95.2% CPU** and 12.5% memory. This appears to be runaway process. Would you like me to terminate it?"
        conversations.append(self.create_assistant_message(response))
        conversations.append(self.create_user_message("Yes, kill it"))

        cmd2 = f"kill -9 {bad_pid}"
        tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
        conversations.append(tool_msg2)
        conversations.append(self.create_tool_result(tool_id2, ""))

        # Verify system is better
        cmd3 = "uptime"
        tool_msg3, tool_id3 = self.create_tool_call_message(cmd3)
        conversations.append(tool_msg3)
        output3 = f" 14:35:00 up 10 days,  2:35,  2 users,  load average: 0.50, 1.20, 2.10"
        conversations.append(self.create_tool_result(tool_id3, output3))

        response2 = f"Terminated the runaway `{bad_process}` process. System load is already dropping (0.50 now vs higher before). Your system should be responsive again."
        conversations.append(self.create_assistant_message(response2))

        return self.build_example(example_id, conversations, ["ps", "kill", "uptime"], "hard", template["tags"], uses_pipes=True)
