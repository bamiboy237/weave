"""
llama-cpp-python wrapper.

Handles model loading with appropriate settings:
- Quantization level configuration
- GPU layer offloading (n_gpu_layers)
- Context window size (n_ctx)
- Memory management

Provides a clean interface for the rest of the application.
"""

from llama_cpp import Llama
import sys
import os
from typing import Generator, Sequence
from weave.core.logging import logger
from weave.tui.models import MessageContent
from llama_cpp.llama_types import ChatCompletionRequestMessage, ChatCompletionTool
from weave.tools import registry as tool_registry




# supppress stderr from llama.cpp
sys.stderr = open(os.devnull, 'w')

llm = Llama(
    model_path="/home/bamiboy/projects/weave/models/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf",
    n_ctx=8192,
    n_threads=4,
    n_gpu_layers=0,
    verbose=False,
    chat_format="qwen"
)
logger.info("LLM model loaded successfully")
logger.debug(f"Model path: {llm.model_path}")

def _convert_messages(messages: Sequence[MessageContent]) -> list[ChatCompletionRequestMessage]:
    """Convert MessageContent sequence to llama-cpp-python's expected format."""
    return[
        ChatCompletionRequestMessage(role=m["role"], content=m["content"]) for m in messages # type: ignore
    ]


def stream_chat_completion(messages: Sequence[MessageContent], max_tokens=2048, temperature=0.3, top_p=0.9) -> Generator[str, None, None]:
    """
    Get a chat completion response from the LLM.
    
    Note: When tools are enabled, returns non-streaming responses to properly handle tool calls.
    
    Args:
        messages: List of messages of type MessageContent with 'role' and 'content' keys:
        [{"role": "system", "content": "..."}, 
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."},
        {"role": "user", "content": "..."}]
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature (0.0 to 1.0)
        top_p: Nucleus sampling parameter
        
    Yields:
        str: Content tokens or tool call information

    Raises:
        ValueError: If messages are not properly formatted or temp/top_p are out of range
    """
    logger.info("stream_chat_completion called")
    logger.debug(f"Messages: {messages}")
    logger.debug(f"max_tokens={max_tokens}, temp={temperature}, top_p={top_p}")
    
    try:
        logger.info("Creating chat completion...")
        tools_dicts = tool_registry.get_tools()
        tools: list[ChatCompletionTool] = [
            ChatCompletionTool(
                type=tool_dict["type"],
                function=tool_dict["function"]
            )
            for tool_dict in tools_dicts
        ]
    

        response = llm.create_chat_completion(
            messages=_convert_messages(messages),
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stream=False,
            tools=tools,
            tool_choice="auto"
        )
        logger.info("Chat completion received")
        logger.debug(f"Full response: {response}")
        
        # Extract the message from the response
        if isinstance(response, dict):
            choices = response.get("choices", []) # type: ignore
        else:
            choices = getattr(response, "choices", [])
        
        if not choices:
            logger.warning("No choices in response")
            return
        
        choice = choices[0]
        message = choice.get("message") if isinstance(choice, dict) else getattr(choice, "message", None)
        
        if not message:
            logger.warning("No message in choice")
            return
        
        # Check for tool calls
        tool_calls = message.get("tool_calls") if isinstance(message, dict) else getattr(message, "tool_calls", None)
        
        if tool_calls:
            logger.info(f"Tool calls detected: {tool_calls}")
            # Yield tool call information as a special format
            import json
            yield json.dumps({"tool_calls": tool_calls})
        else:
            # Regular text response
            content = message.get("content") if isinstance(message, dict) else getattr(message, "content", None)
            if content:
                logger.info(f"Yielding content: {repr(content)}")
                yield content
            else:
                logger.warning("No content or tool calls in message")
                
    except Exception as e:
        logger.error(f"Error during chat completion: {e}", exc_info=True)
        raise ValueError(f"Error during chat completion: {e}")


if __name__ == "__main__":
    # call the streaming function and print each token as it arrives
    messages: Sequence[MessageContent] = [
        {
            "role": "system",
            "content": "You are Linus Torvalds, the creator of Linux. You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Explain asyncio in python"
        }
    ]  # type: ignore
    for token in stream_chat_completion(messages):
        print(token, end="", flush=True)
    print()  # newline at the end