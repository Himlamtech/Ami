"""Seed a test student profile for local development."""

import asyncio

from config.services import ServiceRegistry
from domain.entities.student_profile import StudentProfile, StudentLevel
from infrastructure.persistence.mongodb.client import (
    get_database,
    get_mongodb_client,
)


async def main() -> None:
    db = await get_database()
    ServiceRegistry.initialize(db)

    repo = ServiceRegistry.get_student_profile_repository()

    user_id = "test_user_b22"
    existing = await repo.get_by_user_id(user_id)

    profile = existing or StudentProfile(
        id="",
        user_id=user_id,
    )

    profile.student_id = "B22DCVT303"
    profile.name = "Test Student"
    profile.email = "test.student@ptit.edu.vn"
    profile.phone = "0900000000"
    profile.gender = "male"
    profile.date_of_birth = "2004-08-15"
    profile.address = "Hanoi"
    profile.major = "DCVT"
    profile.faculty = "Vien thong"
    profile.class_name = "D22DCVT03"
    profile.level = StudentLevel.JUNIOR

    progress = profile.get_academic_progress()
    if progress.get("current_year"):
        profile.year = progress["current_year"]

    if existing:
        await repo.update(profile)
    else:
        await repo.create(profile)

    client = await get_mongodb_client()
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
