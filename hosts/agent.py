from typing import Union

import click
from fastapi import APIRouter
from google.adk.models.base_llm import BaseLlm
from starlette.middleware.cors import CORSMiddleware

from common.server import A2AServer
from common.types import AgentCard, AgentCapabilities
from hosts.multiagent.agent_task_manager import AgentTaskManager
from hosts.multiagent.host_agent import HostAgent
from service.server.manager.adk_host_manager import ADKHostManager
from service.server.manager.application_manager import ApplicationManager
from service.server.server import ConversationServer


class A2AHost:
    _host_agent: HostAgent
    _a2a_server: A2AServer
    _application_manager: ApplicationManager
    _conversation_server: ConversationServer

    def __init__(self, host: int, port: int, llm: Union[str, BaseLlm] = "gemini-2.0-flash-001"):
        self._host_agent: HostAgent = HostAgent([])
        llm_agent = self._host_agent.create_agent(model=llm)

        capabilities = AgentCapabilities(streaming=True)
        agent_card = AgentCard(
            name="HostAgent",
            description="This is the Host agent coordinating other agents using A2A.",
            url=f"http://{host}:{port}/",
            version="1.0.0",
            defaultInputModes=["text", "text/plain"],
            defaultOutputModes=["text", "text/plain"],
            capabilities=capabilities,
            skills=[],
        )

        self._a2a_server = A2AServer(
            agent_card=agent_card,
            task_manager=AgentTaskManager(agent=llm_agent),
            host=host,
            port=port,
        )

        app = self._a2a_server.app
        router = APIRouter()
        self._application_manager: ApplicationManager = ADKHostManager(
            host_agent=self._host_agent
        )

        self._conversation_server = ConversationServer(
            router=router,
            application_manager=self._application_manager
        )
        app.include_router(router)

        # Note: local use only
        self._a2a_server.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self._a2a_server.start()


@click.command()
@click.option("--host", default="localhost")
@click.option("--port", default=10008)
def main(host, port):
    A2AHost(host, port)


if __name__ == "__main__":
    main()
