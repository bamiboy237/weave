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
from typing import Generator

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
def stream_chat_completion(messages, max_tokens=2048, temperature=0.5, top_p=0.9) -> Generator[str, None, None]:
    """
    Stream a chat completion response token by token.
    
    Args:
        messages: List of message dicts with 'role' and 'content' keys
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature (0.0 to 1.0)
        top_p: Nucleus sampling parameter
        
    Yields:
        str: Individual tokens as they are generated

    Raises:
        ValueError: If messages are not properly formatted or temp/top_p are out of range
    """
    try:
        response_stream = llm.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stream=True
        )
        
        for chunk in response_stream:
            try:
                choices = getattr(chunk, "choices", None) or []
                if choices:
                    delta = getattr(choices[0], "delta", None)
                    if delta:
                        content = getattr(delta, "content", None)
                        if content:
                            yield content
            except (KeyError, IndexError, TypeError, AttributeError):
                continue  # Skip malformed chunks
    except Exception as e:
        raise ValueError(f"Error during chat completion: {e}")


if __name__ == "__main__":
    # call the streaming function and print each token as it arrives
    for token in stream_chat_completion([
        {
            "role": "system",
            "content": "You are Linus Torvalds, the creator of Linux. You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Explain asyncio in python"
        }
    ]):
        print(token, end="", flush=True)
    print()  # newline at the end