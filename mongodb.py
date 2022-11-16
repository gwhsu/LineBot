# -*- coding:utf-8 -*-

from pymongo import MongoClient
from imgurpython import ImgurClient
from config import client_id, client_secret, access_token, refresh_token, mongo_client, mongo_client_ccsue
from linebot.models import *

client = ImgurClient(client_id, client_secret, access_token, refresh_token)


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

