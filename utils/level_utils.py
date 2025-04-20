import json
import os

LEVEL_FILE = "data/level.json"
EXP_PER_LEVEL = 600

def load_level_data():
		if not os.path.exists(LEVEL_FILE):
				with open(LEVEL_FILE, "w") as f:
						json.dump({}, f)
		with open(LEVEL_FILE, "r") as f:
				return json.load(f)

def save_level_data(data):
		with open(LEVEL_FILE, "w") as f:
				json.dump(data, f, indent=4)

def get_user_level(user_id):
	uid = str(user_id)
	data = load_level_data()

	if uid not in data:
			data[uid] = {"xp": 0, "level": 1}
			save_level_data(data)

	return data[uid]

def add_exp(user_id, amount=30):
	uid = str(user_id)
	data = load_level_data()

	if uid not in data:
			data[uid] = {"xp": 0, "level": 1}

	user = data[uid]
	user["xp"] += amount

	while user["xp"] >= EXP_PER_LEVEL:
			user["xp"] -= EXP_PER_LEVEL
			user["level"] += 1

	data[uid] = user
	save_level_data(data)
