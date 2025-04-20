import json
import os

DATA_FILE = "data/users.json"


def load_data():
	if not os.path.exists(DATA_FILE):
		with open(DATA_FILE, "w") as f:
			json.dump({}, f)
	with open(DATA_FILE, "r") as f:
		return json.load(f)


def save_data(data):
	with open(DATA_FILE, "w") as f:
		json.dump(data, f, indent=4)


def get_user(user_id):
	data = load_data()
	user_id = str(user_id)
	if user_id not in data:
		data[user_id] = {
		    "money": 0,
		    "last_daily": "1970-01-01T00:00:00",
		    "last_work": "1970-01-01T00:00:00",
		    "exp": 0,
		    "level": 1
		}
		save_data(data)
	return data[user_id]


def get_balance(user_id):
	user = get_user(user_id)
	return user.get("money", 0)


def update_balance(user_id, amount):
	data = load_data()
	user_id = str(user_id)
	user = get_user(user_id)
	user["money"] += amount
	data[user_id] = user
	save_data(data)
	return user["money"]


def set_last_time(user_id, key, time_str):
	data = load_data()
	user_id = str(user_id)
	user = get_user(user_id)
	user[key] = time_str
	data[user_id] = user
	save_data(data)


def get_last_time(user_id, key):
	user = get_user(user_id)
	return user.get(key, "1970-01-01T00:00:00")


def add_exp(user_id, amount):
	data = load_data()
	user_id = str(user_id)
	user = get_user(user_id)
	user["exp"] = user.get("exp", 0) + amount

	current_level = user.get("level", 1)
	next_level_exp = 100 * current_level

	while user["exp"] >= next_level_exp:
		user["exp"] -= next_level_exp
		user["level"] = current_level + 1
		current_level += 1
		next_level_exp = 100 * current_level

	data[user_id] = user
	save_data(data)
	return user["exp"], user["level"]


def get_level_info(user_id):
	user = get_user(user_id)
	exp = user.get("exp", 0)
	level = user.get("level", 1)
	next_level_exp = 100 * level
	return {"level": level, "exp": exp, "next_level_exp": next_level_exp}
