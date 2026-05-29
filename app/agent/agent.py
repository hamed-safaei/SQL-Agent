import json
import time
import re
from typing import Generator

from app.agent.graph import graph
from app.agent.chains import (
    intent_chain,
    chat_prompt,
    sql_chain,
    full_chain,
    analyzer_chain,
    streaming_llm,
)
from app.agent.nodes import get_db_schema_text, run_sql_query


# def run_ai_agent(question: str):
#     print(f"🔍 Analyzing question: {question}")

#     try:
#         final_state = graph.invoke({"question": question})

#         mode = final_state.get("mode")

#         response = {
#             "mode": mode,
#             "question": question
#         }

#         if mode == "chat":
#             response["message"] = final_state.get("message")

#         elif mode == "sql":
#             response["sql"] = final_state.get("sql")

#         elif mode == "result":
#             response["sql"] = final_state.get("sql")
#             response["data"] = final_state.get("result")
#             response["columns"] = list(final_state["result"][0].keys()) if final_state.get("result") else []

#         elif mode == "full":
#             response["intro_message"] = final_state.get("intro_message")
#             response["sql"] = final_state.get("sql")
#             response["sql_message"] = final_state.get("sql_message")
#             response["data"] = final_state.get("result")
#             response["columns"] = list(final_state["result"][0].keys()) if final_state.get("result") else []
#             response["analysis"] = final_state.get("analysis")

#         if final_state.get("error"):
#             response["error"] = final_state["error"]

#         return response

#     except Exception as e:
#         return {
#             "mode": "error",
#             "error": str(e)
#         }


#Streaming Function 

def run_ai_agent_stream(question: str) -> Generator[str, None, None]:
    """
    پیام‌های متنی رو token به token با SSE می‌فرسته.
    SQL و جدول به صورت یکجا ارسال می‌شن.

    فرمت هر event:
        data: {"event": "...", ...}\n\n

    event ها:
        mode        → {"mode": "chat"|"sql"|"result"|"full"}
        token       → {"text": "..."}         پیام متنی token به token
        new_bubble  → {}                       شروع حباب متنی جدید
        sql         → {"sql": "..."}           کوئری SQL (یکجا)
        table       → {"columns": [], "data": []}  جدول نتیجه (یکجا)
        error       → {"error": "..."}
        done        → {}                       پایان stream
    """

    def sse(event: str, data: dict) -> str:
        payload = {"event": event, **data}
        return f"data: {json.dumps(payload, ensure_ascii=False, default=str)}\n\n"

    def stream_text(text: str):
        """استریم کردن متن با حفظ فاصله‌ها و خطوط جدید"""
        if not text:
            return
        tokens = re.findall(r'\S+|\s+', text)
        for token in tokens:
            yield sse("token", {"text": token})
            time.sleep(0.03)

    try:
        intent_result = intent_chain.invoke({"question": question})
        mode = intent_result.mode
        yield sse("mode", {"mode": mode})

        schema_text = None
        if mode in ("sql", "result", "full"):
            schema_text = get_db_schema_text()


        if mode == "chat":
            msgs = chat_prompt.format_messages(question=question)
            for chunk in streaming_llm.stream(msgs):
                if chunk.content:
                    yield sse("token", {"text": chunk.content})

        elif mode == "sql":
            sql_result = sql_chain.invoke({"question": question, "schema": schema_text})
            yield sse("sql", {"sql": sql_result.sql})

        elif mode == "result":
            sql_result = sql_chain.invoke({"question": question, "schema": schema_text})
            try:
                rows = run_sql_query(sql_result.sql)
                cols = list(rows[0].keys()) if rows else []
                yield sse("table", {"columns": cols, "data": rows})
            except Exception as e:
                yield sse("error", {"error": str(e)})

        elif mode == "full":
            full_result = full_chain.invoke({"question": question, "schema": schema_text})

            yield from stream_text(full_result.intro_message)

            yield sse("sql", {"sql": full_result.sql})

            yield sse("new_bubble", {})
            yield from stream_text(full_result.sql_message)

            try:
                rows = run_sql_query(full_result.sql)
                cols = list(rows[0].keys()) if rows else []
                yield sse("table", {"columns": cols, "data": rows})

                analysis_result = analyzer_chain.invoke({
                    "question": question,
                    "sql": full_result.sql,
                    "result": rows
                })

                yield sse("new_bubble", {})
                yield from stream_text(analysis_result.analysis)

            except Exception as e:
                yield sse("error", {"error": str(e)})

        yield sse("done", {})

    except Exception as e:
        yield sse("error", {"error": str(e)})
        yield sse("done", {})