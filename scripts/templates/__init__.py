"""
Template generators for each command category.
"""

from .file_operations import FileOperationsTemplates
from .text_processing import TextProcessingTemplates
from .git_templates import GitTemplates
from .system_info import SystemInfoTemplates
from .network import NetworkTemplates
from .archive import ArchiveTemplates
from .package_management import PackageManagementTemplates
from .permissions import PermissionsTemplates
from .user_environment import UserEnvironmentTemplates
from .mixed_complex import MixedComplexTemplates

__all__ = [
    "FileOperationsTemplates",
    "TextProcessingTemplates",
    "GitTemplates",
    "SystemInfoTemplates",
    "NetworkTemplates",
    "ArchiveTemplates",
    "PackageManagementTemplates",
    "PermissionsTemplates",
    "UserEnvironmentTemplates",
    "MixedComplexTemplates",
]
