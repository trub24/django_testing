import pytest
from django.urls import reverse
from django.conf import settings
from news.forms import CommentForm


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name', ('news:home',)
)
def test_news_count(name, all_news, client):
    all_news = all_news
    url = reverse(name)
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name', ('news:home',)
)
def test_news_order(name, all_news, client):
    all_news = all_news
    url = reverse(name)
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name', ('news:detail',),
)
def test_comments_order(comments, name, client, news):
    comments = comments
    url = reverse(name, args=(news.id,))
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name', ('news:detail',),
)
@pytest.mark.parametrize(
    'parametrized_client, comment_form_in',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
def test_client_has_difrent_form(name, parametrized_client,
                                 comment_form_in, news):
    url = reverse(name, args=(news.id,))
    response = parametrized_client.get(url)
    assert ('form' in response.context) is comment_form_in
    if comment_form_in is True:
        assert isinstance(response.context['form'], CommentForm)
