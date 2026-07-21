import asyncio
from unittest.mock import patch

from graph.router import router_node


class FakeStructuredModel:
    def __init__(self, selected_agent: str):
        self.selected_agent = selected_agent

    def with_structured_output(self, schema):
        return self

    def invoke(self, messages):
        class Decision:
            selected_agent = self.selected_agent

        return Decision()


def test_router_node_uses_model_without_awaiting_it():
    with patch("graph.router.get_model", return_value=FakeStructuredModel("chat")):
        result = asyncio.run(
            router_node({"prompt": "hello", "messages": []})
        )

    assert result["agent"] == "chat"
