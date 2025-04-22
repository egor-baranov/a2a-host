from common.client import A2ACardResolver
from common.types import AgentCard


def get_agent_card(remote_agent_address: str) -> AgentCard:
    """Get the agent card."""
    card_resolver = A2ACardResolver(remote_agent_address)
    agent_card = card_resolver.get_agent_card()
    return agent_card
