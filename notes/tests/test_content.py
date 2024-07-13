from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Пользователь')
        cls.note_author = User.objects.create(username='Автор заметки')
        cls.note = Note.objects.create(
            title='Название заметки',
            text='Текст заметки',
            slug='note-slug',
            author=cls.note_author
        )
        cls.user_note = Note.objects.create(
            title='Название заметки',
            text='Текст заметки',
            slug='user-note-slug',
            author=cls.user
        )

    def test_note_in_context(self):
        url = reverse('notes:list')
        self.client.force_login(self.note_author)
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_wrong_note_in_context(self):
        url = reverse('notes:list')
        self.client.force_login(self.note_author)
        resposne = self.client.get(url)
        object_list = resposne.context['object_list']
        self.assertNotIn(self.user_note, object_list)

    def test_form_in_add_edit(self):
        names_args = (('notes:add', None), ('notes:edit', (self.note.slug,)))
        for name, args in names_args:
            with self.subTest():
                self.client.force_login(self.note_author)
                url = reverse(name, args=args)
                response = self.client.get(url)
                context = response.context
                self.assertIn('form', context)
                self.assertIsInstance(context['form'], NoteForm)
