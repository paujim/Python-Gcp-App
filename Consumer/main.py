from flask import Flask, request, jsonify
from google.cloud import language
import base64
from google.cloud.language import enums
from google.cloud.language import types
import os
import logging
from flask_sqlalchemy import SQLAlchemy
import dateutil.parser

app = Flask(__name__)

logger = logging.getLogger()

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Tweets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255))
    keyword = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime())
    location = db.Column(db.String(255))
    sentiment_score = db.Column(db.Float())
    sentiment_magnitude = db.Column(db.Float())

    def __init__(self, text,  keyword, timestamp, location, score, magnitude):
        self.text = text
        self.keyword = keyword
        self.timestamp = timestamp
        self.location = location
        self.sentiment_score = score
        self.sentiment_magnitude = magnitude


def get_sentiment(tweet):
    client = language.LanguageServiceClient()
    document = types.Document(
        content=tweet,
        type=enums.Document.Type.PLAIN_TEXT)
    sentiment = client.analyze_sentiment(
        document=document)\
        .document_sentiment
    return sentiment


def insert_tweet(text, keyword, timestamp_in_text, location, score, magnitude):
    timestamp = None
    if timestamp_in_text is not None:
        timestamp = dateutil.parser.parse(timestamp_in_text)

    tweet = Tweets(text=text, keyword=keyword, timestamp=timestamp, location=location, score=score, magnitude=magnitude)
    db.session.add(tweet)
    db.session.commit()


def get_attribute(data, key):
    try:
        return data['message']['attributes'][key]
    except KeyError:
        return None


# {
#   "message": {
#     "attributes": {
#       "key": "value"
#     },
#     "data": "SGVsbG8gQ2xvdWQgUHViL1N1YiEgSGVyZSBpcyBteSBtZXNzYWdlIQ==",
#     "messageId": "136969346945"
#   },
#   "subscription": "projects/myproject/subscriptions/mysubscription"
# }
@app.route('/', methods=['POST'])
def process_message():
    req_data = request.get_json()
    encoded = req_data['message']['data']
    keyword = get_attribute(req_data, 'keyword')
    timestamp = get_attribute(req_data, 'timestamp')
    location = get_attribute(req_data, 'location')
    tweet = base64.b64decode(encoded)
    sentiment = get_sentiment(tweet)
    insert_tweet(tweet, keyword, timestamp, location, sentiment.score, sentiment.magnitude)
    return jsonify({'score': sentiment.score, 'magnitude': sentiment.magnitude}), 200


if __name__ == '__main__':

    app.run(host='127.0.0.1', port=8080, debug=True)
