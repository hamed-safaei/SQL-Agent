from app.agent.schemas.states import AgentState 

def build_metadata(state: AgentState):
    mode = state.get("mode")

    mapping = {
        "chat": [
            "mode",
            "message",
        ],
        "sql": [
            "mode",
            "sql",
        ],
        "result": [
            "mode",
            "result",
        ],
        "full": [
            "mode",
            "intro_message",
            "sql_message",
            "sql",
            "result",
            "analysis",
        ],
    }

    fields = mapping.get(mode, ["mode"])

    return {
        field: state.get(field)
        for field in fields
    }





# ------------------



def message_read_mapper(message):
    if message.role == "assistant":
        metadata = build_metadata(message.agent_metadata)

        return {
            "role": "assistant",
            "mode": metadata.pop("mode"),   # خارج کردن mode
            "agent_metadata": metadata,
            "created_at": message.created_at,
        }

    return {
        "role": "user",
        "content": message.content,
        "created_at": message.created_at,
    }