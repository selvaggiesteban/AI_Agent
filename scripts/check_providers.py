"""Check provider availability and model status for Free Claude Code."""

import os
import sys
import time
from pathlib import Path
from dataclasses import dataclass

# Load .env from project root
env_path = Path(__file__).resolve().parent.parent / "core" / "free-claude-code" / ".env"
if env_path.exists():
    from dotenv import dotenv_values
    for k, v in dotenv_values(env_path).items():
        if v and k not in os.environ:
            os.environ[k] = v

import httpx


@dataclass
class ProviderCheck:
    name: str
    key_env: str
    base_url: str
    endpoint: str
    auth_header: str
    auth_prefix: str
    model: str
    transport: str  # "openai" or "anthropic"
    key: str = ""
    status: str = ""
    latency_ms: int = 0
    models_found: int = 0
    error: str = ""


def build_providers() -> list[ProviderCheck]:
    return [
        ProviderCheck(
            name="Bynara",
            key_env="BYNARA_API_KEY",
            base_url="https://router.bynara.id/v1",
            endpoint="/chat/completions",
            auth_header="Authorization",
            auth_prefix="Bearer ",
            model="mimo-v2.5-free",
            transport="openai",
        ),
        ProviderCheck(
            name="Z.AI",
            key_env="ZAI_API_KEY",
            base_url="https://api.z.ai/api/anthropic",
            endpoint="/v1/messages",
            auth_header="x-api-key",
            auth_prefix="",
            model="glm-5.1",
            transport="anthropic",
        ),
        ProviderCheck(
            name="NVIDIA NIM",
            key_env="NVIDIA_NIM_API_KEY",
            base_url="https://integrate.api.nvidia.com/v1",
            endpoint="/chat/completions",
            auth_header="Authorization",
            auth_prefix="Bearer ",
            model="nvidia/nemotron-3-super-120b-a12b",
            transport="openai",
        ),
        ProviderCheck(
            name="OpenRouter",
            key_env="OPENROUTER_API_KEY",
            base_url="https://openrouter.ai/api/v1",
            endpoint="/chat/completions",
            auth_header="Authorization",
            auth_prefix="Bearer ",
            model="openai/gpt-oss-120b",
            transport="openai",
        ),
        ProviderCheck(
            name="Groq",
            key_env="GROQ_API_KEY",
            base_url="https://api.groq.com/openai/v1",
            endpoint="/chat/completions",
            auth_header="Authorization",
            auth_prefix="Bearer ",
            model="llama-3.1-8b-instant",
            transport="openai",
        ),
        ProviderCheck(
            name="Cerebras",
            key_env="CEREBRAS_API_KEY",
            base_url="https://api.cerebras.ai/v1",
            endpoint="/chat/completions",
            auth_header="Authorization",
            auth_prefix="Bearer ",
            model="gpt-oss-120b",
            transport="openai",
        ),
        ProviderCheck(
            name="Gemini",
            key_env="GEMINI_API_KEY",
            base_url="https://generativelanguage.googleapis.com/v1beta/openai",
            endpoint="/chat/completions",
            auth_header="Authorization",
            auth_prefix="Bearer ",
            model="gemini-2.0-flash-lite",
            transport="openai",
        ),
        ProviderCheck(
            name="DeepSeek",
            key_env="DEEPSEEK_API_KEY",
            base_url="https://api.deepseek.com/anthropic",
            endpoint="/v1/messages",
            auth_header="x-api-key",
            auth_prefix="",
            model="deepseek-chat",
            transport="anthropic",
        ),
        ProviderCheck(
            name="Kimi",
            key_env="KIMI_API_KEY",
            base_url="https://api.moonshot.ai/anthropic",
            endpoint="/v1/messages",
            auth_header="x-api-key",
            auth_prefix="",
            model="moonshot-v1-8k",
            transport="anthropic",
        ),
        ProviderCheck(
            name="Mistral",
            key_env="MISTRAL_API_KEY",
            base_url="https://api.mistral.ai/v1",
            endpoint="/chat/completions",
            auth_header="Authorization",
            auth_prefix="Bearer ",
            model="mistral-small-latest",
            transport="openai",
        ),
    ]


def check_chat(p: ProviderCheck, client: httpx.Client) -> None:
    p.key = os.environ.get(p.key_env, "")
    if not p.key:
        p.status = "SIN KEY"
        return

    url = p.base_url + p.endpoint
    headers = {p.auth_header: f"{p.auth_prefix}{p.key}", "Content-Type": "application/json"}

    if p.transport == "openai":
        body = {"model": p.model, "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 5}
    else:
        body = {"model": p.model, "max_tokens": 5, "messages": [{"role": "user", "content": "Hi"}]}

    t0 = time.time()
    try:
        r = client.post(url, json=body, headers=headers, timeout=20)
        p.latency_ms = int((time.time() - t0) * 1000)
        if r.status_code == 200:
            p.status = "OK"
        elif r.status_code == 429:
            data = r.json()
            msg = data.get("error", {}).get("message", "")[:60]
            p.status = "RATE LIMITED"
            p.error = msg
        elif r.status_code == 401:
            p.status = "KEY INVALID"
            p.error = r.text[:80]
        elif r.status_code == 402:
            p.status = "SIN SALDO"
            p.error = r.text[:80]
        else:
            p.status = f"ERROR {r.status_code}"
            p.error = r.text[:80]
    except Exception as e:
        p.latency_ms = int((time.time() - t0) * 1000)
        p.status = "TIMEOUT/ERROR"
        p.error = str(e)[:80]


def check_models(p: ProviderCheck, client: httpx.Client) -> None:
    if p.key and p.status not in ("SIN KEY", "KEY INVALID"):
        url = p.base_url + "/models"
        headers = {p.auth_header: f"{p.auth_prefix}{p.key}"}
        try:
            r = client.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                data = r.json()
                models = data.get("data", [])
                p.models_found = len(models)
        except Exception:
            pass


def main():
    print("=" * 80)
    print("FREE CLAUDE CODE — Provider Status Check")
    print("=" * 80)
    print()

    providers = build_providers()
    client = httpx.Client()

    for p in providers:
        print(f"Checking {p.name}...", end=" ", flush=True)
        check_chat(p, client)
        check_models(p, client)

        if p.status == "OK":
            icon = "+"
        elif p.status in ("SIN KEY",):
            icon = "-"
        else:
            icon = "!"

        print(f"[{icon}] {p.status} ({p.latency_ms}ms)")
        if p.models_found:
            print(f"        Models available: {p.models_found}")
        if p.error:
            print(f"        Error: {p.error}")

    client.close()

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    ok = [p for p in providers if p.status == "OK"]
    rate = [p for p in providers if p.status == "RATE LIMITED"]
    nokey = [p for p in providers if p.status == "SIN KEY"]
    err = [p for p in providers if p.status not in ("OK", "RATE LIMITED", "SIN KEY")]

    print(f"  OK:              {len(ok)}")
    for p in ok:
        print(f"    - {p.name}: {p.model} ({p.latency_ms}ms)")

    print(f"  RATE LIMITED:    {len(rate)}")
    for p in rate:
        print(f"    - {p.name}: {p.error}")

    print(f"  SIN KEY:         {len(nokey)}")
    for p in nokey:
        print(f"    - {p.name}")

    print(f"  ERROR:           {len(err)}")
    for p in err:
        print(f"    - {p.name}: {p.status} — {p.error}")

    # Save results to file
    out_path = Path(__file__).resolve().parent.parent / "PROVIDER_STATUS.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"Provider Status — {time.strftime('%Y-%m-%d %H:%M')}\n")
        f.write("=" * 60 + "\n\n")
        for p in providers:
            f.write(f"{p.name:15} {p.status:15} {p.latency_ms:>6}ms  {p.model}\n")
            if p.error:
                f.write(f"{'':15} Error: {p.error}\n")
        f.write(f"\nTotal OK: {len(ok)} | Rate Limited: {len(rate)} | Sin Key: {len(nokey)} | Error: {len(err)}\n")

    print(f"\nSaved to: {out_path}")
    return 0 if not err else 1


if __name__ == "__main__":
    sys.exit(main())
