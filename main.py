from common.server import A2AServer
from common.types import AgentCard, AgentCapabilities
from hosts.multiagent.agent_task_manager import AgentTaskManager
from hosts.multiagent.host_agent import HostAgent
from starlette.middleware.cors import CORSMiddleware
import click
from fastapi import FastAPI, APIRouter
from service.server.server import ConversationServer


@click.command()
@click.option("--host", default="localhost")
@click.option("--port", default=10008)
def main(host, port):
    initial_remote_agents = []
    host_agent: HostAgent = HostAgent(initial_remote_agents)
    llm_agent = host_agent.create_agent()

    # host_agent.register_remote_agent("http://localhost:10000")

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

    server = A2AServer(
        agent_card=agent_card,
        task_manager=AgentTaskManager(agent=llm_agent),
        host=host,
        port=port,
    )

    app = server.app
    router = APIRouter()
    ConversationServer(router)
    app.include_router(router)

    # Note: local use only
    server.app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    server.start()


if __name__ == "__main__":
    main()
