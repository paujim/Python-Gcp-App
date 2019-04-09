from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from google.cloud import datastore
import os


def gen_connection_string():
    if not os.environ.get('GAE_INSTANCE'):
        return 'mysql+pymysql://user:password@127.0.0.1:3306/tweet'
    else:
        client = datastore.Client()
        entity = client.get(client.key('settings', 'SQLALCHEMY_DATABASE_URI'))
        if entity is None:
            return None
        return entity.get('value')


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = gen_connection_string()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Tweet(db.Model):
    __tablename__ = 'tweets'
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


class TweetSerializer(Schema):
    id = fields.Integer()
    text = fields.Str()
    keyword = fields.Str()
    location = fields.Str()
    timestamp = fields.DateTime()
    score = fields.Float(attribute="sentiment_score")
    magnitude = fields.Float(attribute="sentiment_magnitude")


def fetch_data():
    tweets = Tweet.query.group_by(Tweet.timestamp, Tweet.text).order_by(Tweet.timestamp.desc()).limit(5).all()
    schema = TweetSerializer(many=True, only=('text', 'keyword', 'location', 'timestamp', 'score', 'magnitude'))
    return schema.dump(tweets).data


def classify_sentiment(tweets):
    if tweets is None:
        return "Not Available"
    score = sum(item['score'] for (item) in tweets) / len(tweets)
    if score >= 0.25:
        return "Clearly Positive"
    if score >= 0.10:
        return "Positive"
    if score < 0.10 and score > -0.10:
        return "Neutral"
    if score <= -0.25:
        return "Clearly Negative"
    if score <= -0.10:
        return "Negative"


@app.route("/")
def chart():
    tweets = fetch_data()
    return render_template('chart.html', tweets=tweets, keyword="dogs", sentiment=classify_sentiment(tweets))


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)
