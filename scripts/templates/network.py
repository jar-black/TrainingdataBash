"""
Network Templates

Commands: curl, wget, ssh, scp, rsync, ping, netstat, ss, ifconfig, ip, host, dig
"""

import random
from .base import BaseTemplateGenerator, Example


class NetworkTemplates(BaseTemplateGenerator):
    """Generate network operation examples."""

    category = "network"

    TEMPLATES = [
        {"type": "check_connectivity", "difficulty": "easy", "tags": ["ping"]},
        {"type": "download_file", "difficulty": "easy", "tags": ["wget", "curl"]},
        {"type": "check_ports", "difficulty": "easy", "tags": ["ss", "netstat"]},
        {"type": "dns_lookup", "difficulty": "easy", "tags": ["dig", "host"]},
        {"type": "http_request", "difficulty": "medium", "tags": ["curl", "api"]},
        {"type": "check_ip", "difficulty": "medium", "tags": ["ip", "ifconfig"]},
        {"type": "transfer_file", "difficulty": "medium", "tags": ["scp", "rsync"]},
        {"type": "api_call", "difficulty": "medium", "tags": ["curl", "json", "api"]},
        {"type": "debug_connection", "difficulty": "hard", "tags": ["curl", "debug"]},
        {"type": "sync_remote", "difficulty": "hard", "tags": ["rsync", "sync"]},
    ]

    def generate(self, example_id: str) -> Example:
        template = random.choice(self.TEMPLATES)
        method_name = f"_gen_{template['type']}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(example_id, template)
        return self._gen_check_connectivity(example_id, template)

    def _gen_check_connectivity(self, example_id: str, template: dict) -> Example:
        target = random.choice(["google.com", "8.8.8.8", "github.com", "api.example.com"])

        requests = [
            f"Check if {target} is reachable",
            f"Ping {target}",
            f"Test connection to {target}",
            f"Is {target} up?",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"ping -c 4 {target}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        avg_time = random.uniform(10, 100)
        output = f"""PING {target} ({self.var.random_ip()}) 56(84) bytes of data.
64 bytes from {target}: icmp_seq=1 ttl=64 time={avg_time:.1f} ms
64 bytes from {target}: icmp_seq=2 ttl=64 time={avg_time + random.uniform(-5, 5):.1f} ms
64 bytes from {target}: icmp_seq=3 ttl=64 time={avg_time + random.uniform(-5, 5):.1f} ms
64 bytes from {target}: icmp_seq=4 ttl=64 time={avg_time + random.uniform(-5, 5):.1f} ms

--- {target} ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3004ms
rtt min/avg/max/mdev = {avg_time - 5:.1f}/{avg_time:.1f}/{avg_time + 5:.1f}/2.5 ms"""

        conversations.append(self.create_tool_result(tool_id, output))

        response = f"""`{target}` is reachable!

- **Packets**: 4 sent, 4 received (0% loss)
- **Response time**: ~{avg_time:.0f}ms average
- **Status**: Connection is healthy"""

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["ping"], "easy", template["tags"])

    def _gen_download_file(self, example_id: str, template: dict) -> Example:
        filename = random.choice(["data.csv", "archive.tar.gz", "installer.sh", "config.json"])
        url = f"https://example.com/files/{filename}"

        requests = [
            f"Download {url}",
            f"wget {url}",
            f"Get the file from {url}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        use_curl = random.choice([True, False])
        if use_curl:
            cmd = f"curl -LO {url}"
            output = self.out.curl_download_output(random.uniform(1, 20))
        else:
            cmd = f"wget {url}"
            size_mb = random.uniform(1, 20)
            output = f"""--{self.var.random_date()} {self.var.random_time()}--  {url}
Resolving example.com... {self.var.random_ip()}
Connecting to example.com... connected.
HTTP request sent, awaiting response... 200 OK
Length: {int(size_mb * 1024 * 1024)} ({size_mb:.1f}M) [application/octet-stream]
Saving to: '{filename}'

{filename}           100%[===================>]  {size_mb:.1f}M  {random.uniform(1, 10):.1f}MB/s    in {random.uniform(0.5, 5):.1f}s

{self.var.random_date()} {self.var.random_time()} (5.0 MB/s) - '{filename}' saved [{int(size_mb * 1024 * 1024)}]"""

        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Downloaded `{filename}` successfully. The file is now in your current directory."
        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["curl" if use_curl else "wget"], "easy", template["tags"])

    def _gen_check_ports(self, example_id: str, template: dict) -> Example:
        requests = [
            "What ports are open on this system?",
            "Show listening ports",
            "ss -tlnp",
            "Check what services are running",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = "ss -tlnp"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        services = [
            ("22", "sshd"),
            ("80", "nginx"),
            ("443", "nginx"),
            ("3000", "node"),
            ("5432", "postgres"),
            ("6379", "redis-server"),
        ]
        random.shuffle(services)
        selected = services[:random.randint(3, 5)]

        lines = ["State    Recv-Q   Send-Q     Local Address:Port     Peer Address:Port  Process"]
        for port, proc in selected:
            lines.append(f"LISTEN   0        128        0.0.0.0:{port}          0.0.0.0:*      users:((\"{proc}\",pid={self.var.random_pid()},fd=3))")

        output = "\n".join(lines)
        conversations.append(self.create_tool_result(tool_id, output))

        response = "Here are the listening ports:\n\n| Port | Service |\n|------|--------|\n"
        for port, proc in selected:
            response += f"| {port} | {proc} |\n"
        response += "\nWould you like to check any specific port in detail?"

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["ss"], "easy", template["tags"])

    def _gen_dns_lookup(self, example_id: str, template: dict) -> Example:
        domain = random.choice(["google.com", "github.com", "api.example.com", "mail.company.org"])

        requests = [
            f"Look up DNS for {domain}",
            f"What's the IP of {domain}?",
            f"dig {domain}",
            f"Resolve {domain}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"dig +short {domain}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        ips = [self.var.random_ip() for _ in range(random.randint(1, 3))]
        output = "\n".join(ips)
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"DNS lookup for `{domain}`:\n\n"
        for ip in ips:
            response += f"- {ip}\n"
        if len(ips) > 1:
            response += f"\nMultiple IPs indicate load balancing or redundancy."

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["dig"], "easy", template["tags"])

    def _gen_http_request(self, example_id: str, template: dict) -> Example:
        url = random.choice([
            "https://api.example.com/health",
            "http://localhost:8080/status",
            "https://httpbin.org/get",
        ])

        requests = [
            f"Check if {url} is responding",
            f"Get the response from {url}",
            f"curl {url}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"curl -s {url}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        output = '{"status": "healthy", "version": "2.1.0", "uptime": "3d 12h"}'
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"""Response from `{url}`:

```json
{output}
```

The service is healthy and running version 2.1.0."""

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["curl"], "medium", template["tags"])

    def _gen_check_ip(self, example_id: str, template: dict) -> Example:
        requests = [
            "What's my IP address?",
            "Show network interface info",
            "ip addr",
            "Check my network configuration",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = "ip addr show"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        local_ip = f"192.168.1.{random.randint(2, 254)}"
        output = f"""1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536
    inet 127.0.0.1/8 scope host lo
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500
    inet {local_ip}/24 brd 192.168.1.255 scope global eth0
    inet6 fe80::1/64 scope link"""

        conversations.append(self.create_tool_result(tool_id, output))

        response = f"""Network interfaces:

| Interface | IP Address | Type |
|-----------|------------|------|
| lo | 127.0.0.1 | Loopback |
| eth0 | {local_ip} | Ethernet |

Your primary IP is `{local_ip}` on the eth0 interface."""

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["ip"], "medium", template["tags"])

    def _gen_transfer_file(self, example_id: str, template: dict) -> Example:
        filename = self.var.random_filename()
        remote_host = f"server.{self.var.project_name()}.com"
        remote_user = self.var.username()

        requests = [
            f"Copy {filename} to {remote_host}",
            f"Transfer {filename} to the remote server",
            f"scp {filename} {remote_user}@{remote_host}:",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"scp {filename} {remote_user}@{remote_host}:~/"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        size_kb = random.randint(10, 5000)
        output = f"{filename}                           100% {size_kb}KB   {random.uniform(1, 10):.1f}MB/s   00:00"
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Successfully transferred `{filename}` ({size_kb} KB) to `{remote_user}@{remote_host}:~/`"
        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["scp"], "medium", template["tags"])

    def _gen_api_call(self, example_id: str, template: dict) -> Example:
        method = random.choice(["GET", "POST", "PUT"])
        endpoint = random.choice(["/users", "/products", "/orders", "/api/data"])
        base_url = "https://api.example.com"

        requests = [
            f"Make a {method} request to {base_url}{endpoint}",
            f"Call the {endpoint} API",
            f"Fetch data from {endpoint}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        if method == "GET":
            cmd = f"curl -s {base_url}{endpoint}"
            output = '{"data": [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}], "total": 2}'
        elif method == "POST":
            cmd = f"curl -s -X POST {base_url}{endpoint} -H 'Content-Type: application/json' -d '{{\"name\": \"New Item\"}}'"
            output = '{"id": 3, "name": "New Item", "created_at": "2024-01-15T10:30:00Z"}'
        else:
            cmd = f"curl -s -X PUT {base_url}{endpoint}/1 -H 'Content-Type: application/json' -d '{{\"name\": \"Updated Item\"}}'"
            output = '{"id": 1, "name": "Updated Item", "updated_at": "2024-01-15T10:30:00Z"}'

        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"API {method} request successful:\n\n```json\n{output}\n```"
        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["curl"], "medium", template["tags"])

    def _gen_debug_connection(self, example_id: str, template: dict) -> Example:
        url = random.choice([
            "https://api.example.com/health",
            "https://broken-service.com/status",
        ])

        requests = [
            f"Debug connection issues with {url}",
            f"Why can't I connect to {url}?",
            f"Troubleshoot {url} connection",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        # First try basic curl
        cmd = f"curl -v {url} 2>&1 | head -30"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        is_error = random.choice([True, False])
        if is_error:
            output = f"""*   Trying {self.var.random_ip()}:443...
* Connection timed out after 10000 milliseconds
* Closing connection 0
curl: (28) Connection timed out"""
            response = "The connection is timing out. Let me check DNS and routing."
        else:
            output = f"""*   Trying {self.var.random_ip()}:443...
* Connected to api.example.com ({self.var.random_ip()}) port 443
* SSL connection using TLSv1.3
> GET /health HTTP/2
< HTTP/2 200
< content-type: application/json"""
            response = "Connection is working. SSL handshake succeeded and got HTTP 200."

        conversations.append(self.create_tool_result(tool_id, output))
        conversations.append(self.create_assistant_message(response))

        if is_error:
            # Check DNS
            cmd2 = f"dig +short {url.split('/')[2]}"
            tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
            conversations.append(tool_msg2)

            output2 = self.var.random_ip()
            conversations.append(self.create_tool_result(tool_id2, output2))

            # Check if port is blocked
            cmd3 = f"nc -zv {url.split('/')[2]} 443 -w 5 2>&1"
            tool_msg3, tool_id3 = self.create_tool_call_message(cmd3)
            conversations.append(tool_msg3)

            output3 = f"nc: connect to {url.split('/')[2]} port 443 (tcp) timed out: Operation now in progress"
            conversations.append(self.create_tool_result(tool_id3, output3))

            response2 = f"""Diagnosis:
- **DNS**: Resolving correctly to {output2}
- **Port 443**: Connection times out

This suggests either:
1. Firewall blocking outbound HTTPS
2. The remote server is down
3. Network routing issues

Try checking your firewall rules or contacting the service provider."""
            conversations.append(self.create_assistant_message(response2))

        return self.build_example(example_id, conversations, ["curl", "dig", "nc"], "hard", template["tags"], uses_pipes=True, has_error_recovery=is_error)

    def _gen_sync_remote(self, example_id: str, template: dict) -> Example:
        local_dir = f"./{self.var.project_name()}"
        remote_host = f"server.example.com"
        remote_dir = f"/var/www/{self.var.project_name()}"

        requests = [
            f"Sync {local_dir} to {remote_host}:{remote_dir}",
            f"Deploy files to {remote_host}",
            f"rsync my project to the server",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        # Dry run first
        cmd = f"rsync -avhn --delete {local_dir}/ {self.var.username()}@{remote_host}:{remote_dir}/"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        files = [f"{self.var.directory()}/{self.var.random_filename()}" for _ in range(random.randint(3, 8))]
        output = f"""sending incremental file list
{chr(10).join(files)}
deleting old_file.txt

sent 2,345 bytes  received 234 bytes  5,158.00 bytes/sec
total size is 1,234,567  speedup is 478.23 (DRY RUN)"""

        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Dry run complete. Will sync {len(files)} files and delete 1 obsolete file. Proceed?"
        conversations.append(self.create_assistant_message(response))
        conversations.append(self.create_user_message("Yes"))

        # Actual sync
        cmd2 = f"rsync -avh --delete {local_dir}/ {self.var.username()}@{remote_host}:{remote_dir}/"
        tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
        conversations.append(tool_msg2)

        output2 = output.replace("(DRY RUN)", "")
        conversations.append(self.create_tool_result(tool_id2, output2))

        response2 = f"Sync complete! {len(files)} files transferred to `{remote_host}:{remote_dir}/`"
        conversations.append(self.create_assistant_message(response2))

        return self.build_example(example_id, conversations, ["rsync"], "hard", template["tags"])
