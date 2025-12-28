"""Clean up empty chat sessions (sessions with 0 messages)."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import mongodb_config
from infrastructure.persistence.mongodb.client import MongoDBClient


async def clean_empty_sessions():
    """Delete all chat sessions that have 0 messages."""
    client = MongoDBClient(mongodb_config)
    await client.connect()

    try:
        # Find all sessions with message_count = 0
        empty_sessions = await client.db.chat_sessions.find(
            {"message_count": 0, "is_deleted": False}
        ).to_list(length=None)

        if not empty_sessions:
            print("✅ No empty sessions found")
            return

        print(f"Found {len(empty_sessions)} empty sessions")

        # Soft delete them
        result = await client.db.chat_sessions.update_many(
            {"message_count": 0, "is_deleted": False}, {"$set": {"is_deleted": True}}
        )

        print(f"✅ Deleted {result.modified_count} empty sessions")

        # Show some examples
        for session in empty_sessions[:5]:
            print(
                f"  - {session['_id']}: '{session.get('title', 'Untitled')}' (user: {session.get('user_id', 'unknown')})"
            )

        if len(empty_sessions) > 5:
            print(f"  ... and {len(empty_sessions) - 5} more")

    finally:
        await client.close()


if __name__ == "__main__":
    print("🧹 Cleaning empty chat sessions...")
    asyncio.run(clean_empty_sessions())
    print("✨ Done!")
