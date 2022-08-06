import sqlite3
from os.path import exists

DB_PATH = ".db/store.db"

if not exists(DB_PATH):
	exit()

def get_user(discord_id=None, beatleader_id=None):
	conn = sqlite3.connect(DB_PATH)
	conn.row_factory = sqlite3.Row
	c = conn.cursor()

	if discord_id:
		c.execute("SELECT rowid, * FROM users WHERE discord_id=? LIMIT 1", (discord_id,))
	elif beatleader_id:
		c.execute("SELECT rowid, * FROM users WHERE beatleader_id=? LIMIT 1", (beatleader_id,))

	user_data = c.fetchone()

	conn.commit()
	conn.close()

	if user_data == None:
		return None
	else:
		return dict(user_data)

def get_all_users():
	conn = sqlite3.connect(DB_PATH)
	conn.row_factory = sqlite3.Row
	c = conn.cursor()

	c.execute("SELECT rowid, * FROM users")
	user_data = c.fetchall()

	conn.commit()
	conn.close()
	
	if len(user_data) == 0:
		return []
	else:
		return [dict(it) for it in user_data]

def insert_user(discord_id, beatleader_id):
	conn = sqlite3.connect(DB_PATH)
	c = conn.cursor()

	c.execute("INSERT INTO users (discord_id, beatleader_id, created_at, level, exp) " \
				"VALUES (?, ?, strftime('%s', 'now'), 1, 0)", (discord_id, beatleader_id,))

	conn.commit()
	conn.close()

def update_user(discord_id, beatleader_id=None, level=None, exp=None):
	conn = sqlite3.connect(DB_PATH)
	c = conn.cursor()

	if beatleader_id == "":
		c.execute("UPDATE users SET beatleader_id=null WHERE discord_id=?", (discord_id,))
	elif beatleader_id is not None:
		c.execute("UPDATE users SET beatleader_id=? WHERE discord_id=?", (beatleader_id, discord_id,))

	if level is not None:
		c.execute("UPDATE users SET level=? WHERE discord_id=?", (level, discord_id,))
	if exp is not None:
		c.execute("UPDATE users SET exp=? WHERE discord_id=?", (exp, discord_id,))

	conn.commit()
	conn.close()

def get_leaderboard(rowid):
	conn = sqlite3.connect(DB_PATH)
	conn.row_factory = sqlite3.Row
	c = conn.cursor()

	c.execute("SELECT rowid, * FROM leaderboards WHERE rowid=? LIMIT 1", (rowid,))
	lb_data = c.fetchone()

	conn.commit()
	conn.close()

	if lb_data == None:
		return None
	else:
		return dict(lb_data)

def get_leaderboards():
	conn = sqlite3.connect(DB_PATH)
	conn.row_factory = sqlite3.Row
	c = conn.cursor()

	c.execute("SELECT rowid, * FROM leaderboards")
	lbs = c.fetchall()

	conn.commit()
	conn.close()

	if len(lbs) == 0:
		return []
	else:
		return [dict(it) for it in lbs]

def get_active_leaderboards():
	conn = sqlite3.connect(DB_PATH)
	conn.row_factory = sqlite3.Row
	c = conn.cursor()

	c.execute("SELECT rowid, * FROM leaderboards WHERE (start_time < strftime('%s', 'now') AND end_time > strftime('%s', 'now')) OR active=1 ORDER BY end_time")
	lbs = c.fetchall()

	conn.commit()
	conn.close()

	if len(lbs) == 0:
		return []
	else:
		return [dict(it) for it in lbs]

def get_old_leaderboards():
	conn = sqlite3.connect(DB_PATH)
	conn.row_factory = sqlite3.Row
	c = conn.cursor()

	c.execute("SELECT rowid, * FROM leaderboards WHERE strftime('%s', 'now') > end_time AND active=0 ORDER BY end_time")
	lbs = c.fetchall()

	conn.commit()
	conn.close()

	if len(lbs) == 0:
		return []
	else:
		return [dict(it) for it in lbs]

def insert_leaderboard(lb_id, s_id, s_hash, s_name, s_subname, s_author, s_mapper, m_diff, m_mode, s_time, e_time, desc=""):
	conn = sqlite3.connect(DB_PATH)
	c = conn.cursor()

	c.execute("INSERT INTO leaderboards (leaderboard_id, song_id, song_hash, song_name, song_subname, song_author, song_mapper, map_diff, map_mode, start_time, end_time, active, description) " \
				"VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (lb_id, s_id, s_hash, s_name, s_subname, s_author, s_mapper, m_diff, m_mode, s_time, e_time, 0, desc,))
	
	conn.commit()
	conn.close()

def update_leaderboard(rowid, active=None, msg_id=None, desc=None):
	conn = sqlite3.connect(DB_PATH)
	c = conn.cursor()

	if active is not None:
		c.execute("UPDATE leaderboards SET active=? WHERE rowid=?", (active, rowid,))
	if msg_id is not None:
		c.execute("UPDATE leaderboards SET message_id=? WHERE rowid=?", (msg_id, rowid,))
	if desc is not None:
		c.execute("UPDATE leaderboards SET desc=? WHERE rowid=?", (desc, rowid,))

	conn.commit()
	conn.close()

def insert_score(lb_ref, lb_id, d_id, bl_id, rank, acc, misses):
	conn = sqlite3.connect(DB_PATH)
	c = conn.cursor()

	c.execute("INSERT INTO scores (leaderboard_ref, leaderboard_id, discord_id, beatleader_id, rank, accuracy, misses) " \
				"VALUES (?, ?, ?, ?, ?, ?, ?)", (lb_ref, lb_id, d_id, bl_id, rank, acc, misses,))

	conn.commit()
	conn.close()

def get_scores(lb_rowid=None, d_id=None):
	conn = sqlite3.connect(DB_PATH)
	conn.row_factory = sqlite3.Row
	c = conn.cursor()

	if lb_rowid is not None:
		c.execute("SELECT rowid, * FROM scores WHERE leaderboard_ref=? ORDER BY rank", (lb_rowid,))
	elif d_id is not None:
		c.execute("SELECT rowid, * FROM scores WHERE discord_id=? ORDER BY rank", (d_id,))

	scores = c.fetchall()

	conn.commit()
	conn.close()

	if len(scores) == 0:
		return []
	else:
		return [dict(it) for it in scores]
