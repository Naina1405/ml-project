from agent.graph import agent_graph

def test_agent_simple_flow():
    state = {
        "user_input": "Find three machine learning courses and compare them",
        "user_id": "test_user",
        "execution_trace": []
    }
    result = agent_graph.invoke(state)
    assert result.get("task_status") == "COMPLETED"
    assert len(result.get("execution_trace", [])) > 0

def test_agent_sensitive_action_approval():
    state = {
        "user_input": "Send an email to prof.smith@edu regarding my grade",
        "user_id": "test_user",
        "execution_trace": []
    }
    result = agent_graph.invoke(state)
    assert result.get("task_status") == "AWAITING_APPROVAL"
    assert result.get("requires_approval") is True
