import datetime
import hikari
import lightbulb
from lightbulb import checks
from lightbulb.ext import tasks
import os
import re
import time

import beatleader_api
import level
import motd_db
import motd_util
import motd_vars
import motd_playlist
import motd_profile


bot = lightbulb.BotApp(token=os.environ["BS_MOTD_BOT_TOKEN"], prefix=None, default_enabled_guilds=motd_vars.guild)
tasks.load(bot)

@bot.command()
@lightbulb.option("beatleader_id", "Your BeatLeader profile ID")
@lightbulb.command("register", "Register your BeatLeader profile ID to join the Map of the Day competitions")
@lightbulb.implements(lightbulb.SlashCommand)
async def register(ctx: lightbulb.Context) -> None:
	msg = "Discord ID and BeatLeader profile ID have been successfully linked!"

	id = -1
	if re.search("^[0-9]+$", ctx.options.beatleader_id): # Only user ID provided
		id = ctx.options.beatleader_id
	else: # Provided the entire URL
		rgx = re.search("(.*)/u/([0-9]+)(.*)", ctx.options.beatleader_id)
		if rgx:
			id = rgx.group(2)

	if id == -1:
		await ctx.respond("Invalid entry into the ID field! Please input your BeatLeader profile ID.")
	else:
		user_data = motd_db.get_user(discord_id=ctx.user.id)
		if user_data == None: # User doesn't currently exist
			bl_data = motd_db.get_user(beatleader_id=id)
			if bl_data:
				msg = "This BeatLeader profile is already registered!"
			else:
				motd_db.insert_user(ctx.user.id, id)
		else:
			bl_data = motd_db.get_user(beatleader_id=id)
			if bl_data:
				msg = "This BeatLeader profile is already registered!"
			else:
				if user_data["beatleader_id"] == None:
					motd_db.update_user(ctx.user.id, beatleader_id=id)
				else:
					msg = "You are already currently registered! Use `/unregister` to remove any linked BeatLeader profiles."

		await ctx.respond(msg)

@bot.command()
@lightbulb.command("unregister", "Unlinks your BeatLeader profile ID from your Discord account")
@lightbulb.implements(lightbulb.SlashCommand)
async def unregister(ctx: lightbulb.Context) -> None:
	user_data = motd_db.get_user(discord_id=ctx.user.id)
	if user_data:
		motd_db.update_user(ctx.user.id, beatleader_id="")

	await ctx.respond("BeatLeader profile ID has been successfully unregistered!")

@bot.command()
@lightbulb.option("map", "An active leaderboard being competed on", autocomplete=True)
@lightbulb.command("standings", "Lists the accuracy of all players on an active leaderboard")
@lightbulb.implements(lightbulb.SlashCommand)
async def standings(ctx: lightbulb.Context) -> None:
	await ctx.respond("Please wait...")

	leaderboard = motd_db.get_leaderboard(ctx.options.map)

	json = beatleader_api.get_leaderboard(leaderboard["leaderboard_id"], format=True)
	users = motd_db.get_all_users()

	filtered_scores = []
	for user in users:
		try:
			if json["formatted_scores"][f"{user['beatleader_id']}"]:
				json["formatted_scores"][f"{user['beatleader_id']}"]["discordId"] = user["discord_id"]
				filtered_scores.append(json["formatted_scores"][f"{user['beatleader_id']}"])
		except KeyError:
			pass

	filtered_scores = sorted(filtered_scores, key=lambda k: k["accuracy"], reverse=True)

	map_id = json['song']['id'].strip("x")

	msg = f"**Map:** {json['song']['author']} - {json['song']['name']} {json['song']['subName']}\n" \
		  f"**Difficulty:** {json['difficulty']['modeName']} - {json['difficulty']['difficultyName']}\n" \
		  f"**Mapper:** {json['song']['mapper']}\n\n" \
		  f"**Description:** {leaderboard['description']}\n\n" \
		  f"**Start Time:** <t:{leaderboard['start_time']}>\n" \
		  f"**End Time:** <t:{leaderboard['end_time']}>\n\n" \
		  f"**Link:** <https://beatsaver.com/maps/{map_id}>\n\n" \
		  f"**Current Standings:**\n"

	for counter, filtered_score in enumerate(filtered_scores):
		if counter > 19: # Only list the top 20 scores
			break

		discord_user = await bot.rest.fetch_user(filtered_score["discordId"])

		if counter == 0:
			msg += ":first_place: "
		elif counter == 1:
			msg += ":second_place: "
		elif counter == 2:
			msg += ":third_place: "
		else:
			msg += f"{counter + 1}. "

		msg += f"{discord_user.mention} ({round(filtered_score['accuracy'] * 100, 2)}% - {filtered_score['badCuts'] + filtered_score['missedNotes']} misses)\n"

	await ctx.edit_last_response(msg)

@standings.autocomplete("map")
async def active_map_autocomplete(opt, inter):
	active_leaderboards = motd_db.get_active_leaderboards()
	return [hikari.CommandChoice(name=f"[{leaderboard['map_mode']} - {leaderboard['map_diff']}] {leaderboard['song_name']}", value=str(leaderboard["rowid"])) for leaderboard in active_leaderboards]

@bot.command()
@lightbulb.option("map", "A previous Map of the Day leaderboard", autocomplete=True)
@lightbulb.command("history", "Lists the accuracy of a previous Map of the Day leaderboard")
@lightbulb.implements(lightbulb.SlashCommand)
async def history(ctx: lightbulb.Context) -> None:
	await ctx.respond("Please wait...")

	leaderboard = motd_db.get_leaderboard(ctx.options.map)

	msg = f"**Map:** {leaderboard['song_author']} - {leaderboard['song_name']} {leaderboard['song_subname']}\n" \
		  f"**Difficulty:** {leaderboard['map_mode']} - {leaderboard['map_diff']}\n" \
		  f"**Mapper:** {leaderboard['song_mapper']}\n\n" \
		  f"**Description:** {leaderboard['description']}\n\n" \
		  f"**Start Time:** <t:{leaderboard['start_time']}>\n" \
		  f"**End Time:** <t:{leaderboard['end_time']}>\n\n" \
		  f"**Link:** <https://beatsaver.com/maps/{leaderboard['song_id']}>\n\n" \
		  f"**Historical Standings:**\n"

	scores = motd_db.get_scores(lb_rowid=ctx.options.map)
	for score in scores:
		counter = score["rank"] - 1
		if counter > 19: # Only list the top 20 scores
			break
			
		discord_user = await bot.rest.fetch_user(score["discord_id"])

		if counter == 0:
			msg += ":first_place: "
		elif counter == 1:
			msg += ":second_place: "
		elif counter == 2:
			msg += ":third_place: "
		else:
			msg += f"{counter + 1}. "

		msg += f"{discord_user.mention} ({score['accuracy']}% - {score['misses']} misses)\n"

	await ctx.edit_last_response(msg)

@history.autocomplete("map")
async def old_map_autocomplete(opt, inter):
	old_leaderboards = motd_db.get_old_leaderboards()
	return [hikari.CommandChoice(name=f"[{leaderboard['map_mode']} - {leaderboard['map_diff']}] {leaderboard['song_name']}", value=str(leaderboard["rowid"])) for leaderboard in old_leaderboards]

@bot.command()
@lightbulb.option("leaderboard_id", "The BeatLeader leaderboard ID of the map")
@lightbulb.command("leaderboard", "Lists the accuracy of all registered players on the current leaderboard")
@lightbulb.implements(lightbulb.SlashCommand)
async def leaderboard(ctx: lightbulb.Context) -> None:
	await ctx.respond("Please wait...")

	json = beatleader_api.get_leaderboard(ctx.options.leaderboard_id, format=True)
	users = motd_db.get_all_users()

	filtered_scores = []
	for user in users:
		try:
			if json["formatted_scores"][f"{user['beatleader_id']}"]:
				json["formatted_scores"][f"{user['beatleader_id']}"]["discordId"] = user["discord_id"]
				filtered_scores.append(json["formatted_scores"][f"{user['beatleader_id']}"])
		except KeyError:
			pass

	filtered_scores = sorted(filtered_scores, key=lambda k: k["accuracy"], reverse=True)

	msg = f"**Map:** {json['song']['author']} - {json['song']['name']} {json['song']['subName']}\n" \
		  f"**Difficulty:** {json['difficulty']['modeName']} - {json['difficulty']['difficultyName']}\n" \
		  f"**Mapper:** {json['song']['mapper']}\n" \
		  f"**Link:** <https://beatsaver.com/maps/{json['song']['id']}>\n\n" \
		  f"**Current Standings:**\n"

	for counter, filtered_score in enumerate(filtered_scores):
		if counter > 19: # Only list the top 20 scores
			break

		if counter == 0:
			msg += ":first_place: "
		elif counter == 1:
			msg += ":second_place: "
		elif counter == 2:
			msg += ":third_place: "
		else:
			msg += f"{counter + 1}. "

		msg += f"<@{filtered_score['discordId']}> ({round(filtered_score['accuracy'] * 100, 2)}% - {filtered_score['badCuts'] + filtered_score['missedNotes']} misses)\n"

	await ctx.edit_last_response(msg)

@bot.command()
@lightbulb.option("user", "Profile of the user you would like to see", type=hikari.User, required=False)
@lightbulb.command("profile", "See a user's profile")
@lightbulb.implements(lightbulb.SlashCommand)
async def profile(ctx: lightbulb.Context) -> None:
	user_obj = ctx.options.user
	if user_obj is None:
		user_obj = ctx.user

	user = motd_profile.get_profile(user_obj.id)
	user_scores = user["user_scores"]

	embed_msg = hikari.Embed(title=f"{user_obj.username}'s Profile", timestamp=datetime.datetime.now(tz=datetime.timezone.utc))

	if user_obj.avatar_url:
		embed_msg.set_thumbnail(user_obj.avatar_url)
	else:
		embed_msg.set_thumbnail(user_obj.default_avatar_url)

	if len(user_scores) > 0:
		embed_msg.add_field(name="Scores", value=f"{len(user_scores)}", inline=True)
		embed_msg.add_field(name="Top Rank", value=f"{motd_util.ordinal(user_scores[0]['rank'])}", inline=True)

		ordered_scores = sorted(user_scores, key=lambda k: k["rowid"], reverse=True)
		ordered_scores_str = ""
		for counter, score in enumerate(ordered_scores):
			if counter < 5: 
				ordered_scores_str += f"{motd_util.ordinal(score['rank'])}, "
		ordered_scores_str = ordered_scores_str[:-2]

		embed_msg.add_field(name="Recent Ranks (Newest First)", value=ordered_scores_str, inline=True)

	embed_msg.add_field(name="Level", value=f"{user['level']}", inline=True)
	embed_msg.add_field(name="EXP", value=f"{user['exp']} / 100", inline=True)
	embed_msg.add_field(name="\u200b", value="\u200b", inline=True)

	embed_msg.set_footer("Beat Saber Map of the Day")

	await ctx.respond(embed=embed_msg)

@bot.command()
@lightbulb.command("playlist", "Create playlists for Map of the Day - both active maps and all maps")
@lightbulb.implements(lightbulb.SlashCommand)
async def playlist(ctx: lightbulb.Context) -> None:
	await ctx.respond("Please wait...")

	json_active = motd_playlist.create_playlist_response(active=True)
	json_all = motd_playlist.create_playlist_response(active=False)

	await ctx.edit_last_response("Attached are up-to-date playlists for Map of the Day", attachments=[hikari.Bytes(json_active, "motd_active.json"), hikari.Bytes(json_all, "motd_all.json")])

@bot.command()
@lightbulb.add_checks(checks.has_role_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.option("leaderboard_id", "BeatLeader leaderboard ID of the chosen map")
@lightbulb.option("start_time", "Start time in Unix epoch time", required=False)
@lightbulb.option("end_time", "End time in Unix epoch time")
@lightbulb.option("description", "Description of the map", required=False)
@lightbulb.command("schedule", "Set up a new Map of the Day")
@lightbulb.implements(lightbulb.SlashCommand)
async def schedule(ctx: lightbulb.Context) -> None:
	start_time = int(time.time())
	if ctx.options.start_time:
		start_time = ctx.options.start_time

	desc = ""
	if ctx.options.description:
		desc = ctx.options.description

	json = beatleader_api.get_leaderboard(ctx.options.leaderboard_id)
	if json:
		motd_db.insert_leaderboard(json["id"], json["song"]["id"], json["song"]["hash"], json["song"]["name"], json["song"]["subName"], json["song"]["author"],json["song"]["mapper"],
									json["difficulty"]["difficultyName"], json["difficulty"]["modeName"], start_time, ctx.options.end_time, desc)
		await ctx.respond(f"{json['song']['name']} added to the database!")
	else:
		await ctx.respond("There was an issue adding the leaderboard to the database.")

@tasks.task(m=1, auto_start=True)
async def leaderboard_check():
	active_leaderboards = motd_db.get_active_leaderboards()
	epoch_time = int(time.time())

	for lb in active_leaderboards:
		if lb["active"] == 0: # Initially false
			if epoch_time > lb["start_time"] and epoch_time < lb["end_time"]: # Flip to true
				json = beatleader_api.get_leaderboard(lb["leaderboard_id"])

				msg = f"**Map:** {json['song']['author']} - {json['song']['name']} {json['song']['subName']}\n" \
					f"**Difficulty:** {json['difficulty']['modeName']} - {json['difficulty']['difficultyName']}\n" \
					f"**Mapper:** {json['song']['mapper']}\n\n" \
					f"**Description:** {lb['description']}\n\n" \
					f"**Start Time:** <t:{lb['start_time']}>\n" \
					f"**End Time:** <t:{lb['end_time']}>\n\n" \
					f"**Link:** https://beatsaver.com/maps/{json['song']['id']}"

				msg_obj = await bot.rest.create_message(motd_vars.active_channel, msg)
				motd_db.update_leaderboard(lb["rowid"], active=1, msg_id=msg_obj.id)
		elif lb["active"] == 1: # Initially true
			if epoch_time > lb["end_time"]: # Flip to false
				json = beatleader_api.get_leaderboard(lb["leaderboard_id"], format=True)
				users = motd_db.get_all_users()

				filtered_scores = []
				for user in users:
					try:
						if json["formatted_scores"][f"{user['beatleader_id']}"]:
							json["formatted_scores"][f"{user['beatleader_id']}"]["discordId"] = user["discord_id"]
							filtered_scores.append(json["formatted_scores"][f"{user['beatleader_id']}"])
					except KeyError:
						pass

				filtered_scores = sorted(filtered_scores, key=lambda k: k["accuracy"], reverse=True)

				msg = f"**Map:** {json['song']['author']} - {json['song']['name']} {json['song']['subName']}\n" \
					f"**Difficulty:** {json['difficulty']['modeName']} - {json['difficulty']['difficultyName']}\n" \
					f"**Mapper:** {json['song']['mapper']}\n\n" \
					f"**Description:** {lb['description']}\n\n" \
					f"**Start Time:** <t:{lb['start_time']}>\n" \
					f"**End Time:** <t:{lb['end_time']}>\n\n" \
					f"**Link:** https://beatsaver.com/maps/{json['song']['id']}\n\n" \
					f"**Final Standings:**\n"

				for counter, filtered_score in enumerate(filtered_scores):
					motd_db.insert_score(lb["rowid"], lb["leaderboard_id"], filtered_score["discordId"], filtered_score["playerId"], counter + 1, round(filtered_score["accuracy"] * 100, 2), filtered_score["badCuts"] + filtered_score["missedNotes"])
					level.give_exp(filtered_score["discordId"], level.calculate_exp_gain(counter + 1))
					if counter < 3: # Only list the top 3 scores	
						if counter == 0:
							msg += ":first_place: "
						elif counter == 1:
							msg += ":second_place: "
						elif counter == 2:
							msg += ":third_place: "

						msg += f"<@{filtered_score['discordId']}> ({round(filtered_score['accuracy'] * 100, 2)}% - {filtered_score['badCuts'] + filtered_score['missedNotes']} misses)\n"

				await bot.rest.delete_message(motd_vars.active_channel, lb["message_id"])
				msg_obj = await bot.rest.create_message(motd_vars.archived_channel, msg)
				motd_db.update_leaderboard(lb["rowid"], active=0, msg_id=msg_obj.id)
