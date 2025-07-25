from service.agent_service.state.state import AgentState
from service.agent_service.llm_provider.toolset import llm_with_tool

def call_model(state: AgentState):
    """Hàm gọi LLM để nhận câu trả lời hoặc quyết định sử dụng tool."""
    messages = state['messages']
    model = llm_with_tool
    response = model.invoke(messages)
    return {"messages": [response]}
