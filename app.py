from flask import Flask
import praw
import time
import os
import re
import pymongo
from threading import Thread
import certifi
from asyncpraw.models import MoreComments
from Reddit_ChatBot_Python import ChatBot, RedditAuthentication
from Reddit_ChatBot_Python import CustomType, Snoo, Reaction
import ssl

app = Flask(__name__)
 
@app.route("/")
def home_view():
        print("HOMEVIEEEEEEW")
        return "<h1>Welcome!</h1><h2>You can check my Exway promo code:</h2><h2><a href='https://www.reddit.com/r/Exway/comments/jlh9p2/disc0unts_on_exway_boards_updated/?utm_medium=android_app&utm_source=share'>https://www.reddit.com/r/Exway/comments/jlh9p2/disc0unts_on_exway_boards_updated/?utm_medium=android_app&utm_source=share</a></h2>"

conn_str = "mongodb+srv://Exway_hawk_eye:shotsXAEA-XII12@cluster0.nqljd.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"

client = pymongo.MongoClient(conn_str, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)

reddit_authentication = RedditAuthentication.PasswordAuth(reddit_username="exway-helper", reddit_password="shotsXAEA-XII12", twofa=None)

#reddit_authentication = RedditAuthentication.PasswordAuth(reddit_username="exway-mailer", reddit_password="exway284agc", twofa=None)

chatbot = ChatBot(print_chat=True, store_session=True, log_websocket_frames=False, authentication=reddit_authentication)

#chatbot.enable_rate_limiter(max_calls=23, period=1.5)

try:
    print("CONNECTED TO DB SUCCESSFULLY!")
    print(client.server_info())
except Exception as e:
    print("Error connecting to db")
    print(e)

db = client.BigData
reddit = db.r1
chat = db.r2

def bot_login():
    print("Logging in...")
    """r = praw.Reddit(username="exway_assistance",
                    password="exway284agc",
                    client_id="x5lxnULe7oaYw-takx7uBQ",
                    client_secret="4BzMjGh10NWevxtnxb9m07Qv1HjUlg",
                    user_agent="exway_assistance",
                    redirect_uri="https://exway-hawk-eye.herokuapp.com/"
                    )"""
    """r = praw.Reddit(username="exway-helper",
                    password="shotsXAEA-XII12",
                    client_id="JxdBVsEQbWMLG9XAAnePog",
                    client_secret="gB7IjdnzFzBlShmJ0Qf8T9tojyNraA",
                    user_agent="exway-helper",
                    redirect_uri="https://exway-hawk-eye.herokuapp.com/"
                    )"""
    r = praw.Reddit(username="exway-mailer",
                    password="exway284agc",
                    client_id="ZWAU7J8n4DlbuoLPhUD4zw",
                    client_secret="z6NXNWwRE3y-eIO26_8kzGf5XdxbBQ",
                    user_agent="exway-mailer",
                    redirect_uri="https://exway-hawk-eye.herokuapp.com/"
                    )
    print(r.user.me())
    if r:
        print("Logged in!")
    else:
        print("ERROR LOGGING IN")

    return r

err_ans = []
chat_err_ans = []

def run_bot(r, comments_replied_to, chats_replied_to):
    print("Searching last 1,000 comments")
    
    url = "https://www.reddit.com/r/ElectricSkateboarding/comments/n28k7u/recommendations_and_suggestions/"
    submission = r.submission(url=url)
    submission.comment_sort = 'new'
    submission.comments.replace_more(limit=0)
    for comment in submission.comments.list():
        id = str(comment.author)
        if re.search("Exway", comment.body, flags=re.I) and comment.id not in chats_replied_to and comment.author != r.user.me() and comment.created_utc > 1663751982.0:
            print("comment found-chat")
            
            try:
                dm1(id)
                print("Chatted to comment " + comment.id)
                print("Chat receiver was: " + id)
                chats_replied_to.append(comment.id)
                chat.insert_one({ "id": comment.id, "author": comment.author.name, "url": comment.permalink, "timestamp": comment.created_utc, "err_message": "None"})
            except Exception as e:
                print(chat_err_ans)
                cors = False
                if len(chat_err_ans) > 0:
                    for i in chat_err_ans:
                        if i["id"] == comment.id:
                            cors = True
                            i["n"]+=1
                            if i["n"] >= 1:
                                chat_err_ans.remove(i)
                                chats_replied_to.append(comment.id)
                                chat.insert_one({ "id": comment.id, "author": comment.author.name, "url": comment.permalink, "timestamp": comment.created_utc, "err_message": str(e)})
                    if cors == False:
                        chat_err_ans.append({"id": comment.id, "n": 0})
                else:
                    chat_err_ans.append({"id": comment.id, "n": 0})

                print("Exception error in chat, retrying: ")
                print(e)
                print(chat_err_ans)
        
        if re.search("Exway", comment.body, flags=re.I) and comment.id not in comments_replied_to and comment.author != r.user.me() and comment.created_utc > 1663751982.0:
            
            print("comment found")
            print(comment.body)
            print(comment.created_utc)
            print("String with \"exway\" found in comment (id) " + comment.id)
            
            
            try:
                r.redditor(id).message(subject = 'EXWAY SUPPORT TEAM', message = 'Hey there! Thanks for your support to Exway. If you end up buying a board and you ever have a problem just pm u/alxpht or reply here. Thanks bro :). Oh and btw it helps me a lot if you use my promo code: www.reddit.com/r/Exway/comments/jlh9p2/disc0unts_on_exway_boards_updated/')
                print("Replied to comment " + comment.id)
                print("Receiver was: " + id)
                comments_replied_to.append(comment.id)
                reddit.insert_one({ "id": comment.id, "author": comment.author.name, "url": comment.permalink, "timestamp": comment.created_utc, "err_message": "None"})
            except Exception as e:
                print(err_ans)
                corr = False
                if len(err_ans) > 0:
                    for i in err_ans:
                        if i["id"] == comment.id:
                            corr = True
                            i["n"]+=1
                            if i["n"] >= 3:
                                err_ans.remove(i)
                                comments_replied_to.append(comment.id)
                                reddit.insert_one({ "id": comment.id, "author": comment.author.name, "url": comment.permalink, "timestamp": comment.created_utc, "err_message": str(e)})
                    if corr == False:
                        err_ans.append({"id": comment.id, "n": 0})
                else:
                    err_ans.append({"id": comment.id, "n": 0})

                print("Exception error, retrying: ")
                print(e)
                print(err_ans)
                
        
    print("Search Completed.")
    print("Sleeping for 10 seconds...")
    # Sleep for 10 seconds...
    time.sleep(10)

def get_saved_comments():
    comments_replied_to = []
    found = reddit.find()
    for i in found:
        comments_replied_to.append(i["id"])

    return comments_replied_to

def get_saved_chats():
    comments_replied_to = []
    found = chat.find()
    for i in found:
        comments_replied_to.append(i["id"])

    return comments_replied_to


r = bot_login()
comments_replied_to = get_saved_comments()
chats_replied_to = get_saved_chats()
print(comments_replied_to)

def func():
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
        pass
    else:
    # Handle target environment that doesn't support HTTPS verification
        ssl._create_default_https_context = _create_unverified_https_context
    
    while True:
        run_bot(r, comments_replied_to, chats_replied_to)

def func1():
    chatbot.run_4ever(auto_reconnect=True, disable_ssl_verification=True)

"""@chatbot.event.on_ready
def dm(_):
    print('GOING ON')
    dm_channel = chatbot.create_direct_channel("New_Finalizer_28")
    chatbot.send_message('Hey there!', dm_channel.channel_url)
    chatbot.send_message('Thanks for your support to Exway. If you end up buying a board and you ever have a problem just pm u/alxpht or reply here. Thanks bro :)', dm_channel.channel_url)
    chatbot.send_message('Oh and btw it helps me a lot if you use my promo code: www.reddit.com/r/Exway/comments/jlh9p2/disc0unts_on_exway_boards_updated/', dm_channel.channel_url)"""

def dm1(id):
    print('msgins')
    dm_channel = chatbot.create_direct_channel(id)
    chatbot.send_message('Hey there!', dm_channel.channel_url)
    chatbot.send_message('Thanks for your support to Exway. If you end up buying a board and you ever have a problem just pm u/alxpht or reply here. Thanks bro :)', dm_channel.channel_url)
    chatbot.send_message('Oh and btw it helps me a lot if you use my promo code: www.reddit.com/r/Exway/comments/jlh9p2/disc0unts_on_exway_boards_updated/', dm_channel.channel_url)

if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 5000))
    Thread(target = func).start()
    Thread(target = func1).start()
    app.run(use_reloader=False, host='0.0.0.0', port=puerto)
    

