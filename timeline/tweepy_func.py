import os
import datetime
import tweepy
import requests
import requests_oauthlib
from django.shortcuts import redirect


def login(request):
    API_KEY = os.environ['CONSUMER_KEY']
    API_KEY_SECRET = os.environ['CONSUMER_SECRET']

    callback_url = "http://localhost:8000/timeline/oauth/"
    # callback_url = "https://mi0256.pythonanywhere.com/timeline/oauth/"
    request_endpoint_url = "https://api.twitter.com/oauth/request_token"
    authenticate_url = "https://api.twitter.com/oauth/authenticate"

    session_req = requests_oauthlib.OAuth1Session(API_KEY, API_KEY_SECRET)
    response_req = session_req.post(request_endpoint_url, params={"oauth_callback": callback_url})
    response_req_text = response_req.text

    oauth_token_kvstr = response_req_text.split("&")
    token_dict = {x.split("=")[0]: x.split("=")[1] for x in oauth_token_kvstr}
    oauth_token = token_dict["oauth_token"]

    response = redirect(f'{authenticate_url}?oauth_token={oauth_token}')
    return response


def oauth(request):
    oauth_token = request.GET.get('oauth_token')
    oauth_verifier = request.GET.get('oauth_verifier')

    access_endpoint_url = "https://api.twitter.com/oauth/access_token"

    API_KEY = os.environ['CONSUMER_KEY']
    API_KEY_SECRET = os.environ['CONSUMER_SECRET']

    session_acc = requests_oauthlib.OAuth1Session(API_KEY, API_KEY_SECRET, oauth_token, oauth_verifier)
    response_acc = session_acc.post(access_endpoint_url, params={"oauth_verifier": oauth_verifier})
    response_acc_text = response_acc.text

    access_token_kvstr = response_acc_text.split("&")
    acc_token_dict = {x.split("=")[0]: x.split("=")[1] for x in access_token_kvstr}
    access_token = acc_token_dict["oauth_token"]
    access_token_secret = acc_token_dict["oauth_token_secret"]

    request.session['access_token'] = access_token
    request.session['access_token_secret'] = access_token_secret

    return redirect('timeline:index')


def page_home(client: tweepy.Client, days: int):
    tweets = []
    for response in tweepy.Paginator(
        client.get_home_timeline,
        exclude=['retweets', 'replies'],
        tweet_fields=['created_at', 'author_id', 'public_metrics'],
        expansions=['author_id', 'attachments.media_keys'],
        user_fields=['name', 'profile_image_url'],
        media_fields=['url'],
        max_results=100,
        start_time=datetime.datetime.now() - datetime.timedelta(days=days)
    ):
        format_append_tweets(tweets, response)
    return tweets


def page_user(client: tweepy.Client, id: int, days: int):
    tweets = []
    for response in tweepy.Paginator(
        client.get_users_tweets,
        id=id,
        exclude=['retweets', 'replies'],
        tweet_fields=['created_at', 'author_id', 'public_metrics'],
        expansions=['author_id', 'attachments.media_keys'],
        user_fields=['name', 'profile_image_url'],
        media_fields=['url'],
        max_results=100,
        start_time=datetime.datetime.now() - datetime.timedelta(days=days)
    ):
        format_append_tweets(tweets, response)
    return tweets


def page_list(client: tweepy.Client, id: int, days: int):
    tweets = []
    for response in tweepy.Paginator(
        client.get_list_tweets,
        id=id,
        tweet_fields=['created_at', 'author_id', 'public_metrics'],
        expansions=['author_id', 'attachments.media_keys'],
        user_fields=['name', 'profile_image_url'],
        media_fields=['url'],
        max_results=100
    ):
        format_append_tweets(tweets, response)
    return tweets


def like_user_tweets(client: tweepy.Client, id: int, limit: int):
    tweets = client.get_users_tweets(
        id=id,
        exclude=['retweets', 'replies'],
        max_results=limit
    )
    try:
        for tweet in tweets.json()['data']:
            client.like(tweet['id'])
    except KeyError:
        pass


def rt_user_tweets(client: tweepy.Client, id: int, limit: int):
    tweets = client.get_users_tweets(
        id=id,
        exclude=['retweets', 'replies'],
        max_results=limit
    )
    try:
        for tweet in tweets.json()['data']:
            client.retweet(tweet['id'])
    except KeyError:
        pass


def like_home(client: tweepy.Client, limit: int):
    tweets = client.get_home_timeline(
        exclude=['retweets', 'replies'],
        max_results=limit
    )
    try:
        for tweet in tweets.json()['data']:
            try:
                client.like(tweet['id'])
            except tweepy.errors.BadRequest:
                pass
    except KeyError:
        pass


def create_client(access_token: str, access_token_secret: str):
    return tweepy.Client(
        os.environ['BEARER_TOKEN'],
        os.environ['CONSUMER_KEY'],
        os.environ['CONSUMER_SECRET'],
        access_token,
        access_token_secret,
        return_type=requests.Response,
        wait_on_rate_limit=True
    )


def username_to_id(client: tweepy.Client, username: str):
    response = client.get_user(username=username)
    return response.json()['data']['id']


def get_pinned_lists(client: tweepy.Client):
    try:
        return client.get_pinned_lists().json()['data']
    except Exception:
        return []


def format_tweet_data(tweet_data: str):
    iso_data = datetime.datetime.fromisoformat(tweet_data.split('.')[0])
    utc_data = iso_data.replace(tzinfo=datetime.timezone.utc)
    jst_data = utc_data.astimezone(datetime.timezone(datetime.timedelta(hours=9)))
    return jst_data.strftime('%Y-%m-%d %H:%M:%S')


def format_append_tweets(tweets: list, response: requests.Response):
    response = response.json()
    if 'data' in response:
        for tweet in response['data']:
            public_metrics = tweet['public_metrics']
            public_metrics['reaction_count'] = public_metrics['retweet_count'] + public_metrics['like_count'] + public_metrics['quote_count'] + public_metrics['reply_count']
            tweet['public_metrics']['virtual_engagement'] = round(public_metrics['reaction_count'] / (public_metrics['impression_count'] + 1) * 100, 2)
            tweet['created_at'] = format_tweet_data(tweet['created_at'])
            if 'attachments' in tweet:
                append_media_tweet(tweet, response['includes']['media'])
            append_profile_tweet(tweet, response['includes']['users'])
            tweets.append(tweet)


def append_media_tweet(tweet: dict, media_dict: dict):
    tweet['media_url'] = []
    for media_key in tweet['attachments']['media_keys']:
        for media in media_dict:
            if media_key == media['media_key'] and 'url' in media:
                tweet['media_url'].append(media['url'])


def append_profile_tweet(tweet: dict, users: dict):
    for user in users:
        if user['id'] == tweet['author_id']:
            tweet['name'] = user['name']
            tweet['profile_image_url'] = user['profile_image_url']
