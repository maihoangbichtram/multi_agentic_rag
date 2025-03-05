import asyncio
import builtins
import time
from utils.utils import new_uuid

from main_graph.graph_states import InputState
from main_graph.graph_builder import graph

async def process_query(query):
    inputState = InputState(messages=[query])

    async for c, metadata in graph.astream(input=inputState, stream_mode="messages", config={"configurable": {"thread_id": new_uuid()}}):
        if c.additional_kwargs.get("tool_calls"):
            print(c.additional_kwargs.get("tool_calls")[0]["function"].get("arguments"), end="", flush=True)
        if c.content:
            time.sleep(0.05)
            print(c.content, end="", flush=True)

async def main():
    input = builtins.input
    print("Query:")
    while True:
        query = input("> ")
        print("query", query)
        await process_query(query)

if __name__ == "__main__":
    asyncio.run(main())