from django.contrib.syndication.views import Feed
from blog.models import Entry

class RssSiteNewsFeed(Feed):
    title = "my-SPY Blog"
    link = "/blog/rss/"

    def items(self):
        return Entry.objects.order_by('-date')[:5]
