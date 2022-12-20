# -*- coding:utf-8 -*-

from pymongo import MongoClient
from extEnv import *
from linebot.models import *

# get mongoDB database
mongo_client = MongoClient(mongo_client)
mongo_client_ccsue = MongoClient(mongo_client_ccsue)


def get_pttinfo():
    db = mongo_client.get_database('PTT')
    record = db.beauty_data
    q = record.aggregate([{'$sample': {'size': 1}}])
    for x in q:
        url = x['url']
        rd_img = x['img']
        title = x['title']
    return url, rd_img, title

def lineid_mapping(display_name, userid):
    db = mongo_client_ccsue.get_database('linebot')
    record = db.id_map
    post = {str(display_name): str(userid)}
    record.insert_one(post)

def check_user_DB(userID, name):
    db = mongo_client_ccsue.get_database('linebot')
    record = db['userID_map']

    # find exist in DB
    if record.find_one({"ID":userID}):
        return

    post = {"name":str(name), "ID":userID}
    record.insert_one(post)

def check_group_DB(groupID, name):
    db = mongo_client_ccsue.get_database('linebot')
    record = db['groupID_map']

    # find exist in DB
    if record.find_one({"ID":groupID}):
        return

    post = {"name":str(name), "ID":groupID}
    record.insert_one(post)

def nameMapID(name):
    db = mongo_client_ccsue.get_database('linebot')
    List = [db['userID_map'], db['groupID_map']]

    for data in List:
        entry = data.find_one({"name":str(name)})
        if entry:
            return entry["ID"]

    return None