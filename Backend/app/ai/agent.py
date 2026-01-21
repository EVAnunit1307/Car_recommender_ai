from __future__ import annotations

import os
from typing import Dict

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI

from app.ai.memory import get_memory
from app.ai.prompts import SYSTEM_PROMPT
from app.ai.tools import build_tools


_EXECUTORS: Dict[str, AgentExecutor] = {}


def _build_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ]
    )


def _build_llm() -> ChatGoogleGenerativeAI:
    model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    return ChatGoogleGenerativeAI(model=model, temperature=0.2)


def get_agent_executor(session_id: str) -> AgentExecutor:
    executor = _EXECUTORS.get(session_id)
    if executor:
        return executor
    tools = build_tools()
    prompt = _build_prompt()
    llm = _build_llm()
    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, memory=get_memory(session_id))
    _EXECUTORS[session_id] = executor
    return executor


def run_agent(session_id: str, message: str) -> str:
    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY is not set.")
    executor = get_agent_executor(session_id)
    result = executor.invoke({"input": message})
    return result.get("output", "")
