from flask import Flask, request, abort

from config import client_id, client_secret, album_id, access_token, refresh_token, client_mongo, line_channel_access_token, line_channel_secret

# ======這裡是呼叫的檔案內容=====
from function import *
import os
# ======這裡是呼叫的檔案內容=====
game_start = 0
low = 1
high = 100
talk_mode = -1  # -1:非初始 0:初始 1:安靜 2:講話
control_img = 0
control_game = 0
control_msg = 0
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
    global game_start, key, low, high, talk_mode
    msg = event.message.text

    user_id = event.source.user_id
    print('get user id::', user_id)
    profile = line_bot_api.get_profile(user_id)
    print('get profile pass::', profile)
    # INFO -------------------------------
    print(profile.display_name)
    print(profile.user_id)
    print(profile.picture_url)
    print(profile.status_message)
    print('join')

    if 'Hello' in msg:
        message = 'Hello' + profile.display_name
        line_bot_api.reply_message(event.reply_token, message)

    elif '占卜一個人 @' in msg:
        message = procast(msg)
        line_bot_api.reply_message(event.reply_token, message)

    elif 'Start......' in msg:
        message = TextSendMessage(text='game_start: 輸入1~100的數字')
        line_bot_api.reply_message(event.reply_token, message)
        key = random.randint(low, high)
        game_start = 1

    elif '貼圖' in msg:
        message = StickerSendMessage(package_id='1', sticker_id='2')
        line_bot_api.reply_message(event.reply_token, message)

    else:
        message = set_msg(msg)
        line_bot_api.reply_message(event.reply_token, message)


# 處理貼圖
'''
@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker(event):
    if control_game != 0:
        if game_start == 0:
            message = game(event)
            line_bot_api.reply_message(event.reply_token, message)
'''

# 處理圖片
@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    if isinstance(event.message, ImageMessage):
        '''
        url = images[index].link
        image_message = ImageSendMessage(
            original_content_url=url,
            preview_image_url=url
        )
        '''
        # line_bot_api.reply_message(event.reply_token, image_message)
        # line_bot_api.reply_message(event.reply_token, message)

        return 0


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
