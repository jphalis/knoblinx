from django.db import models
from django.test import TestCase

from .models import TagMixin

# Create your tests here.


class TestModel(TagMixin):
    """
    This model is purely for unit testing.
    """
    tags = models.CharField(max_length=255)
    tag_text_field = 'tags'


class TagMixinUnitTest(TestCase):
    def test_tags_parsed(self):
        c = TestModel(tags='some cool text')
        tags = c._get_tags()
        expected_tags = ['cool', 'text']
        self.assertEqual(
            tags, expected_tags, 'tags did not equal '
            'expected_tags. Instead was: {}'.format(tags)
        )

    # def test_tags_persisted(self):
    #     c = TestModel.objects.create(title='foo',
    #                                  description='some cool text')
    #     self.assertIsNot(
    #         c.hashtags.all(), None,
    #         'hashtags were not saved to the database.'
    #     )
