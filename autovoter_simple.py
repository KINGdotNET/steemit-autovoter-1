from steem import Steem
from steem.blockchain import Blockchain
from steem.post import Post
from steem.account import Account
from datetime import datetime
import json, os

def converter(object_):
	if isinstance(object_, datetime.datetime):
		return object_.__str__()

def create_json():
	user_json = {}
	for user in Account(username).export()["following"]:
		user_json[user] = {
			"upvote_weight" : 100.0,
			"upvote_limit" : 2,
			"upvote_count" : 0
		}
	return user_json

def limit_reached(user_json, author):
	if user_json[author]["upvote_limit"] == user_json[author]["upvote_count"]:
		return True
	else:
		return False

def valid_post(post, user_json):
	title  = post["title"]
	author = post["author"]
	
	if (post.is_main_post()
		and author in user_json
		and not limit_reached(user_json, author)):
		user_json[author]["upvote_count"] += 1
		return True
	else:
		return False

def run(user_json):
	username   = "amosbastian"
	wif        = os.environ.get("UNLOCK")
	steem      = Steem(wif=wif)
	blockchain = Blockchain()
	stream 	   = map(Post, blockchain.stream(filter_by=["comment"]))

	print("Entering blockchain stream!")
	while True:
		try:
			for post in stream:
				if valid_post(post, user_json):
					try:
						author = post["author"]
						post.upvote(weight=user_json[author]["upvote_weight"],
							voter=username)
					except Exception as error:
						print(repr(error))
						continue

		except Exception as error:
			# print(repr(error))
			continue

if __name__ == '__main__':
	# user_json = create_json()
	with open("user_json.json") as json_data:
		user_json = json.load(json_data)
	run(user_json)
