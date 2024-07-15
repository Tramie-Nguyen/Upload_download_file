import os
import pymongo

user_col = None


def connect_database():
    global user_col

    try:
        myClient = pymongo.MongoClient(os.getenv("MONGODB_URL"))
        db = myClient["send_file_project"]
        user_col = db["users"]
        return "Connected to MongoDB successfully!", user_col
    except pymongo.errors.ConnectionFailure as e:
        return "Failed to connect to MongoDB", None
