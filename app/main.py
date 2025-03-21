import asyncio
import builtins
import time
from app.utils.utils import new_uuid

from app.main_graph.graph_states import InputState
from app.main_graph.graph_builder import graph

from fastapi import FastAPI
import json
app = FastAPI(
    title="Deaths Data API",
    description="Get the data",
    summary="Retrieve ONS deaths data for England and Wales",
)

@app.post("/process_query")
async def process_query(query):
    inputState = InputState(messages=[query])
    output = ""

    async for c, metadata in graph.astream(input=inputState, stream_mode="messages", config={"configurable": {"thread_id": new_uuid()}}):
        if c.additional_kwargs.get("tool_calls"):
            print(c.additional_kwargs.get("tool_calls")[0]["function"].get("arguments"), end="", flush=True)
        if c.content:
            time.sleep(0.05)
            output += f"{c.content}"
            print(c.content, end="", flush=True)

    return output

async def main():
    input = builtins.input
    print("Query:")
    while True:
        query = input("> ")
        print("query", query)
        await process_query(query)

if __name__ == "__main__":
    asyncio.run(main())