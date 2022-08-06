import requests


def get_leaderboard(leaderboard_id, format=False):
	response = requests.get(f"https://api.beatleader.xyz/leaderboard/{leaderboard_id}?page=1&count=2000")

	json = None

	try:
		json = response.json()
	except requests.JSONDecodeError:
		return None

	if format == True: # Reorganize data for better performance
		formatted_scores = {}

		for score in json["scores"]:
			formatted_scores[f"{score['playerId']}"] = score

		json["formatted_scores"] = formatted_scores

	return json
