# -*- coding: utf-8 -*-
import re


class Item(object):
    def __init__(self, css, type_, use_parent=False, translate=False, sanitizer=None):
        self.css = css
        self.type = type_
        self.use_parent = use_parent
        self.translate = translate
        self.sanitize = self.sanitize if sanitizer is None else sanitizer

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.css)

    @staticmethod
    def sanitize(value, type_=None):
        raise NotImplementedError

    def extract(self, soup):
        raise NotImplementedError


class StrItem(Item):
    def __init__(self, css, use_parent=False, translate=False, sanitizer=None, attr=None,
                 recursive=False):
        super().__init__(css, str, use_parent, translate, sanitizer)
        self.attr = attr
        self.recursive = recursive

    @staticmethod
    def sanitize(value, type_=None):
        if value is None:
            return value

        return value.strip() if re.search('\w+', value) else None

    def extract(self, soup):
        if not self.css:
            return self.sanitize(soup.get(self.attr) if self.attr else soup.get_text())

        elem = soup.select_one(self.css)
        if not elem:
            return None

        if self.recursive:
            return self.sanitize(elem.get(self.attr) if self.attr else elem.get_text())
        else:
            return self.sanitize(elem.get(self.attr) if self.attr
                                 else self.get_text_not_recursive(elem))

    @staticmethod
    def get_text_not_recursive(elem):
        return ''.join(elem.find_all(text=True, recursive=False)).strip()


class IntItem(Item):
    def __init__(self, css, use_parent=False, translate=False, sanitizer=None, attr=None):
        super().__init__(css, int, use_parent, translate, sanitizer)
        self.attr = attr

    @staticmethod
    def sanitize(value, type_=None):
        if value is None:
            return value

        search = re.search(u'[\d,]+', value)
        return int(search.group().replace(',', '')) if search else 0

    def extract(self, soup):
        if not self.css:
            return self.sanitize(soup.get(self.attr) if self.attr else soup.get_text())

        elem = soup.select_one(self.css)
        if not elem:
            return None

        return self.sanitize(elem.get(self.attr) if self.attr else elem.get_text())


class DictItem(Item):
    # don't need css for DictItem (just a placeholder)
    def __init__(self, child, css=None, type_=dict, use_parent=False, translate=False):
        super().__init__(css, type_, use_parent, translate)

        from . import Schema

        if child and not issubclass(child, Schema):
            raise AttributeError('Child parameter must be inheritance of Schema.')
        self.child = child

    @staticmethod
    def sanitize(value, type_=None):
        pass

    def extract(self, soup):
        data = {}

        for child_key, child_item in self.child.get_items():
            value = child_item.extract(soup)
            if not value:
                continue

            if isinstance(child_item, DictItem):
                data.update(value)
            else:
                data[child_key] = value

        return data


class ListItem(Item):
    def __init__(self, css, type_=list, use_parent=False, translate=False, sanitizer=None,
                 child=None, attrs=None):
        super().__init__(css, type_, use_parent, translate, sanitizer)
        self.child = child
        self.attrs = attrs if attrs else {}

    @staticmethod
    def sanitize(value, type_=None):
        if type_ == int:
            return IntItem.sanitize(value)
        elif type_ == str:
            return StrItem.sanitize(value)
        else:
            return value

    @staticmethod
    def is_values_full(values):
        for value in values:
            if value in [None, [], {}]:
                return False

        return True

    def extract(self, soup):
        data = []

        elems = soup.select(self.css)
        if not elems:
            return data

        for elem in elems:
            if self.child or self.attrs:
                child_data = {}
                
                if self.child:
                    for child_key, child_item in self.child.get_items():
                        value = child_item.extract(elem)
                        if isinstance(child_item, DictItem):
                            child_data[child_key].update(value)
                        else:
                            child_data[child_key] = value
                elif self.attrs:
                    for attr, type_ in self.attrs.items():
                        if elem.get(attr):
                            child_data[attr] = self.sanitize(elem.get(attr), type_)

                    if child_data:
                        child_data['text'] = elem.get_text()

                if child_data and self.is_values_full(child_data.values()):
                    data.append(child_data)
            else:
                data.append(self.sanitize(elem.get_text()))

        return data


class HtmlItem(Item):
    def __init__(self, css, use_parent=False, translate=False, sanitizer=None, remove_elems=None):
        super().__init__(css, 'html', use_parent, translate, sanitizer)
        self.remove_elems = remove_elems
        self.elem = None

    @staticmethod
    def sanitize(value, type_=None):
        return value

    def extract(self, soup):
        if not self.css:
            return self.sanitize(soup)

        self.elem = soup.select_one(self.css)
        if not self.elem:
            return None

        if self.remove_elems:
            for remove_elem in self.elem.select(self.remove_elems):
                remove_elem.extract()

        return self.elem

    def to_string(self):
        if not self.elem:
            raise NotImplementedError('Element not extracted yet')

        return re.sub('\s+', ' ', str(self.elem))
