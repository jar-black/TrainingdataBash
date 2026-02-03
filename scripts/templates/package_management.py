"""
Package Management Templates

Commands: apt, apt-get, dpkg, pip, npm, snap
"""

import random
from .base import BaseTemplateGenerator, Example


class PackageManagementTemplates(BaseTemplateGenerator):
    """Generate package management examples."""

    category = "package_management"

    TEMPLATES = [
        {"type": "install_system_package", "difficulty": "easy", "tags": ["apt", "install"]},
        {"type": "update_system", "difficulty": "easy", "tags": ["apt", "update"]},
        {"type": "search_package", "difficulty": "easy", "tags": ["apt", "search"]},
        {"type": "install_pip_package", "difficulty": "medium", "tags": ["pip", "python"]},
        {"type": "install_npm_package", "difficulty": "medium", "tags": ["npm", "node"]},
        {"type": "list_installed", "difficulty": "medium", "tags": ["list", "packages"]},
        {"type": "remove_package", "difficulty": "medium", "tags": ["apt", "remove"]},
        {"type": "upgrade_packages", "difficulty": "hard", "tags": ["upgrade", "maintenance"]},
        {"type": "requirements_install", "difficulty": "hard", "tags": ["pip", "requirements"]},
    ]

    def generate(self, example_id: str) -> Example:
        template = random.choice(self.TEMPLATES)
        method_name = f"_gen_{template['type']}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(example_id, template)
        return self._gen_install_system_package(example_id, template)

    def _gen_install_system_package(self, example_id: str, template: dict) -> Example:
        packages = ["htop", "vim", "tmux", "curl", "wget", "jq", "tree", "ncdu", "ripgrep", "fd-find"]
        package = random.choice(packages)

        requests = [
            f"Install {package}",
            f"apt install {package}",
            f"I need {package} installed",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"sudo apt install -y {package}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        output = f"""Reading package lists... Done
Building dependency tree... Done
The following NEW packages will be installed:
  {package}
0 upgraded, 1 newly installed, 0 to remove and 0 not upgraded.
Need to get {random.randint(100, 500)} kB of archives.
Selecting previously unselected package {package}.
Preparing to unpack .../{package}_{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}_amd64.deb ...
Unpacking {package} ...
Setting up {package} ...
Processing triggers for man-db ..."""

        conversations.append(self.create_tool_result(tool_id, output))

        # Verify
        cmd2 = f"which {package}"
        tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
        conversations.append(tool_msg2)
        conversations.append(self.create_tool_result(tool_id2, f"/usr/bin/{package}"))

        response = f"Installed `{package}` successfully. It's now available at `/usr/bin/{package}`."
        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["apt", "which"], "easy", template["tags"])

    def _gen_update_system(self, example_id: str, template: dict) -> Example:
        requests = [
            "Update package lists",
            "apt update",
            "Refresh package database",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = "sudo apt update"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        upgradable = random.randint(0, 20)
        output = f"""Hit:1 http://archive.ubuntu.com/ubuntu jammy InRelease
Get:2 http://archive.ubuntu.com/ubuntu jammy-updates InRelease [119 kB]
Get:3 http://security.ubuntu.com/ubuntu jammy-security InRelease [110 kB]
Fetched 229 kB in 2s (115 kB/s)
Reading package lists... Done
Building dependency tree... Done
{upgradable} packages can be upgraded. Run 'apt list --upgradable' to see them."""

        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Package lists updated. "
        if upgradable > 0:
            response += f"There are {upgradable} packages that can be upgraded. Would you like me to upgrade them?"
        else:
            response += "All packages are up to date!"

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["apt"], "easy", template["tags"])

    def _gen_search_package(self, example_id: str, template: dict) -> Example:
        search_term = random.choice(["json", "python", "docker", "database", "editor"])

        requests = [
            f"Search for packages related to {search_term}",
            f"apt search {search_term}",
            f"Find packages for {search_term}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"apt search {search_term} 2>/dev/null | head -20"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        packages = [
            f"{search_term}-tools/jammy 1.2.3 amd64\n  Tools for working with {search_term}",
            f"lib{search_term}-dev/jammy 2.0.0 amd64\n  Development files for {search_term}",
            f"python3-{search_term}/jammy 3.1.0 all\n  Python bindings for {search_term}",
        ]
        output = "Sorting... Done\nFull Text Search...\n\n" + "\n\n".join(packages)
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Found several packages related to `{search_term}`:\n\n"
        for p in packages:
            name = p.split("/")[0]
            desc = p.split("\n")[1].strip()
            response += f"- **{name}**: {desc}\n"
        response += "\nWould you like me to install any of these?"

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["apt"], "easy", template["tags"], uses_pipes=True)

    def _gen_install_pip_package(self, example_id: str, template: dict) -> Example:
        package = self.var.python_package()

        requests = [
            f"Install {package} with pip",
            f"pip install {package}",
            f"I need the {package} Python package",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"pip install {package}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        version = f"{random.randint(1, 5)}.{random.randint(0, 20)}.{random.randint(0, 10)}"
        output = self.out.pip_install_output(package)
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Installed `{package}` successfully. You can now use it in your Python code with `import {package}`."
        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["pip"], "medium", template["tags"])

    def _gen_install_npm_package(self, example_id: str, template: dict) -> Example:
        package = self.var.node_package()
        global_install = random.choice([True, False])

        requests = [
            f"Install {package}" + (" globally" if global_install else ""),
            f"npm install {package}",
            f"Add {package} to my project",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        flag = "-g " if global_install else ""
        cmd = f"npm install {flag}{package}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        version = f"{random.randint(1, 10)}.{random.randint(0, 20)}.{random.randint(0, 10)}"
        if global_install:
            output = f"added 1 package in 2s\n\n{package}@{version}"
        else:
            output = f"""added {random.randint(10, 100)} packages, and audited {random.randint(100, 500)} packages in 5s

found 0 vulnerabilities"""

        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Installed `{package}@{version}`"
        if global_install:
            response += " globally. It's now available as a command."
        else:
            response += " to your project. It's been added to package.json."

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["npm"], "medium", template["tags"])

    def _gen_list_installed(self, example_id: str, template: dict) -> Example:
        pkg_type = random.choice(["pip", "npm", "apt"])

        requests = [
            f"List installed {pkg_type} packages",
            f"What {pkg_type} packages do I have?",
            f"Show installed packages",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        if pkg_type == "pip":
            cmd = "pip list"
            packages = ["numpy", "pandas", "requests", "flask", "pytest"]
            output = "Package         Version\n--------------- -------\n"
            output += "\n".join([f"{p:<15} {random.randint(1,5)}.{random.randint(0,20)}.{random.randint(0,10)}" for p in packages])
        elif pkg_type == "npm":
            cmd = "npm list --depth=0"
            packages = ["express", "lodash", "axios", "jest"]
            output = f"{self.var.project_name()}@1.0.0\n"
            output += "\n".join([f"├── {p}@{random.randint(1,10)}.{random.randint(0,20)}.{random.randint(0,10)}" for p in packages])
        else:
            cmd = "apt list --installed 2>/dev/null | head -20"
            packages = ["vim", "curl", "git", "python3", "nodejs"]
            output = "Listing...\n"
            output += "\n".join([f"{p}/jammy,now {random.randint(1,5)}.{random.randint(0,20)} amd64 [installed]" for p in packages])

        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Here are your installed {pkg_type} packages:\n\n"
        for p in packages:
            response += f"- {p}\n"

        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, [pkg_type if pkg_type != "apt" else "apt"], "medium", template["tags"])

    def _gen_remove_package(self, example_id: str, template: dict) -> Example:
        package = random.choice(["htop", "vim-tiny", "nano", "tree"])

        requests = [
            f"Remove {package}",
            f"Uninstall {package}",
            f"apt remove {package}",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        cmd = f"sudo apt remove -y {package}"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        output = f"""Reading package lists... Done
Building dependency tree... Done
The following packages will be REMOVED:
  {package}
0 upgraded, 0 newly installed, 1 to remove and 0 not upgraded.
Removing {package} ...
Processing triggers for man-db ..."""

        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Removed `{package}` from your system."
        conversations.append(self.create_assistant_message(response))

        return self.build_example(example_id, conversations, ["apt"], "medium", template["tags"])

    def _gen_upgrade_packages(self, example_id: str, template: dict) -> Example:
        requests = [
            "Upgrade all packages",
            "apt upgrade",
            "Update and upgrade everything",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        # Update first
        cmd = "sudo apt update"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        upgradable = random.randint(5, 15)
        output = f"Fetched 1,234 kB in 2s\n{upgradable} packages can be upgraded."
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Found {upgradable} upgradable packages. Proceeding with upgrade..."
        conversations.append(self.create_assistant_message(response))

        # Upgrade
        cmd2 = "sudo apt upgrade -y"
        tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
        conversations.append(tool_msg2)

        output2 = f"""Reading package lists... Done
Building dependency tree... Done
Calculating upgrade... Done
The following packages will be upgraded:
  package1 package2 package3 ... ({upgradable} total)
{upgradable} upgraded, 0 newly installed, 0 to remove.
Need to get {random.randint(10, 100)} MB of archives.
...(downloading and installing)...
Processing triggers..."""

        conversations.append(self.create_tool_result(tool_id2, output2))

        response2 = f"Upgrade complete! {upgradable} packages were updated to their latest versions."
        conversations.append(self.create_assistant_message(response2))

        return self.build_example(example_id, conversations, ["apt"], "hard", template["tags"])

    def _gen_requirements_install(self, example_id: str, template: dict) -> Example:
        requests = [
            "Install packages from requirements.txt",
            "pip install -r requirements.txt",
            "Install all Python dependencies",
        ]

        conversations = [self.create_system_message()]
        conversations.append(self.create_user_message(random.choice(requests)))

        # Check requirements file
        cmd = "cat requirements.txt"
        tool_msg, tool_id = self.create_tool_call_message(cmd)
        conversations.append(tool_msg)

        packages = ["flask==2.0.1", "requests>=2.25.0", "numpy", "pandas==1.3.0", "pytest"]
        output = "\n".join(packages)
        conversations.append(self.create_tool_result(tool_id, output))

        response = f"Found {len(packages)} packages in requirements.txt. Installing..."
        conversations.append(self.create_assistant_message(response))

        # Install
        cmd2 = "pip install -r requirements.txt"
        tool_msg2, tool_id2 = self.create_tool_call_message(cmd2)
        conversations.append(tool_msg2)

        output2 = """Collecting flask==2.0.1
Collecting requests>=2.25.0
Collecting numpy
Collecting pandas==1.3.0
Collecting pytest
Installing collected packages: numpy, requests, flask, pandas, pytest
Successfully installed flask-2.0.1 numpy-1.21.0 pandas-1.3.0 pytest-6.2.4 requests-2.26.0"""

        conversations.append(self.create_tool_result(tool_id2, output2))

        response2 = f"All {len(packages)} packages from requirements.txt have been installed successfully."
        conversations.append(self.create_assistant_message(response2))

        return self.build_example(example_id, conversations, ["cat", "pip"], "hard", template["tags"])
