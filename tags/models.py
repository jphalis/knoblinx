from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.db import models

# Create your models here.


class Tag(models.Model):
    tag = models.SlugField(max_length=250, unique=True)

    class Meta:
        app_label = 'tags'

    def __unicode__(self):
        return str(self.tag)

    def get_absolute_url(self):
        return reverse('tags:detail', kwargs={'tag': str(self.tag)})


class TagMixin(models.Model):
    tags = models.ManyToManyField(Tag, blank=True)
    tag_text_field = None

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(TagMixin, self).__init__(*args, **kwargs)
        # some defensive coding to ensure the field defined is a
        # CharField or TextField, especially when open sourcing
        if not self.tag_text_field:
            raise NotImplemented(
                u'You must define a source for the tags '
                u'to derive from, which needs to be a CharField or TextField.')

        self.tag_text_field = self._meta.get_field(self.tag_text_field)

        if not isinstance(self.tag_text_field,
                          (models.CharField, models.TextField,)):
            raise Exception(u'"tag_text_field" must be of type: '
                            u'models.CharField or TextField.')

    def _get_tags(self):
        # split the string if the word starts with '#'
        # return [str(word[1:]) for word in self.tag_text_field.value_to_string(
        #     self).split() if word.startswith('#')]
        return [str(word[1:]) for word in self.tag_text_field.value_to_string(
            self).split()]

    def _delete_tags(self):
        # remove any previously set tags for the instance
        self.tags.clear()
        self.tags.all().delete()

    def _set_tags(self):
        self._delete_tags()
        # add any tags derived from the tag_text_field
        # makes all tags lowercase
        tags = []
        for tag in self._get_tags():
            tag, created = Tag.objects.get_or_create(
                tag=tag, defaults={'tag': tag})
            tags.append(tag)

        self.tags.add(*tags)

    def save(self, *args, **kwargs):
        super(TagMixin, self).save(*args, **kwargs)
        self._set_tags()
