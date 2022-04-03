import requests
import datetime
import random


def news_looker(company, api_k):
    date = datetime.datetime.today().__str__().split(" ")[0]
    url = 'https://newsapi.org/v2/everything'
    params = {
        'q': company,
        "from": date,
        "sortBy": "popularity",
        "apiKey": api_k
    }
    request = requests.get(url, params=params)
    request.raise_for_status()

    news_data = request.json()['articles']
    ready_news = {}
    try:
        chosen_news = [news_data[i] for i in range(0, 3)]
        for news in chosen_news:
            news_source = news['source']['name']
            author = news['author']
            title = news['title']
            news_url = news['url']
            ready_news[news_source] = {'author': author, 'title': title, 'url': news_url}
    except IndexError:
        ready_news["No news"] = f"No news available for {company}"

    return ready_news

