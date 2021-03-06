from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=50, unique=True)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('category-page', [str(self.slug)])

class Entry(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=50, unique=True)
    category = models.ManyToManyField(Category)
    date = models.DateTimeField()
    entry = models.TextField()
    thumbnail_entry = models.TextField()
    keywords = models.CharField(max_length=300, blank=True, null=True)
    description = models.CharField(max_length=300, blank=True, null=True)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return "/blog/%s/" % self.slug

    class Meta:
        ordering = ['-date']
