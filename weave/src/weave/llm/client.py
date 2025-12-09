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
from llama_cpp.llama_types import ChatCompletionRequestMessage


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
    Stream a chat completion response token by token.
    
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
        str: Individual tokens as they are generated

    Raises:
        ValueError: If messages are not properly formatted or temp/top_p are out of range
    """
    logger.info("stream_chat_completion called")
    logger.debug(f"Messages: {messages}")
    logger.debug(f"max_tokens={max_tokens}, temp={temperature}, top_p={top_p}")
    
    try:
        logger.info("Creating chat completion stream...")
        response_stream = llm.create_chat_completion(
            messages=_convert_messages(messages),
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stream=True,
            tools=
        )
        logger.info("Chat completion stream created")
        
        chunk_count = 0
        for chunk in response_stream:
            chunk_count += 1
            logger.debug(f"Received chunk #{chunk_count}: {chunk}")
            
            try:
                # Handle both dict and object types
                if isinstance(chunk, dict):
                    choices = chunk.get("choices", [])
                else:
                    choices = getattr(chunk, "choices", [])
                
                logger.debug(f"Chunk has {len(choices)} choices")
                
                if choices:
                    # Handle both dict and object types for delta
                    if isinstance(choices[0], dict):
                        delta = choices[0].get("delta", {})
                        content = delta.get("content", None) if isinstance(delta, dict) else getattr(delta, "content", None)
                    else:
                        delta = getattr(choices[0], "delta", None)
                        content = getattr(delta, "content", None) if delta else None
                    
                    logger.debug(f"Delta: {delta}")
                    
                    if content:
                        logger.debug(f"Yielding content: {repr(content)}")
                        yield content
            except (KeyError, IndexError, TypeError, AttributeError) as e:
                logger.warning(f"Error processing chunk: {e}")
                continue
        
        logger.info(f"Stream complete. Yielded {chunk_count} chunks")
    except Exception as e:
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