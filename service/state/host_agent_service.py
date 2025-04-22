import json
from typing import Tuple, Any

from common.types import Message, Task, Part
from service.client.client import ConversationClient
from service.types import (
    Conversation,
    Event,
    CreateConversationRequest,
    ListConversationRequest,
    SendMessageRequest,
    ListMessageRequest,
    PendingMessageRequest,
    ListTaskRequest,
    RegisterAgentRequest,
    ListAgentRequest,
    GetEventRequest
)
from .state import (
    StateMessage,
    StateConversation,
    StateTask,
    StateEvent
)

server_url = "http://localhost:12000"


async def ListConversations() -> list[Conversation]:
    client = ConversationClient(server_url)
    try:
        response = await client.list_conversation(ListConversationRequest())
        return response.result
    except Exception as e:
        print("Failed to list conversations: ", e)


async def SendMessage(message: Message) -> str | None:
    client = ConversationClient(server_url)
    try:
        response = await client.send_message(SendMessageRequest(params=message))
        return response.result
    except Exception as e:
        print("Failed to send message: ", e)


async def CreateConversation() -> Conversation:
    client = ConversationClient(server_url)
    try:
        response = await client.create_conversation(CreateConversationRequest())
        return response.result
    except Exception as e:
        print("Failed to create conversation", e)


async def ListRemoteAgents():
    client = ConversationClient(server_url)
    try:
        response = await client.list_agents(ListAgentRequest())
        return response.result
    except Exception as e:
        print("Failed to read implementation", e)


async def AddRemoteAgent(path: str):
    client = ConversationClient(server_url)
    try:
        await client.register_agent(RegisterAgentRequest(params=path))
    except Exception as e:
        print("Failed to register the agent", e)


async def GetEvents() -> list[Event]:
    client = ConversationClient(server_url)
    try:
        response = await client.get_events(GetEventRequest())
        return response.result
    except Exception as e:
        print("Failed to get events", e)


async def GetProcessingMessages():
    client = ConversationClient(server_url)
    try:
        response = await client.get_pending_messages(PendingMessageRequest())
        return dict(response.result)
    except Exception as e:
        print("Error getting pending messages", e)


def GetMessageAliases():
    return {}


async def GetTasks():
    client = ConversationClient(server_url)
    try:
        response = await client.list_tasks(ListTaskRequest())
        return response.result
    except Exception as e:
        print("Failed to list tasks ", e)


async def ListMessages(conversation_id: str) -> list[Message]:
    client = ConversationClient(server_url)
    try:
        response = await client.list_messages(ListMessageRequest(params=conversation_id))
        return response.result
    except Exception as e:
        print("Failed to list messages ", e)


def convert_message_to_state(message: Message) -> StateMessage:
    if not message:
        return StateMessage()

    return StateMessage(
        message_id=extract_message_id(message),
        role=message.role,
        content=extract_content(message.parts),
    )


def convert_conversation_to_state(conversation: Conversation) -> StateConversation:
    return StateConversation(
        conversation_id=conversation.conversation_id,
        conversation_name=conversation.name,
        is_active=conversation.is_active,
        message_ids=[extract_message_id(x) for x in conversation.messages],
    )


def convert_task_to_state(task: Task) -> StateTask:
    # Get the first message as the description
    message = task.history[0]
    last_message = task.history[-1]
    output = [extract_content(a.parts) for a in task.artifacts] if task.artifacts else []
    if last_message != message:
        output = [extract_content(last_message.parts)] + output
    return StateTask(
        task_id=task.id,
        session_id=task.sessionId,
        state=str(task.status.state),
        message=convert_message_to_state(message),
        artifacts=output,
    )


def convert_event_to_state(event: Event) -> StateEvent:
    return StateEvent(
        conversation_id=extract_message_conversation(event.content),
        actor=event.actor,
        role=event.content.role,
        content=extract_content(event.content.parts),
    )


def extract_content(message_parts: list[Part]) -> list[Tuple[str | dict[str, Any], str]]:
    parts = []
    if not message_parts:
        return []
    for p in message_parts:
        if p.type == 'text':
            parts.append((p.text, 'text/plain'))
        elif p.type == 'file':
            if p.file.bytes:
                parts.append((p.file.bytes, p.file.mimeType))
            else:
                parts.append((p.file.uri, p.file.mimeType))
        elif p.type == 'data':
            try:
                jsonData = json.dumps(p.data)
                if 'type' in p.data and p.data['type'] == 'form':
                    parts.append((p.data, 'form'))
                else:
                    parts.append((jsonData, 'application/json'))
            except Exception as e:
                print("Failed to dump data", e)
                parts.append(('<data>', 'text/plain'))
    return parts


def extract_message_id(message: Message) -> str:
    if message.metadata and 'message_id' in message.metadata:
        return message.metadata['message_id']
    return ""


def extract_message_conversation(message: Task) -> str:
    if message.metadata and 'conversation_id' in message.metadata:
        return message.metadata['conversation_id']
    return ""


def extract_conversation_id(task: Task) -> str:
    if task.sessionId:
        return task.sessionId
    # Tries to find the first conversation id for the message in the task.
    if (
            task.status.message and
            task.status.message.metadata and
            'conversation_id' in task.status.message.metadata):
        return task.status.message.metadata['conversation_id']
    # Now check if maybe the task has conversation id in metadata.
    if (task.metadata and 'conversation_id' in task.metadata):
        return task.metadata['conversation_id']
    # Now check if any artifacts contain a conversation id.
    if not task.artifacts:
        return ""
    for a in task.artifacts:
        if a.metadata and 'conversation_id' in a.metadata:
            return a.metadata['conversation_id']
    return ""
