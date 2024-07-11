from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username='TestAuthor')
        cls.wrong_author = User.objects.create(username='WrongAuthor')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Да, да. Это тестовая заметка',
            author=cls.author
        )

    def test_pages_for_anonymous(self):
        """Тест доступности страниц для анонимных пользователей"""
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup'
        )
        for name in urls:
            url = reverse(name)
            response = self.client.get(url)
            with self.subTest():
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_for_notes_authors(self):
        """Тест доступности страниц для авторов заметок"""
        urls_args = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
            ('notes:list', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,))
        )
        for item in urls_args:
            self.client.force_login(self.author)
            name, args = item
            url = reverse(name, args=args)
            response = self.client.get(url)
            with self.subTest():
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_anonymous_redirects(self):
        """
        Тест редиректа анонимного пользователя на страницу входа
        при запросе страниц требующих авторизации
        """
        urls_args = (
            ('notes:list', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,))
        )
        login_url = reverse('users:login')
        for item in urls_args:
            name, args = item
            url = reverse(name, args=args)
            redirect_url = f'{login_url}?next={url}'
            with self.subTest():
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_404_for_wrong_authors(self):
        """Тест ошибки 404 для авторов при запросе чужих заметок"""
        urls_args = (
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,))
        )
        for item in urls_args:
            self.client.force_login(self.wrong_author)
            name, args = item
            url = reverse(name, args=args)
            response = self.client.get(url)
            with self.subTest():
                self.assertEqual(
                    response.status_code, HTTPStatus.NOT_FOUND
                )
