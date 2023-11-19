
from openai import AsyncClient
from openai.types.beta import Assistant, Thread
import time
import asyncio
async def get_completion(async_client: AsyncClient, message:str, agent: Assistant, funcs, thread:Thread):
    """
    Executes a thread based on a provided message and retrieves the completion result.

    This function submits a message to a specified thread, triggering the execution of an array of functions
    defined within a first_matching_func parameter. Each function in the array must implement a `run()` method that returns the outputs.

    Parameters:
    - message (str): The input message to be processed.
    - agent (OpenAI Assistant): The agent instance that will process the message.
    - funcs (list): A list of function objects, defined with the instructor library.
    - thread (Thread): The OpenAI Assistants API thread responsible for managing the execution flow.

    Returns:
    - str: The completion output as a string, obtained from the agent following the execution of input message and functions.
    """

    # create new message in the thread
    conversation = await start_conversation(agent, async_client, message, thread)

    while True:
      # wait until run completes
      status = await get_response(async_client, conversation, thread)

      # function execution
      if status == "requires_action":
        conversation = await perform_action(async_client, conversation, funcs, thread)
      # error
      elif status == "failed":
        raise Exception("Run Failed. Error: ", conversation.last_error)
      # return assistant message
      else:
        message = await get_latest_message_text(async_client, message, thread)
        return message


async def get_latest_message_text(async_client, message, thread):
    messages = await async_client.beta.threads.messages.list(
        thread_id=thread.id
    )
    message = messages.data[0].content[0].text.value
    return message


async def perform_action(async_client, conversation, funcs, thread):
    tool_calls = conversation.required_action.submit_tool_outputs.tool_calls
    tool_outputs_coroutines = [get_tool_output(funcs, tool_call) for tool_call in tool_calls]
    tool_call_ids = [tool_call.id for tool_call in tool_calls]
    tool_output_results = asyncio.gather(*tool_outputs_coroutines, return_exceptions=True)
    tool_outputs = [{"tool_call_id": id, "output": output}
                    for id, output in
                    zip(tool_call_ids, tool_output_results)]
    # submit tool outputs
    conversation = await async_client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread.id,
        run_id=conversation.id,
        tool_outputs=tool_outputs
    )
    return conversation


async def get_tool_output(funcs, tool_call):
    matching_funcs = (func for func in funcs if
                      func.__name__ == tool_call.function.name)  # find the tool to be executed
    # init tool
    matching_func_calls = (matching_func(**eval(tool_call.function.arguments)) for matching_func in matching_funcs)
    matching_outputs = (matching_func_call.run() for matching_func_call in matching_func_calls)
    # get outputs from the tool
    output = next(matching_outputs)
    return output


async def get_response(async_client, run, thread):
    while run.status in ['queued', 'in_progress']:
        run = await async_client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        await asyncio.sleep(1)
    return run.status


async def start_conversation(agent, async_client, message, thread):
    # create new message in the thread

    message = await async_client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=message
    )
    # run this thread
    run = await async_client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=agent.id,
    )
    return run
