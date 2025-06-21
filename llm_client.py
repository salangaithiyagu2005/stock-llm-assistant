import asyncio
import httpx

OLLAMA_API = "http://localhost:11434/api/generate"

async def ask_llm(prompt: str) -> str:
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "llama3.2",   # ⚠️ Make sure this matches `ollama list`
        "prompt": prompt,
        "stream": False
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(OLLAMA_API, json=payload, headers=headers, timeout=60)

            # 🔍 Print status + raw text
            print("🔁 Status Code:", response.status_code)
            print("📡 Raw Response Text:", repr(response.text[:300]))

            if not response.text.strip():
                return "❌ Ollama returned an empty response."

            try:
                data = response.json()
                return data.get("response", "").strip()
            except Exception as json_err:
                return f"❌ JSON parse error: {json_err}\n↪ Raw: {response.text[:300]}"

    except httpx.RequestError as e:
        return f"❌ HTTP Request error: {e}"
    except httpx.HTTPStatusError as e:
        return f"❌ HTTP Status error: {e}"
    except Exception as e:
        return f"❌ General error: {e}"

def ask_llm_sync(prompt: str) -> str:
    return asyncio.run(ask_llm(prompt))
