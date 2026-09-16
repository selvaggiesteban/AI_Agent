# Documento Maestro — Proveedores LLM, API Keys y Modelos

**Última actualización:** 2026-06-23
**Propósito:** Referencia centralizada para configurar cualquier script, servicio o herramienta que requiera acceso a modelos de lenguaje.

---

## Tabla de Contenidos

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Proveedores Activos (API Keys válidas)](#proveedores-activos)
3. [Proveedores Pendientes (API Keys inválidas)](#proveedores-pendientes)
4. [Proxy Free Claude Code](#proxy-free-claude-code)
5. [Modelos Recomendados por Uso](#modelos-recomendados)
6. [Quick Reference para Scripts](#quick-reference)

---

## Resumen Ejecutivo

| Proveedor | API Key | Estado | Modelos Gratis | Endpoint |
|-----------|---------|--------|----------------|----------|
| **NVIDIA NIM** | `nvapi-Y-0W1p...` | ✅ ACTIVO | 121 (todos gratis en trial) | `https://integrate.api.nvidia.com/v1` |
| **OpenRouter** | `sk-or-v1-2a0f...` | ✅ ACTIVO | 26 modelos `:free` | `https://openrouter.ai/api/v1` |
| **Groq** | `gsk_R9K1PW...` | ✅ ACTIVO | 17 modelos (todos gratis trial) | `https://api.groq.com/openai/v1` |
| **Cerebras** | `csk-4cyrrw...` | ✅ ACTIVO | 2 modelos (gratis trial) | `https://api.cerebras.ai/v1` |
| **Google Gemini** | `AIzaSyBBsb...` | ❌ INVÁLIDA | — | `https://generativelanguage.googleapis.com` |
| **DeepSeek** | *(sin key)* | ⏳ PENDIENTE | — | `https://api.deepseek.com/v1` |
| **Kimi (Moonshot)** | *(sin key)* | ⏳ PENDIENTE | — | `https://api.moonshot.cn/v1` |
| **Mistral** | *(sin key)* | ⏳ PENDIENTE | — | `https://api.mistral.ai/v1` |

---

## Proveedores Activos

### 1. NVIDIA NIM (build.nvidia.com)

**API Key:** `nvapi-TU_API_KEY_AQUI`

| Campo | Valor |
|-------|-------|
| Endpoint | `https://integrate.api.nvidia.com/v1` |
| Compatibilidad | OpenAI-compatible |
| Free Tier | 1,000 inference credits (hasta 5,000 al solicitar) |
| Rate Limit | **40 RPM** (no publicado, visible en UI de build.nvidia.com) |
| Cadena | No expira (es trial, no tiene fecha de vencimiento) |
| Production | Requiere licencia NVIDIA AI Enterprise ($4,500/GPU/año) |

**Modelos Destacados (121 totales):**

| Modelo | ID | Tipo | Contexto |
|--------|-----|------|----------|
| GLM-5.1 (Z.ai) | `z-ai/glm-5.1` | Chat/Code | — |
| Nemotron Ultra 550B | `nvidia/nemotron-3-ultra-550b-a55b` | Razonamiento | 1M |
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

**Uso en Python:**
```python
import openai

client = openai.OpenAI(
    api_key="nvapi-TU_API_KEY_AQUI",
    base_url="https://integrate.api.nvidia.com/v1"
)

response = client.chat.completions.create(
    model="z-ai/glm-5.1",
    messages=[{"role": "user", "content": "Hola"}],
    max_tokens=100
)
print(response.choices[0].message.content)
```

**Uso en curl:**
```bash
curl -s https://integrate.api.nvidia.com/v1/chat/completions \
  -H "Authorization: Bearer nvapi-TU_API_KEY_AQUI" \
  -H "Content-Type: application/json" \
  -d '{"model":"z-ai/glm-5.1","messages":[{"role":"user","content":"Hola"}],"max_tokens":100}'
```

---

### 2. OpenRouter (openrouter.ai)

**API Key:** `sk-or-v1-TU_API_KEY_AQUI`

| Campo | Valor |
|-------|-------|
| Endpoint | `https://openrouter.ai/api/v1` |
| Compatibilidad | OpenAI-compatible |
| Free Tier | 50 req/día (sin credits), 1,000 req/día (con $1+ credits), 20 RPM |
| Rate Limit | **20 RPM** para modelos `:free` |
| Plataforma Fee | 0% (free), 5.5% (pay-as-you-go) |

**Modelos Gratis Disponibles (26):**

| Modelo | ID | Contexto | Notas |
|--------|-----|----------|-------|
| Qwen3 Coder | `qwen/qwen3-coder:free` | 1M | **Saturado frecuentemente** |
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
| OpenRouter Free Router | `openrouter/free` | 200K | Auto-selecciona modelo |
| Nemotron Nano 30B | `nvidia/nemotron-3-nano-30b-a3b:free` | 256K | |
| North Mini Code | `cohere/north-mini-code:free` | 256K | |

**Uso en Python:**
```python
import openai

client = openai.OpenAI(
    api_key="sk-or-v1-TU_API_KEY_AQUI",
    base_url="https://openrouter.ai/api/v1"
)

response = client.chat.completions.create(
    model="openai/gpt-oss-120b:free",
    messages=[{"role": "user", "content": "Hola"}],
    max_tokens=100
)
print(response.choices[0].message.content)
```

**Uso en curl:**
```bash
curl -s https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer sk-or-v1-TU_API_KEY_AQUI" \
  -H "Content-Type: application/json" \
  -d '{"model":"openai/gpt-oss-120b:free","messages":[{"role":"user","content":"Hola"}],"max_tokens":100}'
```

---

### 3. Groq (groq.com)

**API Key:** `gsk_TU_API_KEY_AQUI`

| Campo | Valor |
|-------|-------|
| Endpoint | `https://api.groq.com/openai/v1` |
| Compatibilidad | OpenAI-compatible |
| Free Tier | 30 RPM / 6K TPM / 14,400 RPD (varía por modelo) |
| Velocidad | **Ultra-rápido** (hardware专用 LPU) |

**Modelos y Rate Limits (Free Tier):**

| Modelo | ID | RPM | RPD | TPM | TPD |
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

**Uso en Python:**
```python
import openai

client = openai.OpenAI(
    api_key="gsk_TU_API_KEY_AQUI",
    base_url="https://api.groq.com/openai/v1"
)

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": "Hola"}],
    max_tokens=100
)
print(response.choices[0].message.content)
```

**Uso en curl:**
```bash
curl -s https://api.groq.com/openai/v1/chat/completions \
  -H "Authorization: Bearer gsk_TU_API_KEY_AQUI" \
  -H "Content-Type: application/json" \
  -d '{"model":"llama-3.1-8b-instant","messages":[{"role":"user","content":"Hola"}],"max_tokens":100}'
```

---

### 4. Cerebras (cerebras.ai)

**API Key:** `csk-TU_API_KEY_AQUI`

| Campo | Valor |
|-------|-------|
| Endpoint | `https://api.cerebras.ai/v1` |
| Compatibilidad | OpenAI-compatible |
| Free Tier | 5 RPM / 30K TPM / 1M TPH / 1M TPD |
| Velocidad | **20x más rápido que GPU** (hardware专用 wafer) |

**Modelos Disponibles:**

| Modelo | ID | RPM | TPM |
|--------|-----|-----|-----|
| GPT-OSS 120B | `gpt-oss-120b` | 5 | 30K |
| Z.ai GLM 4.7 | `zai-glm-4.7` | 5 | 30K |

**Uso en Python:**
```python
import openai

client = openai.OpenAI(
    api_key="csk-TU_API_KEY_AQUI",
    base_url="https://api.cerebras.ai/v1"
)

response = client.chat.completions.create(
    model="zai-glm-4.7",
    messages=[{"role": "user", "content": "Hola"}],
    max_tokens=100
)
print(response.choices[0].message.content)
```

**Uso en curl:**
```bash
curl -s https://api.cerebras.ai/v1/chat/completions \
  -H "Authorization: Bearer csk-TU_API_KEY_AQUI" \
  -H "Content-Type: application/json" \
  -d '{"model":"zai-glm-4.7","messages":[{"role":"user","content":"Hola"}],"max_tokens":100}'
```

---

## Proveedores Pendientes

### 5. Google Gemini

**API Key:** `AIzaSy_TU_API_KEY_AQUI` (proyecto) / `AIzaSyAEmt_-Qj_9f5c0V8491BpvQ9pbwUg5jhA` (otro)

| Campo | Valor |
|-------|-------|
| Estado | ❌ **API KEY INVÁLIDA** |
| Endpoint | `https://generativelanguage.googleapis.com/v1beta` |
| Acción requerir | Regenerar key en [Google AI Studio](https://aistudio.google.com/apikey) |

**Modelos disponibles (cuando se arregle la key):**
- `gemini-2.5-flash` — Gratis, 1M contexto
- `gemini-2.5-pro` — Gratis con límites, 1M contexto
- `gemini-2.0-flash` — Gratis, 1M contexto

---

### 6. DeepSeek

| Campo | Valor |
|-------|-------|
| Estado | ⏳ **SIN API KEY** |
| Endpoint | `https://api.deepseek.com/v1` |
| Precio | $0.14/$0.28 por 1M tokens (el más barato del mundo) |
| Acción requerir | Obtener key en [platform.deepseek.com](https://platform.deepseek.com) |

---

### 7. Kimi (Moonshot AI)

| Campo | Valor |
|-------|-------|
| Estado | ⏳ **SIN API KEY** |
| Endpoint | `https://api.moonshot.cn/v1` |
| Precio | $0.95/$4.00 por 1M tokens |
| Acción requerir | Obtener key en [platform.moonshot.cn](https://platform.moonshot.cn) |

---

### 8. Mistral

| Campo | Valor |
|-------|-------|
| Estado | ⏳ **SIN API KEY** |
| Endpoint | `https://api.mistral.ai/v1` |
| Modelos gratis | Mistral 7B, Codestral 22B |
| Acción requerir | Obtener key en [console.mistral.ai](https://console.mistral.ai) |

---

## Proxy Free Claude Code

### Configuración Actual

| Campo | Valor |
|-------|-------|
| Modelo principal | `nvidia_nim/z-ai/glm-5.1` |
| Puerto | `8082` |
| Auth Token | `freecc` |
| Admin UI | `http://127.0.0.1:8082/admin` |
| Rate Limit | 18 req/60s (configurable en `.env`) |

### Archivos de Configuración

| Archivo | Propósito |
|---------|-----------|
| `core/free-claude-code/.env` | Config del proxy (API keys, modelo, rate limits) |
| `~/.fcc/.env` | Managed env (copia sincronizada) |
| `~/.claude/settings.json` | Config de Claude Code (modelo, hooks, plugins) |

### Comandos

```bash
# Iniciar proxy
fcc-server

# Iniciar Claude Code con proxy
fcc-claude

# Verificar proxy
Invoke-RestMethod -Uri "http://127.0.0.1:8082/v1/models" -Headers @{"x-api-key"="freecc"}
```

### Cambiar Modelo

1. Editar `core/free-claude-code/.env` → cambiar `MODEL=`
2. Copiar a `~/.fcc/.env`
3. Editar `~/.claude/settings.json` → cambiar `"model":`
4. Reiniciar `fcc-server`

---

## Modelos Recomendados por Uso

### Coding / Programación
| Modelo | Proveedor | Velocidad | Contexto | Gratis |
|--------|-----------|-----------|----------|--------|
| `z-ai/glm-5.1` | NVIDIA NIM | Rápido | — | ✅ |
| `qwen/qwen3-coder:free` | OpenRouter | Medio | 1M | ✅ (saturado) |
| `openai/gpt-oss-120b:free` | OpenRouter | Rápido | 131K | ✅ |
| `gpt-oss-120b` | Cerebras | Ultra-rápido | — | ✅ |

### Chat / Conversación
| Modelo | Proveedor | Velocidad | Contexto | Gratis |
|--------|-----------|-----------|----------|--------|
| `llama-3.1-8b-instant` | Groq | Ultra-rápido | — | ✅ |
| `nvidia/nemotron-3-ultra-550b-a55b:free` | OpenRouter | Medio | 1M | ✅ |
| `zai-glm-4.7` | Cerebras | Ultra-rápido | — | ✅ |

### Razonamiento / Análisis Complejo
| Modelo | Proveedor | Velocidad | Contexto | Gratis |
|--------|-----------|-----------|----------|--------|
| `nvidia/nemotron-3-ultra-550b-a55b` | NVIDIA NIM | Lento | 1M | ✅ |
| `nvidia/nemotron-3-ultra-550b-a55b:free` | OpenRouter | Lento | 1M | ✅ |
| `qwen/qwen3.5-397b-a17b` | NVIDIA NIM | Lento | — | ✅ |

### Ultra-Rápido (latencia mínima)
| Modelo | Proveedor | Velocidad | RPM Free |
|--------|-----------|-----------|----------|
| `llama-3.1-8b-instant` | Groq | 560 tok/s | 30 |
| `zai-glm-4.7` | Cerebras | 20x GPU | 5 |
| `z-ai/glm-5.1` | NVIDIA NIM | Rápido | 40 |

### Speech-to-Text
| Modelo | Proveedor | Request/Day |
|--------|-----------|-------------|
| `whisper-large-v3` | Groq | 2,000 |
| `whisper-large-v3-turbo` | Groq | 2,000 |

---

## Quick Reference para Scripts

### Variables de Entorno (copiar y pegar)

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

### Snippet Python Universal (con fallback)

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
    """Envía un prompt al LLM con fallback automático entre proveedores."""
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
            print(f"[{p['name']}] Error: {e}, intentando siguiente...")
            continue
    raise Exception("Todos los proveedores fallaron")

# Uso
print(chat("Explica qué es un agente de IA en 3 oraciones"))
```

---

## Notas Importantes

1. **NVIDIA NIM** tiene la mayor cantidad de modelos (121) y todos son gratis en trial. Es el más versátil.
2. **Groq** es el más rápido (hardware专用 LPU) pero tiene menos modelos y RPD más bajo.
3. **OpenRouter** tiene más modelos gratis (26) pero `qwen/qwen3-coder:free` está frecuentemente saturado.
4. **Cerebras** es ultrarrápido pero solo tiene 2 modelos y 5 RPM.
5. **Todas las API keys son de trial/free** — no usar en producción sin escalar.
6. **El proxy Free Claude Code** usa NVIDIA NIM por defecto (GLM-5.1) — es el más estable para uso diario.
