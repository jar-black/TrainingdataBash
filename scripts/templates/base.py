"""
Base template class for all category generators.
"""

import random
import json
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Tuple


@dataclass
class ToolCall:
    """Represents a tool call."""
    id: str
    type: str = "function"
    function: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def create_bash_call(cls, command: str) -> "ToolCall":
        return cls(
            id=f"call_{uuid.uuid4().hex[:8]}",
            type="function",
            function={
                "name": "bash",
                "arguments": json.dumps({"command": command})
            }
        )


@dataclass
class Message:
    """Represents a conversation message."""
    role: str
    content: Optional[str] = None
    tool_calls: Optional[List[Dict]] = None
    tool_call_id: Optional[str] = None

    def to_dict(self) -> Dict:
        result = {"role": self.role}
        if self.content is not None:
            result["content"] = self.content
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls
            result["content"] = None
        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id
        return result


@dataclass
class Example:
    """Represents a training example."""
    id: str
    conversations: List[Message]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "conversations": [msg.to_dict() for msg in self.conversations],
            "metadata": self.metadata
        }


class BaseTemplateGenerator(ABC):
    """Base class for category template generators."""

    category: str = "base"
    commands_used: List[str] = []

    def __init__(self, var_gen, out_gen, config: Dict):
        self.var = var_gen
        self.out = out_gen
        self.config = config
        self.system_prompts = config.get("system_prompts", [
            "You are a helpful assistant with access to a bash tool for executing commands on a Linux system."
        ])

    def get_system_prompt(self) -> str:
        return random.choice(self.system_prompts)

    def create_tool_call_message(self, command: str) -> Tuple[Message, str]:
        """Create assistant message with tool call and return (message, tool_call_id)."""
        tool_call = ToolCall.create_bash_call(command)
        msg = Message(
            role="assistant",
            content=None,
            tool_calls=[asdict(tool_call)]
        )
        return msg, tool_call.id

    def create_tool_result(self, tool_call_id: str, output: str) -> Message:
        """Create tool result message."""
        return Message(role="tool", content=output, tool_call_id=tool_call_id)

    def create_user_message(self, content: str) -> Message:
        return Message(role="user", content=content)

    def create_assistant_message(self, content: str) -> Message:
        return Message(role="assistant", content=content)

    def create_system_message(self) -> Message:
        return Message(role="system", content=self.get_system_prompt())

    def get_difficulty(self) -> str:
        """Get random difficulty based on config distribution."""
        diff_config = self.config.get("difficulty", {"easy": 0.3, "medium": 0.5, "hard": 0.2})
        r = random.random()
        cumulative = 0
        for diff, prob in diff_config.items():
            cumulative += prob
            if r < cumulative:
                return diff
        return "medium"

    @abstractmethod
    def generate(self, example_id: str) -> Example:
        """Generate a single example."""
        pass

    def build_example(
        self,
        example_id: str,
        conversations: List[Message],
        commands_used: List[str],
        difficulty: str,
        tags: List[str] = None,
        has_error_recovery: bool = False,
        uses_pipes: bool = False,
    ) -> Example:
        """Build an Example object with metadata."""
        return Example(
            id=example_id,
            conversations=conversations,
            metadata={
                "category": self.category,
                "commands_used": commands_used,
                "difficulty": difficulty,
                "turns": len([m for m in conversations if m.role in ("user", "assistant")]),
                "has_error_recovery": has_error_recovery,
                "uses_pipes": uses_pipes,
                "tags": tags or [],
            }
        )
