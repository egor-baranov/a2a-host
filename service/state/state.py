import dataclasses
from typing import Literal, Tuple, Any

from pydantic.dataclasses import dataclass

ContentPart = str | dict[str, Any]


@dataclass
class StateConversation:
    """StateConversation provides state compliant view of a conversation"""
    conversation_id: str = ""
    conversation_name: str = ""
    is_active: bool = True
    message_ids: list[str] = dataclasses.field(default_factory=list)


@dataclass
class StateMessage:
    """StateMessage provides state compliant view of a message"""
    message_id: str = ""
    role: str = ""
    # Each content entry is a content, media type pair.
    content: list[Tuple[ContentPart, str]] = dataclasses.field(default_factory=list)


@dataclass
class StateTask:
    """StateTask provides state compliant view of task"""
    task_id: str = ""
    session_id: str | None = None
    state: str | None = None
    message: StateMessage = dataclasses.field(default_factory=StateMessage)
    artifacts: list[list[Tuple[ContentPart, str]]] = dataclasses.field(default_factory=list)


@dataclass
class SessionTask:
    """SessionTask organizes tasks based on conversation"""
    session_id: str = ""
    task: StateTask = dataclasses.field(default_factory=StateTask)


@dataclass
class StateEvent:
    """StateEvent provides state compliant view of event"""
    conversation_id: str = ""
    actor: str = ""
    role: str = ""
    id: str = ""
    # Each entry is a pair of (content, media type)
    content: list[Tuple[ContentPart, str]] = dataclasses.field(default_factory=list)
