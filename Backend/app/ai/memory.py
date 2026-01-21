from __future__ import annotations

from threading import Lock
from typing import Dict, List

from langchain.memory import ConversationBufferMemory


_MEMORY_LOCK = Lock()
_MEMORIES: Dict[str, ConversationBufferMemory] = {}


def get_memory(session_id: str) -> ConversationBufferMemory:
    with _MEMORY_LOCK:
        memory = _MEMORIES.get(session_id)
        if memory is None:
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
            )
            _MEMORIES[session_id] = memory
        return memory


def reset_memory(session_id: str) -> None:
    with _MEMORY_LOCK:
        _MEMORIES.pop(session_id, None)


def get_history(session_id: str) -> List[Dict[str, str]]:
    memory = _MEMORIES.get(session_id)
    if not memory:
        return []
    history: List[Dict[str, str]] = []
    for message in memory.chat_memory.messages:
        role = "assistant" if message.type == "ai" else "user"
        history.append({"role": role, "content": message.content})
    return history
