from controllers.agent_Controller import AgentRequestPayload


def test_agent_request_payload_allows_missing_conversation_id():
    payload = AgentRequestPayload(prompt="hello")

    assert payload.prompt == "hello"
    assert payload.conversationId == ""
