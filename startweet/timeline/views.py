import os
import datetime
import tweepy
import requests
import requests_oauthlib
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView


def create_client(access_token: str, access_token_secret: str):
    client = tweepy.Client(
        os.environ['BEARER_TOKEN'],
        os.environ['CONSUMER_KEY'],
        os.environ['CONSUMER_SECRET'],
        access_token,
        access_token_secret,
        return_type=requests.Response
    )

    return client


class IndexView(TemplateView):
    template_name = 'timeline/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        client = create_client(self.request.session['access_token'], self.request.session['access_token_secret'])
        tweets = []
        for home in tweepy.Paginator(
            client.get_home_timeline,
            exclude=['retweets', 'replies'],
            tweet_fields=['created_at', 'author_id', 'public_metrics'],
            expansions=['author_id', 'attachments.media_keys'],
            user_fields=['name', 'username', 'profile_image_url', 'url'],
            media_fields=['url'],
            max_results=100,
            start_time=datetime.datetime.now() - datetime.timedelta(days=1)
        ):
            try:
                home = home.json()
                for tweet in home['data']:
                    for user in home['includes']['users']:
                        if user['id'] == tweet['author_id']:
                            tweet['name'] = user['name']
                            tweet['profile_image_url'] = user['profile_image_url']
                            tweets.append(tweet)
            except Exception as e:
                print(e)
        tweets = sorted(tweets, key=lambda x: -x['public_metrics']['retweet_count'])
        context['tweets'] = tweets

        return context

    def get(self, request, *args, **kwargs):
        if not ('access_token' and 'access_token_secret') in request.session:
            return redirect('timeline:login')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        content = request.POST['content']
        create_client(request.session['access_token'],request.session['access_token_secret']).create_tweet(text=content)
        return super().get(request, *args, **kwargs)


def login(request):
    API_KEY = os.environ['CONSUMER_KEY']
    API_KEY_SECRET = os.environ['CONSUMER_SECRET']

    callback_url = "http://localhost:8000/timeline/oauth/"
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


def oauth(request, *args, **kwargs):
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
