import re
import httpx
from config import DEEPSEEK_API_KEY

PROGRAMMING_LANGUAGES = ["python", "javascript", "typescript", "java", "c++", "go", "rust", "swift", "kotlin", "php", "ruby"]
TECH_KEYWORDS = ["code", "function", "api", "database", "sql", "debug", "error", "fix", "deploy", "docker", "kubernetes", "react", "vue", "node", "flask", "django"]
DEBUG_PATTERNS = [r"error\s+at\s+line", r"traceback", r"exception", r"syntax\s*error", r"type\s*error", r"import\s*error", r"stack\s*trace"]

def determine_model(prompt: str) -> str:
    """Route to deepseek-chat or deepseek-coder"""
    prompt_lower = prompt.lower()
    score = 0
    
    for lang in PROGRAMMING_LANGUAGES:
        if re.search(rf'\b{re.escape(lang)}\b', prompt_lower):
            score += 3
    for kw in TECH_KEYWORDS:
        if kw in prompt_lower:
            score += 2
    for pattern in DEBUG_PATTERNS:
        if re.search(pattern, prompt, re.IGNORECASE):
            score += 5
    if re.search(r'```|import |def |class |function |const |let |var ', prompt):
        score += 3
    
    return "deepseek-coder" if score >= 5 else "deepseek-chat"

async def generate_ai_response(prompt: str, model: str, history: list = None):
    """Stream AI response from DeepSeek"""
    if not DEEPSEEK_API_KEY:
        yield f"[DEV MODE] Using {model}. Set DEEPSEEK_API_KEY for real AI.\n\nYou asked: {prompt}"
        return

    messages = []
    if model == "deepseek-coder":
        messages.append({"role": "system", "content": "You are an expert programmer. Provide detailed code solutions with best practices."})
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": prompt})

    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    data = {"model": model, "messages": messages, "stream": True, "temperature": 0.7, "max_tokens": 4096}

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", "https://api.deepseek.com/v1/chat/completions", headers=headers, json=data) as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        if line.strip() == "data: [DONE]":
                            break
                        import json
                        try:
                            chunk = json.loads(line[6:])
                            content = chunk["choices"][0]["delta"].get("content", "")
                            if content:
                                yield content
                        except:
                            continue
    except Exception as e:
        yield f"Error: {str(e)}"