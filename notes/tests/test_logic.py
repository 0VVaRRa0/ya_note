from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify


from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class TestLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_note = Note.objects.create(
            title='Заметка автора',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.another_author = User.objects.create(username='Другой автор')
        cls.another_author_note = Note.objects.create(
            title='Заметка другого автора',
            text='Текст заметки',
            author=cls.another_author
        )
        cls.another_author_client = Client()
        cls.another_author_client.force_login(cls.another_author)
        cls.note_form_data = {
            'title': 'Название заметки из формы',
            'text': 'Текст заметки из формы',
            'slug': 'form-note-slug'
        }

    def test_author_can_create_note_anonimous_cant(self):
        url = reverse('notes:add')
        self.client.post(url, data=self.note_form_data)
        self.assertEqual(Note.objects.count(), 2)
        self.author_client.post(url, data=self.note_form_data)
        self.assertEqual(Note.objects.count(), 3)

    def test_unique_slug_for_notes(self):
        url = reverse('notes:add')
        self.note_form_data['slug'] = 'note-slug'
        response = self.author_client.post(url, data=self.note_form_data)
        self.assertFormError(
            response, 'form', 'slug', (self.author_note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 2)

    def test_autoslug_for_note(self):
        url = reverse('notes:add')
        self.note_form_data['slug'] = ''
        self.author_client.post(url, data=self.note_form_data)
        note = Note.objects.get(id=3)
        expected_slug = slugify(note.title)
        self.assertEqual(expected_slug, note.slug)

    def test_author_can_edit_delete_own_notes(self):
        edit_url = reverse('notes:edit', args=(self.author_note.slug,))
        self.author_client.post(edit_url, data=self.note_form_data)
        self.author_note.refresh_from_db()
        self.assertEquals(
            (
                self.author_note.title,
                self.author_note.text,
                self.author_note.slug
            ),
            (
                self.note_form_data['title'],
                self.note_form_data['text'],
                self.note_form_data['slug']
            )

        )
        delete_url = reverse('notes:delete', args=(self.author_note.slug,))
        self.author_client.post(delete_url)
        self.assertEqual(Note.objects.count(), 1)

    def test_not_author_cant_edit_delete_others_notes(self):
        edit_url = reverse('notes:edit', args=(self.author_note.slug,))
        self.another_author_client.post(edit_url, self.note_form_data)
        self.author_note.refresh_from_db()
        self.assertNotEquals(
            (
                self.author_note.title,
                self.author_note.text,
                self.author_note.slug
            ),
            (
                self.note_form_data['title'],
                self.note_form_data['text'],
                self.note_form_data['slug']
            )
        )
        delete_url = reverse('notes:delete', args=(self.author_note.slug,))
        self.another_author_client.post(delete_url)
        self.assertEqual(Note.objects.count(), 2)
