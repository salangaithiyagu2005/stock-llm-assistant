import subprocess

def ask_llm(prompt: str) -> str:
    try:
        proc = subprocess.Popen(
            ['ollama', 'run', 'llama3.2'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        output, _ = proc.communicate(prompt)
        return output.strip()
    except Exception as e:
        return f"LLM error: {e}"
