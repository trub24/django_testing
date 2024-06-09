from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestContetn(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(title='Заголовок',
                                       text='Текст', author=cls.author,)

    def test_authorized_client_can_add_note(self):
        urls = [
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        ]
        for name, args in urls:
            self.client.force_login(self.author)
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)

    def test_client_has_list_note(self):
        user_bool = (
            (self.author, True),
            (self.reader, False)
        )
        for user, bool in user_bool:
            self.client.force_login(user)
            with self.subTest(user=user):
                response = self.client.get(reverse('notes:list', None))
                object_list = response.context['object_list']
                bool_note = (self.note in object_list)
                self.assertEqual(bool_note, bool)
