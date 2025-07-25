from langgraph.graph import StateGraph, END
from service.agent_service.state.state import AgentState
from service.agent_service.nodes.call_model import call_model
from service.agent_service.nodes.call_tool import tool_executor
from service.agent_service.nodes.should_continue import should_continue

# --- 4. Xây dựng Graph ---
workflow = StateGraph(AgentState)

workflow.add_node("agent", call_model)
workflow.add_node("action", tool_executor)

workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        True: "action",
        False: END
    }
)

workflow.add_edge("action", "agent")

app = workflow.compile()
