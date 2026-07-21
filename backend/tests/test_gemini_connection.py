"""Standalone test – verify Google Gemini API connection.

Run from the backend directory:
    python -m tests.test_gemini_connection

This bypasses the full app and tests the Gemini client directly so we
can isolate API key / model / SDK issues quickly.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Load .env from backend/ (same location main.py uses)
# ---------------------------------------------------------------------------
_backend_dir = Path(__file__).resolve().parent.parent
try:
    from dotenv import load_dotenv
    load_dotenv(_backend_dir / ".env")
    print(f"[OK]  .env loaded from {_backend_dir / '.env'}")
except ImportError:
    print("[WARN] python-dotenv not installed – relying on shell env vars")

# ---------------------------------------------------------------------------
# 1. Check environment variables
# ---------------------------------------------------------------------------

print("\n=== Step 1: Environment Variables ===")

api_key = os.getenv("GEMINI_API_KEY", "")
model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

if not api_key:
    print("[FAIL] GEMINI_API_KEY is not set!")
    print("       Set it in backend/.env or export it in your shell.")
    sys.exit(1)

masked = api_key[:6] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
print(f"  GEMINI_API_KEY : {masked}  ({len(api_key)} chars)")
print(f"  GEMINI_MODEL   : {model}")

if len(api_key) < 10:
    print("[FAIL] API key looks too short – probably invalid.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 2. Check SDK import
# ---------------------------------------------------------------------------

print("\n=== Step 2: SDK Import ===")

try:
    from google import genai
    from google.genai import types
    print(f"[OK]  google-genai imported successfully")

    # Check for conflicting google-generativeai
    try:
        import google.generativeai  # noqa: F401
        print("[WARN] google-generativeai is also installed – this can cause conflicts.")
        print("       Run: pip uninstall google-generativeai")
    except ImportError:
        print("[OK]  google-generativeai is NOT installed (good)")

except ImportError as e:
    print(f"[FAIL] Cannot import google-genai: {e}")
    print("       Run: pip install google-genai")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 3. Create client
# ---------------------------------------------------------------------------

print("\n=== Step 3: Client Creation ===")

try:
    client = genai.Client(api_key=api_key)
    print(f"[OK]  genai.Client created")
except Exception as exc:
    print(f"[FAIL] Could not create client: {exc}")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 4. Simple API call (sync)
# ---------------------------------------------------------------------------

print("\n=== Step 4: API Call (Synchronous) ===")

try:
    response = client.models.generate_content(
        model=model,
        contents="Say exactly one word: hello",
        config=types.GenerateContentConfig(
            max_output_tokens=10,
            temperature=0.0,
        ),
    )
    text = response.text or ""
    print(f"[OK]  Response: \"{text.strip()}\"")
except Exception as exc:
    exc_msg = str(exc)
    print(f"[FAIL] API call failed: {type(exc).__name__}: {exc_msg}")

    if "API_KEY_INVALID" in exc_msg or "api key not valid" in exc_msg.lower():
        print()
        print("  Possible causes:")
        print("  1. The key was revoked or expired in Google AI Studio")
        print("  2. The key belongs to a different Google Cloud project")
        print("  3. Copy-paste error (missing/extra characters)")
        print()
        print("  Fix: Go to https://aistudio.google.com/apikey")
        print("       Create a new key and update backend/.env")
    elif "INVALID_ARGUMENT" in exc_msg:
        print()
        print(f"  The model '{model}' may not exist or not be available.")
        print("  Try: gemini-2.0-flash, gemini-2.5-flash, gemini-2.5-pro")
    elif "PERMISSION_DENIED" in exc_msg:
        print()
        print("  The API key does not have access to this model.")
        print("  Check your Google Cloud project permissions.")
    elif "RESOURCE_EXHAUSTED" in exc_msg or "quota" in exc_msg.lower():
        print()
        print("  You have hit the API rate limit or quota.")
        print("  Wait a minute and try again, or check your billing.")

    sys.exit(1)

# ---------------------------------------------------------------------------
# 5. Async API call
# ---------------------------------------------------------------------------

print("\n=== Step 5: API Call (Async) ===")

import asyncio

async def _test_async():
    response = await client.aio.models.generate_content(
        model=model,
        contents="Say exactly one word: world",
        config=types.GenerateContentConfig(
            max_output_tokens=10,
            temperature=0.0,
        ),
    )
    return response.text or ""

try:
    text = asyncio.run(_test_async())
    print(f"[OK]  Response: \"{text.strip()}\"")
except Exception as exc:
    print(f"[FAIL] Async call failed: {type(exc).__name__}: {exc}")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

print("\n" + "=" * 50)
print("ALL CHECKS PASSED – Gemini API is working correctly!")
print("=" * 50)
