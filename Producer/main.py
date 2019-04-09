import tweepy
import re
import os
from flask import Flask, request
from flask import jsonify
from google.cloud import pubsub
from datetime import datetime, timedelta
from nltk.tokenize import WordPunctTokenizer
from google.cloud import datastore

GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT')


def get_setting(key):
    if GOOGLE_CLOUD_PROJECT == 'NOT_SET':
        return None

    client = datastore.Client()
    entity = client.get(client.key('settings', key))
    if entity is None:
        return None
    return entity.get('value')


app = Flask(__name__)

ACCESS_TOKEN = get_setting('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = get_setting('ACCESS_TOKEN_SECRET')
CONSUMER_KEY = get_setting('CONSUMER_KEY')
CONSUMER_SECRET = get_setting('CONSUMER_SECRET')
PUB_SUB_TOPIC = get_setting('PUB_SUB_TOPIC')


def authentication(cons_key, cons_secret, acc_token, acc_secret):
    auth = tweepy.OAuthHandler(cons_key, cons_secret)
    auth.set_access_token(acc_token, acc_secret)
    api = tweepy.API(auth)
    return api


def search_tweets(keyword, total_tweets):
    today_datetime = datetime.today().utcnow()
    since_datetime = today_datetime - timedelta(seconds=60)
    since_date = since_datetime.strftime('%Y-%m-%d')
    api = authentication(
        CONSUMER_KEY,
        CONSUMER_SECRET,
        ACCESS_TOKEN,
        ACCESS_TOKEN_SECRET)
    search_result = tweepy.Cursor(api.search,
                                  q=keyword,
                                  since=since_date,
                                  result_type='recent',
                                  lang='en').items(total_tweets)
    return search_result


def clean_tweets(tweet):
    user_removed = re.sub(r'@[A-Za-z0-9]+:', '', tweet)
    link_removed = re.sub('https?://[A-Za-z0-9./]+', '', user_removed)
    # number_removed = re.sub('[^a-zA-Z]', ' ', link_removed)
    lower_case_tweet = link_removed.lower()
    tok = WordPunctTokenizer()
    words = tok.tokenize(lower_case_tweet)
    clean_tweet = (' '.join(words)).strip()
    return clean_tweet


def fetch_tweets(keyword, total_tweets):
    tweets = search_tweets(keyword, total_tweets)
    messages = []
    for tweet in tweets:
        cleaned_tweet = clean_tweets(tweet.text)
        timestamp = tweet.created_at.isoformat()
        location = tweet.user.location
        messages.append(dict(
            tweet=cleaned_tweet,
            timestamp=timestamp,
            location=location))
        print('Tweet: {}'.format(dict(
            tweet=cleaned_tweet,
            timestamp=timestamp,
            location=location)))
    return messages


def publish_tweets(keyword, messages):
    client = pubsub.PublisherClient()
    topic_path = client.topic_path(
        GOOGLE_CLOUD_PROJECT,
        PUB_SUB_TOPIC)
    for message in messages:
        data = message['tweet'].encode('utf-8')
        client.publish(topic_path,
                       data=data,
                       keyword=keyword,
                       timestamp=message['timestamp'],
                       location=message['location'])


@app.route('/')
def tweets():
    # (i.e. ?keyword=some-value)
    keyword = request.args.get('keyword')
    if keyword is None:
        keyword = "dogs"
    messages = fetch_tweets(keyword, 1)
    publish_tweets(keyword, messages)
    return jsonify(messages), 200


if __name__ == '__main__':

    app.run(host='127.0.0.1', port=8080, debug=True)
