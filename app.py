import nltk
nltk.download('vader_lexicon')
import googleapiclient.discovery
from googleapiclient.errors import HttpError
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from flask import Flask, request, render_template, jsonify


app = Flask(__name__)


# YouTube API setup
api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = "AIzaSyCATHJTrmSzDFAXM2_-z6C8Ue7hGSyg4_E"


youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey=DEVELOPER_KEY)


# Initialize the sentiment analyzer
sid = SentimentIntensityAnalyzer()


# Define the get_video_comments function
def get_video_comments(youtube, **kwargs):
    comments = []
    try:
        results = youtube.commentThreads().list(**kwargs).execute()


        while results:
            for item in results["items"]:
                comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                comments.append(comment)


            # Retrieve the next page of comments
            if "nextPageToken" in results:
                kwargs["pageToken"] = results["nextPageToken"]
                results = youtube.commentThreads().list(**kwargs).execute()
            else:
                break
    except HttpError as e:
        print(f"An error occurred: {e}")


    return comments


# Define the main route for rendering the HTML form
@app.route('/')
def index():
    return render_template('index.html')


# Define the route for analyzing comments
@app.route('/analyze_comments', methods=['POST'])
def analyze_comments():
    video_id = request.form.get('video_id')
    max_comments = int(request.form.get('max_comments'))
    comment_count = 0
    results = []


    while comment_count < max_comments:
        comments = get_video_comments(youtube, part="snippet", videoId=video_id, textFormat="plainText", maxResults=100)


        for comment in comments:
            # Perform sentiment analysis here
            sentiment_scores = sid.polarity_scores(comment)
           
            if sentiment_scores['compound'] >= 0.05:
                sentiment = 'Positive'
            elif sentiment_scores['compound'] <= -0.05:
                sentiment = 'Negative'
            else:
                sentiment = 'Neutral'


            result = {
                "comment": comment,
                "sentiment": sentiment
            }
            results.append(result)


            comment_count += 1


        if comment_count >= max_comments:
            break


        time.sleep(30)


    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
