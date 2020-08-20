from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.views import View
from datetime import datetime
import json, itertools, random

with open(settings.NEWS_JSON_PATH, 'r') as file:
    news_list = json.load(file)


#  returns date from date and time
def simple_date_fun(date):
    return datetime.strptime(date, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")


class Home(View):
    def get(self, request, *args, **kwargs):
        # html = 'Coming soon'
        # return HttpResponse(html)
        return redirect("/news/")


class NewsPageView(View):
    def get(self, request, link_id, *args, **kwargs):
        context = {}
        for news in news_list:
            if news['link'] == link_id:
                context = news
                break
        return render(
            request, 'news/newspage.html', context
        )
class NewsMainPage(View):
    def get(self, request, *args, **kwargs):
        news_list_current = news_list
        # handle search request
        search_str = request.GET.get('q')
        if search_str:
            news_list_current = [news for news in news_list if search_str in news['title']]

        #  order the news list
        news_list_ordered = sorted(news_list_current, key=lambda x: datetime.strptime(x['created'], "%Y-%m-%d %H:%M:%S"),
                                   reverse=True)
        #  group new with the same date together
        grouped_news = [{'date': date, 'news_group': list(news)} for date, news in
                        itertools.groupby(news_list_ordered, lambda x: simple_date_fun(x['created']))]

        context = {'grouped_news' : grouped_news}
        return render(
            request, 'news/newsmainpage.html', context
        )

class NewsCreate(View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(
            request, 'news/newscreate.html', context
        )
    def post(self, request, *args, **kwargs):

        #  get all link values
        link_list = [news['link'] for news in news_list]

        #  create new news
        new_news={}
        new_news['created'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_news['text'] = request.POST.get('text')
        new_news['title'] = request.POST.get('title')
        #  generating new link
        random.seed()
        link_id = random.randint(1, 10000)
        while link_id in link_list:
            link_id = random.randint(1, 10000)
        new_news['link'] = link_id
        ###################################

        # add news to the list and save json file
        news_list.append(new_news)
        with open(settings.NEWS_JSON_PATH, "w") as file:
            json.dump(news_list, file)



        return redirect("/news/")