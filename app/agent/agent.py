from typing import Generator
from .graph import graph
from .schemas.states.agent_state import AgentState


def run(question: str, streaming: bool = True):

    inputs = {"question": question}

    if streaming:
        def _event_generator() -> Generator:
            for event in graph.stream(inputs, stream_mode=["updates", "custom"]):
                yield event
        return _event_generator()

    else:
        final_state: AgentState = graph.invoke(inputs)
        return final_state
    





    """
    Run the SQL agent graph.

    Parameters
    ----------
    question  : the user's question
    streaming : True  → returns a generator of (event_mode, event_data) tuples
                False → returns the final AgentState dict

    Returns
    -------
    streaming=True  → Generator[tuple[str, dict], None, None]
    streaming=False → AgentState
    """