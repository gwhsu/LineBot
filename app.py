from pickle import APPENDS
from re import S
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
from mongodb import *
import tempfile
from function import *
import os
from dotenv import load_dotenv

# ======setting=====
game_start = 0  # no use now
low = 1  # no use now
high = 100  # no use now
talk_mode = -1  # -1:非初始 0:初始 1:安靜 2:講話  # no use now
control_img = 0  # no use now
control_game = 0  # no use now
control_msg = 0  # no use now
switch = False

# get environment variable
load_dotenv('/etc/secrets/config.env')
line_channel_access_token = os.getenv('line_channel_access_token')
line_channel_secret = os.getenv('line_channel_secret')

# -----------------------------
app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
# Channel Access Token
line_bot_api = LineBotApi(line_channel_access_token)
# Channel Secret
handler = WebhookHandler(line_channel_secret)


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global game_start, key, low, high, talk_mode, switch
    message = None
    msg = event.message.text
    
    user_id = event.source.user_id
    profile = line_bot_api.get_profile(user_id)

    # INFO -------------------------------
    print("-----------User-----------")
    print("name : ", profile.display_name)
    print("userID : ", profile.user_id)
    print("profile : ", profile.picture_url)
    print("statusMessage : ", profile.status_message)

    try:
        group_id = event.source.group_id
        summary = line_bot_api.get_group_summary(group_id)
        check_group_DB(summary.group_id, summary.group_name)

        print("-----------Group-----------")
        print("groupID : ",summary.group_id)
        print("groupName : ",summary.group_name)
        print("groupProfile : ",summary.picture_url)
    except:
        pass

    print("\n")
    
    # check user data in DB
    check_user_DB(profile.user_id, profile.display_name)

    # need build a operation list (json)
    if 'Hello' in msg:
        message = 'Hello ' + str(profile.display_name)
        message = TextSendMessage(text=message)

    elif '!op' in msg:
        txt = '🔥 ' + 'Hello' + ' 🔥\n'
        txt += '🔥 ' + '抽卡' + ' 🔥\n'
        txt += '🔥 ' + '幹你娘' + ' 🔥\n'
        txt += '🔥 ' + 'CC' + ' 🔥\n'
        txt += '🔥 ' + '占卜 @[str]' + ' 🔥\n'
        txt += '🔥 ' + 'Tofu' + ' 🔥\n'
        txt += '🔥 ' + '!Hulan [str] [int]' + ' 🔥\n'
        txt += '🔥 ' + '!sendTo [name] [str]' + ' 🔥\n'
        txt += '🔥 ' + '!broadcast' + ' 🔥\n'

        message = TextSendMessage(text=txt)

    elif '占卜 @' in msg:
        message = procast(msg)

    elif 'CC' in msg:
        msg = '你在笑什麼'
        message = TextSendMessage(text=msg)

    elif '抽卡' in msg:
        url, rd_img, title = get_pttinfo()
        message = ptt_drawcard(url, rd_img, title)

    elif '!Hulan' in msg:
        message = Hulan(msg)

    elif '幹你娘' in msg:
        message = StickerSendMessage(package_id='1', sticker_id='8')

    elif 'Tofu' in msg:
        txt = '好想吃豆腐~~'
        message = TextSendMessage(text=txt)

    elif 'TofuEye' in msg:
        message = ImageSendMessage(
            original_content_url='https://i.imgur.com/Fmghect.jpg',
            preview_image_url='https://i.imgur.com/Fmghect.jpg'
        )

    elif '!Switch' in msg:
        if(switch):
            switch = False
            txt = '關 :('
        else:
            switch = True
            txt = '開 :)'
        message = TextSendMessage(text=txt)

    elif '!getlineid' in msg:
        lineid_mapping(profile.display_name, profile.user_id)
        message = TextSendMessage(text=profile.user_id)

    elif '!broadcast' in msg:
        message = msg.split(' ')[1]
        line_bot_api.broadcast(TextSendMessage(text=message))
    
    elif '!sendTo' in msg:
        name = msg.split(' ')[1]
        text = msg.split(' ')[2]
        userID = nameMapID(name)
        
        if userID:
            line_bot_api.push_message(userID, TextSendMessage(text=text))
        else:    
            message = TextSendMessage(text="The name was not found")

    if message:
        line_bot_api.reply_message(event.reply_token, message)


@handler.add(MessageEvent, message=ImageMessage)
def handle_message(event):
    if isinstance(event.message, ImageMessage) and switch:
        print('Start:..........')
        ext = 'jpg'
        message_content = line_bot_api.get_message_content(event.message.id)
        with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
            for chunk in message_content.iter_content():
                tf.write(chunk)
            tempfile_path = tf.name

        dist_path = tempfile_path + '.' + ext
        dist_name = os.path.basename(dist_path)
        os.rename(tempfile_path, dist_path)

        try:
            path = os.path.join('static', 'tmp', dist_name)
            img_uri = img2anime(path)

            print('Message::', img_uri)
            message = ImageSendMessage(original_content_url=img_uri, preview_image_url=img_uri)
            line_bot_api.reply_message(event.reply_token, message)

        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='上傳失敗'))


@handler.add(JoinEvent)
def handle_join(event):
    newcoming_text = "開始報告"

    line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text=newcoming_text)
        )
    print("JoinEvent =", JoinEvent)


@handler.add(LeaveEvent)
def handle_leave(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextMessage(text="Where I am , U r where ")
    )
    print("leave Event =", event)
    print("我被踢掉了QQ ", event.source)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)