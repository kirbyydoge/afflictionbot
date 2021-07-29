import pymongo
import os
from pymongo import MongoClient
from globalvars import production

MONGO_TOKEN = os.environ["MONGO_TOKEN"]
client = MongoClient(MONGO_TOKEN)
if production:
    db = client["afflictionbot"]
else:
    db = client["testdb"]

def create_counter(counter_name): # makes human readable id fields for events
    collection = db["counters"]
    result = collection.find({
        "_id": counter_name
    })
    if len(list(result)) > 0:
        return "counterexists"
    collection.insert_one({
        "_id": counter_name,
        "sequence_value": 0
    })
    
def get_next_id(counter_name):  # returns current sequence number and updates named couter
    ret = db["counters"].find_one_and_update({"_id": counter_name}, {"$inc": {"sequence_value": 1}})
    return ret["sequence_value"]
    
def remove_user_from_event(event_id, user_id):  # remove entry of user from event
    collection = db["pvp_event_contenders"]
    collection.delete_one({
        "event_id": event_id,
        "user_id": user_id
    })

def add_user_to_event(event_id, user_id):   # add user to event
    collection = db["pvp_event_info"]
    result = collection.find({
        "event_id": event_id
    })
    if len(list(result)) == 0: # this consumes the result, so if you wanna use it later make sure you save it
        return "noevent"
    collection = db["pvp_event_contenders"]
    post = {
        "event_id": event_id,
        "user_id": user_id
    }
    result = collection.find(post)
    if len(list(result)) > 0:
        return "alreadyjoined"
    collection.insert_one(post)
    return "success"

def get_event_name(event_id):
    collection = db["pvp_event_info"]
    result = collection.find_one({
        "event_id": event_id
    })
    if not result:
        return None
    return result["event_name"]

def get_event_size(event_id):
    collection = db["pvp_event_contenders"]
    result = collection.find({
        "event_id": event_id
    })
    return len(list(result))

def get_event_contenders(event_id):
    collection = db["pvp_event_info"]
    result = collection.find({
        "event_id": event_id
    })
    if len(list(result)) == 0: # this consumes the result, so if you wanna use it later make sure you save it
        return None
    collection = db["pvp_event_contenders"]
    result = collection.find({
        "event_id": event_id
    })
    return list(result)

def get_user_events(user_id):
    collection = db["pvp_event_contenders"]
    result = collection.find({
        "user_id": user_id
    })
    return list(result)

def list_events():
    collection = db["pvp_event_info"]
    result = list(collection.find())
    return result
    
def create_event(event_name):   # create a pvp event with name, id is automatically assigned
    collection = db["pvp_event_info"]
    collection.insert_one({
        "event_id": get_next_id("pvp_id"),
        "event_name": event_name
    })
    
def delete_event(event_id): # remove and event with id
    collection = db["pvp_event_info"]
    collection.delete_one({
        "event_id": event_id
    })

def fetch_youtubers():
    collection = db["youtuber_table"]
    result = list(collection.find())
    return result

def add_youtuber(youtuber_name, channel_url):
    collection = db["youtuber_table"]
    result = collection.find({
        "name": youtuber_name,
        "url": channel_url
    })
    if len(list(result)) > 0:
        return "exists"
    collection.insert_one({
        "name": youtuber_name,
        "url": channel_url
    })
    return "success"

def delete_youtuber(youtuber_name):  
    collection = db["youtuber_table"]
    collection.delete_one({
        "name": youtuber_name
    })

def youtube_cache_save(cached_videos):
    collection = db["bot_cache"]
    collection.delete_one({
        "__cache_name": "youtube"
    })
    cached_videos["__cache_name"] = "youtube"
    collection.insert_one(cached_videos)

def youtube_cache_load():
    collection = db["bot_cache"]
    result = collection.find_one({
        "__cache_name": "youtube"
    })
    return result

def youtube_channel_save(channel_id):
    collection = db["bot_cache"]
    collection.delete_one({
        "__cache_name": "youtube_channel"
    })
    collection.insert_one({
        "__cache_name": "youtube_channel",
        "id": channel_id
    })

def youtube_channel_load():
    collection = db["bot_cache"]
    result = collection.find_one({
        "__cache_name": "youtube_channel"
    })
    return result["id"] if result else None

if __name__ == "__main__":
    create_counter("pvp_id")