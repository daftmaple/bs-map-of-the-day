import motd_db


def get_profile(d_id):
    user = motd_db.get_user(discord_id=d_id)
    user_scores = motd_db.get_scores(d_id=d_id)

    user["user_scores"] = user_scores

    return user