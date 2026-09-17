# Master Document — LLM Providers, API Keys, and Models

**Last Update:** 2026-06-23
**Purpose:** Central reference for configuring any script, service, or tool requiring access to language models.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Active Providers (Valid API Keys)](#active-providers)
3. [Pending Providers (Invalid API Keys)](#pending-providers)
4. [Free Claude Code Proxy](#free-claude-code-proxy)
5. [Recommended Models by Use Case](#recommended-models)
6. [Quick Reference for Scripts](#quick-reference)

---

## Executive Summary

| Provider | API Key | Status | Free Models | Endpoint |
|-----------|---------|--------|----------------|----------|
| **NVIDIA NIM** | `nvapi-Y-0W1p...` | ✅ ACTIVE | 121 (all free in trial) | `https://integrate.api.nvidia.com/v1` |
| **OpenRouter** | `sk-or-v1-2a0f...` | ✅ ACTIVE | 26 `:free` models | `https://openrouter.ai/api/v1` |
| **Groq** | `gsk_R9K1PW...` | ✅ ACTIVE | 17 models (all free trial) | `https://api.groq.com/openai/v1` |
| **Cerebras** | `csk-4cyrrw...` | ✅ ACTIVE | 2 models (free trial) | `https://api.cerebras.ai/v1` |
| **Google Gemini** | `AIzaSyBBsb...` | ❌ INVALID | — | `https://generativelanguage.googleapis.com` |
| **DeepSeek** | *(no key)* | ⏳ PENDING | — | `https://api.deepseek.com/v1` |
| **Kimi (Moonshot)** | *(no key)* | ⏳ PENDING | — | `https://api.moonshot.cn/v1` |
| **Mistral** | *(no key)* | ⏳ PENDING | — | `https://api.mistral.ai/v1` |

---

## Active Providers

### 1. NVIDIA NIM (build.nvidia.com)

**API Key:** `nvapi-TU_API_KEY_AQUI`

| Field | Value |
|-------|-------|
| Endpoint | `https://integrate.api.nvidia.com/v1` |
| Compatibility | OpenAI-compatible |
| Free Tier | 1,000 inference credits (up to 5,000 upon request) |
| Rate Limit | **40 RPM** (not published, visible in build.nvidia.com UI) |
| Lifespan | Does not expire (trial, no expiration date) |
| Production | Requires NVIDIA AI Enterprise license ($4,500/GPU/year) |

**Featured Models (121 total):**

| Model | ID | Type | Context |
|--------|-----|------|----------|
| GLM-5.1 (Z.ai) | `z-ai/glm-5.1` | Chat/Code | — |
| Nemotron Ultra 550B | `nvidia/nemotron-3-ultra-550b-a55b` | Reasoning | 1M |
| Nemotron Super 120B | `nvidia/nemotron-3-super-120b-a12b` | Chat | 1M |
| DeepSeek V4 Flash | `deepseek-ai/deepseek-v4-flash` | Chat | — |
| DeepSeek V4 Pro | `deepseek-ai/deepseek-v4-pro` | Chat | — |
| Llama 3.3 70B | `meta/llama-3.3-70b-instruct` | Chat | — |
| Llama 4 Maverick 17B | `meta/llama-4-maverick-17b-128e-instruct` | Chat | — |
| Qwen 3.5 397B | `qwen/qwen3.5-397b-a17b` | Chat | — |
| GPT-OSS 120B | `openai/gpt-oss-120b` | Chat | — |
| GPT-OSS 20B | `openai/gpt-oss-20b` | Chat | — |
| Kimi K2.6 | `moonshotai/kimi-k2.6` | Chat | — |
| Mistral Large 3 675B | `mistralai/mistral-large-3-675b-instruct-2512` | Chat | — |

**Python Usage:**
```python
import openai

client = openai.OpenAI(
    api_key="nvapi-TU_API_KEY_AQUI",
    base_url="https://integrate.api.nvidia.com/v1"
)

response = client.chat.completions.create(
    model="z-ai/glm-5.1",
    messages=[{"role": "user", "content": "Hello"}],
    max_tokens=100
)
print(response.choices[0].message.content)
```

**curl Usage:**
```bash
curl -s https://integrate.api.nvidia.com/v1/chat/completions \
  -H "Authorization: Bearer nvapi-TU_API_KEY_AQUI" \
  -H "Content-Type: application/json" \
  -d '{"model":"z-ai/glm-5.1","messages":[{"role":"user","content":"Hello"}],"max_tokens":100}'
```

---

### 2. OpenRouter (openrouter.ai)

**API Key:** `sk-or-v1-TU_API_KEY_AQUI`

| Field | Value |
|-------|-------|
| Endpoint | `https://openrouter.ai/api/v1` |
| Compatibility | OpenAI-compatible |
| Free Tier | 50 req/day (no credits), 1,000 req/day (with $1+ credits), 20 RPM |
| Rate Limit | **20 RPM** for `:free` models |
| Platform Fee | 0% (free), 5.5% (pay-as-you-go) |

**Free Models Available (26):**

| Model | ID | Context | Notes |
|--------|-----|----------|-------|
| Qwen3 Coder | `qwen/qwen3-coder:free` | 1M | **Frequently saturated** |
| Nemotron Ultra 550B | `nvidia/nemotron-3-ultra-550b-a55b:free` | 1M | |
| Nemotron Super 120B | `nvidia/nemotron-3-super-120b-a12b:free` | 1M | |
| GPT-OSS 120B | `openai/gpt-oss-120b:free` | 131K | |
| GPT-OSS 20B | `openai/gpt-oss-20b:free` | 131K | |
| Llama 3.3 70B | `meta-llama/llama-3.3-70b-instruct:free` | 131K | |
| Hermes 3 405B | `nousresearch/hermes-3-llama-3.1-405b:free` | 131K | |
| Gemma 4 31B | `google/gemma-4-31b-it:free` | 262K | |
| Gemma 4 26B | `google/gemma-4-26b-a4b-it:free` | 262K | |
| Qwen3 Next 80B | `qwen/qwen3-next-80b-a3b-instruct:free` | 262K | |
| Poolside Laguna M.1 | `poolside/laguna-m.1:free` | 262K | |
| OpenRouter Free Router | `openrouter/free` | 200K | Auto-selects model |
| Nemotron Nano 30B | `nvidia/nemotron-3-nano-30b-a3b:free` | 256K | |
| North Mini Code | `cohere/north-mini-code:free` | 256K | |

**Python Usage:**
```python
import openai

client = openai.OpenAI(
    api_key="sk-or-v1-TU_API_KEY_AQUI",
    base_url="https://openrouter.ai/api/v1"
)

response = client.chat.completions.create(
    model="openai/gpt-oss-120b:free",
    messages=[{"role": "user", "content": "Hello"}],
    max_tokens=100
)
print(response.choices[0].message.content)
```

**curl Usage:**
```bash
curl -s https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer sk-or-v1-TU_API_KEY_AQUI" \
  -H "Content-Type: application/json" \
  -d '{"model":"openai/gpt-oss-120b:free","messages":[{"role":"user","content":"Hello"}],"max_tokens":100}'
```

---

### 3. Groq (groq.com)

**API Key:** `gsk_TU_API_KEY_AQUI`

| Field | Value |
|-------|-------|
| Endpoint | `https://api.groq.com/openai/v1` |
| Compatibility | OpenAI-compatible |
| Free Tier | 30 RPM / 6K TPM / 14,400 RPD (varies by model) |
| Speed | **Ultra-fast** (Dedicated LPU hardware) |

**Models and Rate Limits (Free Tier):**

| Model | ID | RPM | RPD | TPM | TPD |
|--------|-----|-----|-----|-----|-----|
| Llama 3.1 8B | `llama-3.1-8b-instant` | 30 | 14,400 | 6,000 | 500K |
| Llama 3.3 70B | `llama-3.3-70b-versatile` | 30 | 1,000 | 12,000 | 100K |
| Llama 4 Scout 17B | `meta-llama/llama-4-scout-17b-16e-instruct` | 30 | 1,000 | 30,000 | 500K |
| GPT-OSS 120B | `openai/gpt-oss-120b` | 30 | 1,000 | 8,000 | 200K |
| GPT-OSS 20B | `openai/gpt-oss-20b` | 30 | 1,000 | 8,000 | 200K |
| Qwen 3.6 27B | `qwen/qwen3.6-27b` | 30 | 1,000 | 8,000 | 200K |
| Qwen 3 32B | `qwen/qwen3-32b` | 60 | 1,000 | 6,000 | 500K |
| Allam 2 7B | `allam-2-7b` | 30 | 7,000 | 6,000 | 500K |
| Whisper V3 | `whisper-large-v3` | 20 | 2,000 | — | — |
| Whisper V3 Turbo | `whisper-large-v3-turbo` | 20 | 2,000 | — | — |

**Python Usage:**
```python
import openai

client = openai.OpenAI(
    api_key="gsk_TU_API_KEY_AQUI",
    base_url="https://api.groq.com/openai/v1"
)

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": "Hello"}],
    max_tokens=100
)
print(response.choices[0].message.content)
```

**curl Usage:**
```bash
curl -s https://api.groq.com/openai/v1/chat/completions \
  -H "Authorization: Bearer gsk_TU_API_KEY_AQUI" \
  -H "Content-Type: application/json" \
  -d '{"model":"llama-3.1-8b-instant","messages":[{"role":"user","content":"Hello"}],"max_tokens":100}'
```

---

### 4. Cerebras (cerebras.ai)

**API Key:** `csk-TU_API_KEY_AQUI`

| Field | Value |
|-------|-------|
| Endpoint | `https://api.cerebras.ai/v1` |
| Compatibility | OpenAI-compatible |
| Free Tier | 5 RPM / 30K TPM / 1M TPH / 1M TPD |
| Speed | **20x faster than GPU** (Dedicated wafer hardware) |

**Models Available:**

| Model | ID | RPM | TPM |
|--------|-----|-----|-----|
| GPT-OSS 120B | `gpt-oss-120b` | 5 | 30K |
| Z.ai GLM 4.7 | `zai-glm-4.7` | 5 | 30K |

**Python Usage:**
```python
import openai

client = openai.OpenAI(
    api_key="csk-TU_API_KEY_AQUI",
    base_url="https://api.cerebras.ai/v1"
)

response = client.chat.completions.create(
    model="zai-glm-4.7",
    messages=[{"role": "user", "content": "Hello"}],
    max_tokens=100
)
print(response.choices[0].message.content)
```

**curl Usage:**
```bash
curl -s https://api.cerebras.ai/v1/chat/completions \
  -H "Authorization: Bearer csk-TU_API_KEY_AQUI" \
  -H "Content-Type: application/json" \
  -d '{"model":"zai-glm-4.7","messages":[{"role":"user","content":"Hello"}],"max_tokens":100}'
```

---

## Pending Providers

### 5. Google Gemini

**API Key:** `AIzaSy_TU_API_KEY_AQUI` (project) / `AIzaSyAEmt_-Qj_9f5c0V8491BpvQ9pbwUg5jhA` (other)

| Field | Value |
|-------|-------|
| Status | ❌ **API KEY INVALID** |
| Endpoint | `https://generativelanguage.googleapis.com/v1beta` |
| Required Action | Regenerate key in [Google AI Studio](https://aistudio.google.com/apikey) |

**Models available (once key is fixed):**
- `gemini-2.5-flash` — Free, 1M context
- `gemini-2.5-pro` — Free with limits, 1M context
- `gemini-2.0-flash` — Free, 1M context

---

### 6. DeepSeek

| Field | Value |
|-------|-------|
| Status | ⏳ **NO API KEY** |
| Endpoint | `https://api.deepseek.com/v1` |
| Price | $0.14/$0.28 per 1M tokens (cheapest in the world) |
| Required Action | Get key at [platform.deepseek.com](https://platform.deepseek.com) |

---

### 7. Kimi (Moonshot AI)

| Field | Value |
|-------|-------|
| Status | ⏳ **NO API KEY** |
| Endpoint | `https://api.moonshot.cn/v1` |
| Price | $0.95/$4.00 per 1M tokens |
| Required Action | Get key at [platform.moonshot.cn](https://platform.moonshot.cn) |

---

### 8. Mistral

| Field | Value |
|-------|-------|
| Status | ⏳ **NO API KEY** |
| Endpoint | `https://api.mistral.ai/v1` |
| Free Models | Mistral 7B, Codestral 22B |
| Required Action | Get key at [console.mistral.ai](https://console.mistral.ai) |

---

## Free Claude Code Proxy

### Current Configuration

| Field | Value |
|-------|-------|
| Primary Model | `nvidia_nim/z-ai/glm-5.1` |
| Port | `8082` |
| Auth Token | `freecc` |
| Admin UI | `http://127.0.0.1:8082/admin` |
| Rate Limit | 18 req/60s (configurable in `.env`) |

### Configuration Files

| File | Purpose |
|---------|-----------|
| `core/free-claude-code/.env` | Proxy config (API keys, model, rate limits) |
| `~/.fcc/.env` | Managed env (synchronized copy) |
| `~/.claude/settings.json` | Claude Code config (model, hooks, plugins) |

### Commands

```bash
# Start proxy
fcc-server

# Start Claude Code with proxy
fcc-claude

# Verify proxy
Invoke-RestMethod -Uri "http://127.0.0.1:8082/v1/models" -Headers @{"x-api-key"="freecc"}
```

### Changing Model

1. Edit `core/free-claude-code/.env` $\rightarrow$ change `MODEL=`
2. Copy to `~/.fcc/.env`
3. Edit `~/.claude/settings.json` $\rightarrow$ change `"model":`
4. Restart `fcc-server`

---

## Recommended Models by Use Case

### Coding / Programming
| Model | Provider | Speed | Context | Free |
|--------|-----------|-----------|----------|--------|
| `z-ai/glm-5.1` | NVIDIA NIM | Fast | — | ✅ |
| `qwen/qwen3-coder:free` | OpenRouter | Medium | 1M | ✅ (saturated) |
| `openai/gpt-oss-120b:free` | OpenRouter | Fast | 131K | ✅ |
| `gpt-oss-120b` | Cerebras | Ultra-fast | — | ✅ |

### Chat / Conversation
| Model | Provider | Speed | Context | Free |
|--------|-----------|-----------|----------|--------|
| `llama-3.1-8b-instant` | Groq | Ultra-fast | — | ✅ |
| `nvidia/nemotron-3-ultra-550b-a55b:free` | OpenRouter | Medium | 1M | ✅ |
| `zai-glm-4.7` | Cerebras | Ultra-fast | — | ✅ |

### Reasoning / Complex Analysis
| Model | Provider | Speed | Context | Free |
|--------|-----------|-----------|----------|--------|
| `nvidia/nemotron-3-ultra-550b-a55b` | NVIDIA NIM | Slow | 1M | ✅ |
| `nvidia/nemotron-3-ultra-550b-a55b:free` | OpenRouter | Slow | 1M | ✅ |
| `qwen/qwen3.5-397b-a17b` | NVIDIA NIM | Slow | — | ✅ |

### Ultra-Fast (Minimum Latency)
| Model | Provider | Speed | Free RPM |
|--------|-----------|-----------|----------|
| `llama-3.1-8b-instant` | Groq | 560 tok/s | 30 |
| `zai-glm-4.7` | Cerebras | 20x GPU | 5 |
| `z-ai/glm-5.1` | NVIDIA NIM | Fast | 40 |

### Speech-to-Text
| Model | Provider | Request/Day |
|--------|-----------|-------------|
| `whisper-large-v3` | Groq | 2,000 |
| `whisper-large-v3-turbo` | Groq | 2,000 |

---

## Quick Reference for Scripts

### Environment Variables (Copy and Paste)

```bash
# NVIDIA NIM
export NVIDIA_NIM_API_KEY="nvapi-TU_API_KEY_AQUI"
export NVIDIA_NIM_BASE_URL="https://integrate.api.nvidia.com/v1"

# OpenRouter
export OPENROUTER_API_KEY="sk-or-v1-TU_API_KEY_AQUI"
export OPENROUTER_BASE_URL="https://openrouter.ai/api/v1"

# Groq
export GROQ_API_KEY="gsk_TU_API_KEY_AQUI"
export GROQ_BASE_URL="https://api.groq.com/openai/v1"

# Cerebras
export CEREBRAS_API_KEY="csk-TU_API_KEY_AQUI"
export CEREBRAS_BASE_URL="https://api.cerebras.ai/v1"

# Free Claude Code Proxy
export ANTHROPIC_AUTH_TOKEN="freecc"
export ANTHROPIC_BASE_URL="http://127.0.0.1:8082"
```

### Universal Python Snippet (with fallback)

```python
import openai
import os

PROVIDERS = [
    {
        "name": "NVIDIA NIM",
        "api_key": os.getenv("NVIDIA_NIM_API_KEY", "nvapi-TU_API_KEY_AQUI"),
        "base_url": "https://integrate.api.nvidia.com/v1",
        "model": "z-ai/glm-5.1",
    },
    {
        "name": "OpenRouter",
        "api_key": os.getenv("OPENROUTER_API_KEY", "sk-or-v1-TU_API_KEY_AQUI"),
        "base_url": "https://openrouter.ai/api/v1",
        "model": "openai/gpt-oss-120b:free",
    },
    {
        "name": "Groq",
        "api_key": os.getenv("GROQ_API_KEY", "gsk_TU_API_KEY_AQUI"),
        "base_url": "https://api.groq.com/openai/v1",
        "model": "llama-3.1-8b-instant",
    },
    {
        "name": "Cerebras",
        "api_key": os.getenv("CEREBRAS_API_KEY", "csk-TU_API_KEY_AQUI"),
        "base_url": "https://api.cerebras.ai/v1",
        "model": "zai-glm-4.7",
    },
]

def chat(prompt: str, provider_index: int = 0) -> str:
    """Sends a prompt to the LLM with automatic fallback between providers."""
    for i in range(provider_index, len(PROVIDERS)):
        p = PROVIDERS[i]
        try:
            client = openai.OpenAI(api_key=p["api_key"], base_url=p["base_url"])
            r = client.chat.completions.create(
                model=p["model"],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
            )
            return r.choices[0].message.content
        except Exception as e:
            print(f"[{p['name']}] Error: {e}, trying next...")
            continue
    raise Exception("All providers failed")

# Usage
print(chat("Explain what an AI agent is in 3 sentences"))
```

---

## Important Notes

1. **NVIDIA NIM** has the largest number of models (121) and all are free in trial. It is the most versatile.
2. **Groq** is the fastest (Dedicated LPU hardware) but has fewer models and lower RPD.
3. **OpenRouter** has more free models (26) but `qwen/qwen3-coder:free` is frequently saturated.
4. **Cerebras** is ultra-fast but only has 2 models and 5 RPM.
5. **All API keys are trial/free** — do not use in production without scaling.
6. **The Free Claude Code Proxy** uses NVIDIA NIM by default (GLM-5.1) — it is the most stable for daily use.
