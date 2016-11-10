# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup, Comment


class Schema(object):
    container = None

    def __init__(self, soup, remove_comments=True):
        self.soup = soup
        if isinstance(self.soup, (str, bytes)):
            self.soup = BeautifulSoup(soup, 'html5lib')

        if remove_comments:
            comments = self.soup.find_all(text=lambda text: isinstance(text, Comment))
            for comment in comments:
                comment.extract()

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.container)

    @classmethod
    def get_items(cls):
        from .item import Item

        return {key: item
                for key, item in cls.__dict__.items()
                if isinstance(item, Item)}.items()

    @classmethod
    def get_translate_keys(cls):
        keys = []
        queue = [(key, item) for key, item in cls.get_items()]

        while queue:
            key, item = queue.pop(0)

            if hasattr(item, 'child'):
                queue.extend([('/'.join([key, child_key]), child_item)
                              for child_key, child_item in item.child.get_items()])
                continue

            if item.translate:
                keys.append('/%s' % key)

        return keys

    def extract(self, key):
        item = getattr(self, key)
        return item.extract(self.soup if item.use_parent else self.soup.select_one(self.container))

    def extract_all(self):
        data = {}

        container = self.soup.select_one(self.container)
        for key, item in self.get_items():
            data[key] = item.extract(self.soup if item.use_parent else container)
            if hasattr(item, 'to_string'):
                data[key] = item.to_string()

        return data
