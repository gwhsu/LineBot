import os
import tempfile
from re import S
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
from mongodb import *
from function import *
from extEnv import *


# ======setting=====
game_start = 0  # no use now
low = 1  # no use now
high = 100  # no use now
talk_mode = -1  # -1:非初始 0:初始 1:安靜 2:講話  # no use now
control_img = 0  # no use now
control_game = 0  # no use now
control_msg = 0  # no use now
switch = False

# flask
app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

# Channel Access Token & Channel Secret
line_bot_api = LineBotApi(line_channel_access_token)
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
    msg = event.message.text
    
    user_id = event.source.user_id
    profile = line_bot_api.get_profile(user_id)

    # INFO -------------------------------
    print("-----------User-----------")
    print("name : ", profile.display_name)
    print("userID : ", profile.user_id)
    print("profile : ", profile.picture_url)
    print("statusMessage : ", profile.status_message)
    print("msg : ", msg)

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

    # operation list
    operationFuncs = {
        '!op' : operationList,
        '占卜' : procast,
        '抽卡' : ptt_drawcard, 
        '!Hulan' : Hulan,
        '!broadcast' : broadcast,
        '!sendTo' : sendTo
    }
    try:
        operationFuncs.get(msg.split()[0](event, msg))
    except:
        message = TextSendMessage(text='Got some error')
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