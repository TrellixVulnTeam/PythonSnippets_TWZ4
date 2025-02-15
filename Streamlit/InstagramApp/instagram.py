# This script is inspired by below article:
# https://predictivehacks.com/how-to-create-an-instagram-profile-analyzer-app-using-python-and-streamlit/

import streamlit as st

import requests
import pandas as pd
import os 
import json
import re
from datetime import datetime


st.title("Instagram Dashboard")

with st.form(key="my_form"):
    username = st.text_input(label="Enter User Name:", value="billybonaros")
    submit_button = st.form_submit_button(label="Submit")

if submit_button:
    try:
        if not os.path.exists(f"{username}"):
            os.system(f"instagram-scraper '{username}' --profile-metadata --media-metadata --media-types none")
    except:
        st.error("Instagram limit is reached.")

    # Reading the JSON file for the user.
    js = json.load(open(f"{username}/{username}.json", encoding="utf-8"))

    df = pd.DataFrame(js["GraphImages"])
    df["likes"] = df["edge_media_preview_like"].apply(lambda x: x["count"])
    df["comments"] = df["edge_media_to_comment"].apply(lambda x: x["count"])
    df["date"] = df["taken_at_timestamp"].apply(datetime.fromtimestamp)
    df["dayofweek"] = df["date"].dt.dayofweek
    df["month"] = df["date"].dt.month
    df["week"] = df["date"].dt.isocalendar().week
    df["year"] = df["date"].dt.year
    df["ym"] = df["year"].astype(str) + df["month"].astype(str)
    df["dayofweek"] = df["dayofweek"].replace([0, 1, 2, 3, 4, 5, 6], ["Mon.", "Tue.", "Wed.", "Thu.", "Fri.", "Sat.", "Sun."])

    # Getting and writing the Profile Pic of the user.
    prof_pic = js["GraphProfileInfo"]["info"]["profile_pic_url"]
    response = requests.get(prof_pic)
    filename = "static/image.jpg"
    with open(filename, "wb") as f:
        f.write(response.content)

    # Follower Count and Engagement Rates
    followers_count = js["GraphProfileInfo"]["info"]["followers_count"]
    engagement_rate = (((df["likes"].sum() + df["comments"].sum())/len(df))/followers_count) * 100

    col1, col2 = st.beta_columns(2)
    col1.image(filename)
    col2.write(f"Full Name: {js['GraphProfileInfo']['info']['full_name']}")
    col2.write(f"Biograph: {js['GraphProfileInfo']['info']['biography']}")
    col2.write(f"Is Business Account: {js['GraphProfileInfo']['info']['is_business_account']}")
    col2.write(f"Number of Posts: {js['GraphProfileInfo']['info']['posts_count']}")
    col2.write(f"Average posts per month: {round(df.groupby('ym').size().mean(), 2)}")
    col2.write(f"Engagement Rate: {round(engagement_rate, 2)}%")

    x = df.groupby("dayofweek").size()
    dfdata = pd.DataFrame(x).rename(columns={0: "Number of Posts"})
    st.subheader("Number of Posts Per Week-Day")
    st.bar_chart(data=dfdata, use_container_width=True)

    x = df.groupby("month").size()
    dfdata = pd.DataFrame(x).rename(columns={0: "Number of Posts"})
    st.subheader("Number of Posts Per Month")
    st.bar_chart(data=dfdata, use_container_width=True)

    def get_caption(x):
        try:
            return(x["edges"][0]["node"]["text"])
        except:
            return("")

    df["caption"] = df["edge_media_to_caption"].apply(get_caption)
    df["hashtags"] = df["caption"].apply(lambda x: re.findall("(#\w+)", x))

    hashtags = df[["hashtags", "likes"]].explode("hashtags").groupby("hashtags").agg({"likes": ["count", "mean"]})
    hashtags.columns = ["count", "average_likes"]
    # hashtags = hashtags.reset_index()
    most_liked_hashtags = hashtags.query("count > 10").sort_values("average_likes", ascending=False)

    col3, col4 = st.beta_columns(2)
    col3. subheader("Most Frequent Hashtags")
    col3.table(hashtags.sort_values("count", ascending=False).head(10))

    col4.subheader("Most Liked Hashtags")
    col4.table(most_liked_hashtags.sort_values("average_likes", ascending=False).head(10))

    topurls = list(df.sort_values("likes", ascending=False)["display_url"].head())

    toplikes = list(df.sort_values("likes", ascending=False)["likes"].head(5))
    topcomments = list(df.sort_values("likes", ascending=False)["comments"].head(5))

    n = 1
    for i in topurls:
        response = requests.get(i)
        filename = f"static/{n}.jpeg"
        with open(filename, "wb") as f:
            f.write(response.content)
        n += 1

    col5, col6, col7, col8, col9 = st.beta_columns(5)
    col5.image("static/1.jpeg")
    col5.write(f"Likes: {toplikes[0]}")
    col5.write(f"Comments: {topcomments[0]}")

    col6.image("static/2.jpeg")
    col6.write(f"Likes: {toplikes[1]}")
    col6.write(f"Comments: {topcomments[1]}")

    col7.image("static/3.jpeg")
    col7.write(f"Likes: {toplikes[2]}")
    col7.write(f"Comments: {topcomments[2]}")

    col8.image("static/4.jpeg")
    col8.write(f"Likes: {toplikes[3]}")
    col8.write(f"Comments: {topcomments[3]}")

    col9.image("static/5.jpeg")
    col9.write(f"Likes: {toplikes[4]}")
    col9.write(f"Comments: {topcomments[4]}")

