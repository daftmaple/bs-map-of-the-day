import motd_db


def give_exp(id, exp):
    user = motd_db.get_user(discord_id=id)

    total_exp = user["exp"] + exp
    level_ups = total_exp // 100
    extra_exp = total_exp % 100

    new_level = user["level"] + level_ups

    motd_db.update_user(id, level=new_level, exp=extra_exp)


# 1 Level = 100 EXP
def calculate_exp_gain(rank):
    if rank <= 3:
        return 100 / (2 ** (rank - 1))
    else:
        return 10