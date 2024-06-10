from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse
from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.exists() is False


@pytest.mark.django_db
def test_user_can_create_comment(news, author, form_data, author_client):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(news, form_data, author_client):
    url = reverse('news:detail', args=(news.id,))
    form_data['text'] = BAD_WORDS[0]
    response = author_client.post(url, data=form_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.exists() is False


def test_author_can_delete_comment(comment, news, author_client):
    url = reverse('news:delete', args=(comment.id,))
    reirect_url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url)
    assertRedirects(response, f'{reirect_url}#comments')
    assert Comment.objects.exists() is False


def test_user_cant_delete_comment_of_another_user(comment, not_author_client):
    url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(comment, news, author_client, form_data):
    url = reverse('news:edit', args=(comment.id,))
    reirect_url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, form_data)
    assertRedirects(response, f'{reirect_url}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(comment,
                                                form_data,
                                                not_author_client):
    url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    coment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == coment_from_db.text
