from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Пользователь')
        cls.note_author = User.objects.create(username='Автор заметки')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.note_author
        )

    def test_pages_availability_for_user(self):
        names = (
            'notes:list',
            'notes:add',
            'notes:success'
        )
        for name in names:
            with self.subTest():
                self.client.force_login(self.user)
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_not_author(self):
        names_args = (
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:edit', (self.note.slug,))
        )
        for name, args in names_args:
            with self.subTest():
                self.client.force_login(self.user)
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_anonimous_redirects(self):
        names_args = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in names_args:
            with self.subTest():
                url = reverse(name, args=args)
                response = self.client.get(url)
                login_url = reverse('users:login')
                expected_url = f'{login_url}?next={url}'
                self.assertRedirects(response, expected_url)

    def test_pages_availability_for_anonimous_and_users(self):
        names = (
            'users:signup',
            'users:login',
            'users:logout',
            'notes:home'
        )
        for name in names:
            with self.subTest():
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.client.force_login(self.user)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
