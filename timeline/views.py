from .tweepy_func import create_client, like_user_tweets, rt_user_tweets, get_pinned_lists, page_home, page_user, page_list, like_home

from django.shortcuts import redirect
from django.views.generic import TemplateView


class TimelineViewBase(TemplateView):
    template_name = 'timeline/index.html'

    def get(self, request, *args, **kwargs):
        if not ('access_token' and 'access_token_secret') in request.session:
            return redirect('timeline:login')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        client = create_client(self.request.session['access_token'], self.request.session['access_token_secret'])
        if 'search_username' in request.POST:
            search_username = request.POST['search_username']
            id = client.get_user(username=str(search_username)).json()['data']['id']
            return redirect('timeline:user', id)
        elif 'like_username' in request.POST:
            like_username = request.POST['like_username']
            id = client.get_user(username=str(like_username)).json()['data']['id']
            like_user_tweets(client, id, 20)
            return redirect('timeline:user', id)
        elif 'rt_username' in request.POST:
            rt_username = request.POST['rt_username']
            id = client.get_user(username=str(rt_username)).json()['data']['id']
            rt_user_tweets(client, id, 10)
            return redirect('timeline:user', id)
        elif 'like_home_limit' in request.POST:
            like_home(client, request.POST['like_home_limit'])
            return redirect('timeline:index')


class IndexView(TimelineViewBase):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        client = create_client(self.request.session['access_token'], self.request.session['access_token_secret'])
        context['lists'] = get_pinned_lists(client)
        context['me'] = client.get_me().json()['data']['id']

        tweets = page_home(client, days=3)
        context['tweets'] = sorted(tweets, key=lambda x: -(x['public_metrics']['retweet_count'] * 2 + x['public_metrics']['like_count']))

        return context


class UserView(TimelineViewBase):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        client = create_client(self.request.session['access_token'], self.request.session['access_token_secret'])
        context['lists'] = get_pinned_lists(client)
        context['me'] = client.get_me().json()['data']['id']

        id = self.kwargs.get('id', '')
        tweets = page_user(client, id, days=7)
        context['tweets'] = sorted(tweets, key=lambda x: -(x['public_metrics']['retweet_count'] * 2 + x['public_metrics']['like_count']))

        return context


class ListView(TimelineViewBase):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        client = create_client(self.request.session['access_token'], self.request.session['access_token_secret'])
        context['lists'] = get_pinned_lists(client)
        context['me'] = client.get_me().json()['data']['id']

        id = self.kwargs.get('id', '')
        tweets = page_list(client, id, days=7)
        context['tweets'] = sorted(tweets, key=lambda x: -(x['public_metrics']['retweet_count'] * 2 + x['public_metrics']['like_count']))

        return context
