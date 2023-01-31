import pandas as pd
import snscrape.modules.twitter as sntwitter
from pymongo import MongoClient
import json
import base64
import streamlit as st

# function.py

def scraping_tweets(hashtag,start_date,end_date,tweet_limit):
   tweet_list=[]
   for i,tweet in enumerate(sntwitter.TwitterSearchScraper(f'{hashtag} since:{start_date} until:{end_date}').get_items()):
     data=[tweet.date,
           tweet.user.username,
           tweet.user.verified,
           tweet.rawContent,
           tweet.likeCount,
           tweet.retweetCount
           ]
     tweet_list.append(data)
     if i==tweet_limit-1:
        break

   return tweet_list

def create_df(tweet_list):
    tweet_data=pd.DataFrame(tweet_list,columns=["Date", "Username", "Verified", "Raw Content", "Like Count", "Retweet Count"])
    
    return tweet_data

#GUI.py
#st.image("twitterbanner05.jpg")
st.title("Scraping The Tweets")

#Getting input from user for hashtag
hashtag= st.text_input("Enter the hashtag:")

#Getting start date from user
start_date= st.date_input("Select start date:", key="start_date")

#Getting end date from user
end_date= st.date_input("Select end date:", key="end_date")

#Getting tweet limits from user
tweet_limit= st.number_input("Enter the number of tweets you need:", key="limit")

#Scraping tweets
if st.button("Scrape Tweets"):
    tweets= scraping_tweets(hashtag,start_date,end_date,tweet_limit)
    tweet_data= create_df(tweets)
    st.dataframe(tweet_data)

#Download file as CSV
    st.write("Saving dataframe as csv")
    csv= tweet_data.to_csv(index=False)
    b64= base64.b64encode(csv.encode()).decode()
    href= f'<a href="data:file/csv;base64,{b64}" download="tweet-data.csv">Download csv File</a>'
    st.markdown(href, unsafe_allow_html=True)

#Download file as JSON
    st.write("Saving dataframe as json")
    json_string= tweet_data.to_json(indent=2)
    b64= base64.b64encode(json_string.encode()).decode()
    href= f'<a href="data:file/json;base64,{b64}" download="tweet-data.json">Download json File</a>'
    st.markdown(href, unsafe_allow_html=True)

# Upload to mongoDB
if st.button("upload to MongoDB"):
  tweets = scraping_tweets(hashtag,start_date,end_date,tweet_limit)
  tweet_data = create_df(tweets)

  client =MongoClient('mongodb://localhost:27017')
  db = client["twitter_db_streamlit"]
  collection = db['tweets']
  tweet_data_json= json.loads(tweet_data.to_json(orient='records'))
  collection.insert_many(tweet_data_json)
  st.success('uploaded to MongoDB')

  #run streamlit by
  # python -m streamlit run twitter.py