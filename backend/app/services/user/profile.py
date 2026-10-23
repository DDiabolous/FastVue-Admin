from app.services.user.auth import profile


async def update_profile(db, user, changes):
    for name, value in changes.items():
        setattr(user, name, value)
    await db.commit()
    return profile(user)
