#!/usr/bin/env python3
"""Debug script để kiểm tra API issues."""

import asyncio
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))


async def debug_chat_service():
    """Debug ChatService và dependencies."""
    try:
        print("🔍 Debugging ChatService...")

        # Test imports
        print("1. Testing imports...")
        from app.services.chat_service import ChatService
        from app.schemas.chat import ChatRequest

        print("   ✅ Imports successful")

        # Test ChatService creation
        print("2. Testing ChatService creation...")
        chat_service = ChatService()
        print("   ✅ ChatService created")

        # Test basic request
        print("3. Testing chat request...")
        request = ChatRequest(message="Hello, test!", model="gpt-5-nano")

        # This will likely fail with OpenAI key missing
        try:
            response = await chat_service.chat(request)
            print(f"   ✅ Chat successful: {response.message.content[:50]}...")
        except Exception as e:
            print(f"   ❌ Chat failed: {type(e).__name__}: {str(e)}")

            # Check specific error types
            if "API key" in str(e).lower():
                print("   💡 Solution: Set OPENAI_API_KEY in .env file")
            elif "connection" in str(e).lower():
                print("   💡 Solution: Check network connectivity")
            else:
                print(f"   💡 Unexpected error: {e}")

        print("\n4. Testing storage...")
        stats = chat_service.storage.get_storage_stats()
        print(f"   ✅ Storage stats: {stats}")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Check if dependencies are installed")
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()


async def debug_config():
    """Debug configuration."""
    try:
        print("\n🔧 Debugging Configuration...")
        from app.core.config import settings

        print(f"   APP_ENV: {settings.APP_ENV}")
        print(f"   DEBUG: {settings.DEBUG}")
        print(f"   SERVER_HOST: {settings.SERVER_HOST}")
        print(f"   SERVER_PORT: {settings.SERVER_PORT}")
        print(f"   DEFAULT_CHAT_MODEL: {settings.DEFAULT_CHAT_MODEL_ID}")

        # Check sensitive configs (masked)
        openai_key = settings.OPENAI_API_KEY
        if openai_key:
            key_str = openai_key.get_secret_value()
            print(
                f"   OPENAI_API_KEY: {'*' * (len(key_str) - 8) + key_str[-8:] if len(key_str) > 8 else '***SET***'}"
            )
        else:
            print("   OPENAI_API_KEY: ❌ NOT SET")

        print(f"   DATABASE_URL: {settings.DATABASE_URL}")
        print(f"   REDIS_URL: {settings.REDIS_URL}")

    except Exception as e:
        print(f"❌ Config error: {e}")


async def main():
    """Main debug function."""
    print("🚀 AmiAgent API Debug Script")
    print("=" * 50)

    await debug_config()
    await debug_chat_service()

    print("\n" + "=" * 50)
    print("🎯 Debug completed!")


if __name__ == "__main__":
    asyncio.run(main())
