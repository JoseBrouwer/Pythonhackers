"""
Server.py will run our website, linking Flask and HTML allowing us to mooify information
provided by the users of our website. Here, we integrate Auth0 our login authentication method.
The code is provided by Auth0 themseleves through their guides.
We also utilize the hackernews API to request news artciles and display them in our website.
"""
#import json
# from builtins import sorted
# from operator import itemgetter
from os import environ as env
from urllib.parse import quote_plus, urlencode

import sqlite3
import requests
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for #, request

# 👆 We're continuing from the steps above. Append this to your server.py file.

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

# 👆 We're continuing from the steps above. Append this to your server.py file.

APP = Flask(__name__)
APP.secret_key = env.get("APP_SECRET_KEY")

PAGE = 0

# 👆 We're continuing from the steps above. Append this to your server.py file.

OAUTH = OAuth(APP)

OAUTH.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

# 👆 We're continuing from the steps above. Append this to your server.py file.

@APP.route("/login")
def login():
    """
    Login function redirects user to call back url located in the auth0 webiste.
    """
    return OAUTH.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

# 👆 We're continuing from the steps above. Append this to your server.py file.

@APP.route("/callback", methods=["GET", "POST"])
def callback():
    """
    after being redirected to the callback url the callback function will run
    This will redirect us to the home page
    """
    token = OAUTH.auth0.authorize_access_token()
    session["user"] = token

    sess = session.get('user') #returns a dictionary with user data
    connection = sqlite3.connect('database.db')
    cur = connection.cursor()
    # print(json.dumps(session.get('user')))

    #inserting the newly logged in user into the users table
    cur.execute("INSERT OR IGNORE INTO users (nickname, name) VALUES (?,?)",
                [sess['userinfo']['nickname'], sess['userinfo']['name']])
    connection.commit()

    return redirect("/")

# 👆 We're continuing from the steps above. Append this to your server.py file.

@APP.route("/logout")
def logout():
    """
    When the logout route is called the following code will logout the user
    returning them to the login page
    """
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

# 👆 We're continuing from the steps above. Append this to your server.py file.
@APP.route("/")
def home():
    """
    This is the code for the home page.
    Here we utilize the hackernews API and request stories to display.
    We store the articles in a list of dictionaries which contain specific
    characteristics of the article
    """
    delete_duplicates() #delete any duplicates in database before displaying likes

    url = 'https://hacker-news.firebaseio.com/v0/topstories.json'
    req = requests.get(url)
    submission_ids = req.json()
    submission_dicts = []
#This code pulls the information from the database and stores them in a dictionary in order
# to keep track of all the current news item in a database
    for submission_id in submission_ids[:20]: #iterate through the first 30 news
        url = ('https://hacker-news.firebaseio.com/v0/item/'+str(submission_id)+'.json')

        submission_r = requests.get(url) #we have obtained a news story
        response_dict = submission_r.json()

        count = select_article_val("artVal", response_dict['title'])
        #count = 0

        #we place story in the submission dictionary with the relevant information
        #in order to then be able to pull relevant information when we need the data later
        submission_dict = {
            'title': response_dict['title'],
            'urlLink': response_dict.get('url', 0),
            'id': response_dict.get('id', 0),
            'likes': count #retrieve likes from query
        }


        submission_dicts.append(submission_dict)
    return render_template("userNews.html", session=session.get('user'),
                           sub=submission_dicts, PAGE=0)

# 👆 We're continuing from the steps above. Append this to your server.py file.

def select_article_val(val, title=None):
    """
    Make a selection from the database of the specified val and
    check the title exists within the database. If so, display
    the right amount of likes across users. If the title is not
    in the database display the likes as 0.
    """
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    if val == "artVal": #when requesting like or dislike
        #query likes
        cur.execute("SELECT " + val + ",artTitle FROM articles WHERE artVal=1 AND artTitle=?",
                    (title, ))
        rows1 = cur.fetchall() #place like tuples in list
        cur.execute("SELECT " + val + ",artTitle FROM articles WHERE artVal=-1 AND artTitle=?",
                    (title, ))
        rows2 = cur.fetchall()
        total = 0
        for row in rows1:
            print(row)
            total = total + 1 #add 1 to total likes if in rows1 list
        for row in rows2:
            print(row)
            total = total - 1 #subtract 1 from total if in rows2
        return total
    return 0

def delete_duplicates():
    """
    We delete all of the duplicates in the database
    by querying all of the entries that have the same data
    and appear more than once. We then place these duplicates
    in the dupes list, enumarate it and use it ro repopulate the database
    after deleting all entries that are duplicates
    """
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    #get duplicate rows
    cur.execute("SELECT * FROM articles \
                GROUP BY nickname,name,artTitle,artId,artVal \
                HAVING COUNT(*) > 1;")

    rows = cur.fetchall()
    print("duplicates collected: \n")
    dupes = [] #list of duplicates
    if len(rows) > 0: # if we have dupes
        for row in rows:
            print(row)
            dupes.append(row) #store in dupes list
        print("\n")
        print("dupes list: \n")
        print(list(enumerate(dupes))) #enum dupes to access later

    for row in rows: #delete all duplicate entries
        cur.execute("DELETE FROM articles \
                    WHERE nickname LIKE '{}'".format(row[0])+
                    " AND artId={}".format(row[3]))

    index = 0 #index for enum dupes
    for row in rows: #insert items in dupes list
        cur.execute("INSERT OR IGNORE INTO articles\
            (nickname, name, artTitle, artId, artVal) VALUES(?, ?, ?, ?, ?)",
                    [dupes[index][0], dupes[index][1], dupes[index][2],
                     dupes[index][3], dupes[index][4]])
        index = index + 1

    conn.commit()
    conn.close()

@APP.route("/like/<art_title>/<int:art_id>/<action>")
def like(art_title, art_id, action):
    """
    This function will run when the client interacts with the like or dislike buttons.
    The function will load the json passed from the javascript function
    We establish a connection with the database
    Then we insert the information from the jason into the database
    we commit the changes and close the connection
    """
    print("In like function\n")
    sess = session.get('user')
    if action == "like":
        val = 1
    else:
        val = -1
    #dictionary to store provided values along like val
    art_info = {'Title': art_title, 'Id': art_id, 'Val': val}

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        #insert appropriate information into articles table
        cursor.execute("INSERT OR IGNORE INTO articles\
                       (nickname, name, artTitle, artId, artVal) VALUES(?, ?, ?, ?, ?)",
                       [sess['userinfo']['nickname'], sess['userinfo']['name'],
                        art_info['Title'], art_info['Id'], art_info['Val']])
        conn.commit()
    except sqlite3.Error as error:
        print("Connection to sqlite failed due to error", error)
    finally:
        if conn:
            cursor.close()
            conn.close()
    return redirect("/")

@APP.route("/profile")
def profile():
    """
    loads the user profile page which contains their name and email
    """
    return render_template("profile.html", session=session.get('user'))

@APP.route("/delete/<title>/<user>")
def delete(title, user):
    """
    Function which deletes the entry by the admin, takes in the title and the user in order to
    query the database and delete the appropriate entry
    """
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("Delete FROM articles WHERE name=? AND artTitle=?",
                (user, title, ))

    conn.commit()
    conn.close()

    return redirect("/adminView")

@APP.route("/adminView")
def admin_view():
    """
    loads the admin view page for qualifying users,
    connects to the appropriate database and selects all the articles which have been liked and what
    users liked it
    """
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM articles")
    rows = cur.fetchall()
    likes = []
#appends the row to the end of a list of likes in order to return the relevant info
    for row in rows:
        likes.append(row)

    return render_template("adminView.html", session=session.get('user'), articles=likes)

if __name__ == "__main__":
    APP.run(host="64.227.27.0", port=env.get("PORT", 3000), debug=True)

