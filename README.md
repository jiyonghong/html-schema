HTML Schema
-----------

`html-schema` allows HTML documents to be handled like SQLAlchemy-like Model and Column. It produces dictionary (json) for of HTML document. __Soon to be uploaded in pip.__

Requisites
* BeautifulSoup4
* html5lib

> Tested on `python3.5.1`

Examples will use this `soup`.
```python
html = """
<div>
	<h1>Hello <span>World</span></h1>
	<ul>
		<li>1</li>
		<li>2</li>
		<li>3</li>
	</ul>
	<h2>Info</h2>
	<p id="name">Name: <span>Ji</span</p>
	<p id="gender">Gender: <span>Male</span></p>
</div>
"""
soup = BeautifulSoup(html, 'html5lib')
```

Schema
======
`Schema` extracts portions of HTML document and produce dictionary from extracted data. `Schema` must have a `container` which tells to `Schema` where to extract its data from. Simplest `Schema` will looks like this.

```python
from html_schema import Schema, StrItem, IntItem

class MySchema(Schema):
    container = 'div'
    title = StrItem('h1')
    
my_schema = MySchema(soup)
my_schema.extract_all() # {'title': 'Hello'}
```
* __\__init____ (self, soup, remove_comments=True):
    + __soup__: `BeautifulSoup`, `str`, `bytes`, initiates `BeautifulSoup` if `soup` is not `BeautifulSoup` instance
    + __remove_comments__: `bool`, removes comments from `soup`
* __extract__ (self, key): returns `Item`'s data matching the name `key`
* __extract_all__ (self): returns all `Item`s data in dictionary
* __get_items__ (self): returns `Item`s in `Schema`
* __get_translate_keys__: returns list of `Item`'s keys with `translate=True` (compatible to used with dpath library)

Item
====
`Item` is a extracted data from a css selector. There are different data types for `Items` to validate and sanitize the content beforehand. You can have custom sanitizer which overrides the default sanitize method.

* __\__init____ (self, css, type_, use_parent=False, translate=False, sanitizer=None)
    + __css__: `str`, css selector for a item to extract its data from
    + __use_parent__: `bool`, used within the schema, extract data from a received soup not in a container
    + __translate__: `bool`, used within the schema, the item will be selected in `Schema.translate_keys`
    + __sanitizer__: `function`, overrides default item's sanitize method
* __sanitize__ (value, type_=None)
    + @staticmethod
    + __value__: value where extracted data will be passed into
    + __type___: `int` or `str`, type to be handle differently 
* __extract__ (self, soup)
    + __soup__: `self.css` will select from here

Different types of `Item` have different parameters. 

### StrItem
String `Item`.
* \__init__ (self, css, use_parent=False, translate=False, sanitizer=None, attr=None, recursive=False)
    + __attr__: `str`, extract data from attr
    + __recursive__: `bool`, generally Items extract from its `self.css` only, but `recursive=True` will include child elements to be extracted as well

```python
h1 = StrItem('h1')
h1.extract(soup) # Hello

h1_recursive = StrItem('h1', recursive=True)
h1_recursive.extract(soup) # Hello World
```

### IntItem
Integer `Item`.
* __\__init____ (self, css, use_parent=False, translate=False, sanitizer=None, attr=None)
    + __attr__: `str`, extract data from attr

### DictItem
Dictonary `Item`.
* __\__init____ (self, child, css=None, type_=dict, use_parent=False, translate=False)
    + __css__: css is not required for dictionary since its just an placeholder *(if you want \__repr__ method to print css, you may use this param)*
    + __child__: `Schema`, child must be subclass of `Schema`, it will return `Schema`'s extracted dictionary

```python
class InfoSchema(Schema):
    name = StrItem('#name span')
    gender = StrItem('#gender span')

dict_ = DictItem(InfoSchema)
dict_.extract(soup) # {'gender': 'Male', 'name': 'Ji'}
```

### ListItem
`Item` for list of elements.
* __\__init____ (self, css, type_=list, use_parent=False, translate=False, sanitizer=None, child=None, attrs=None)
    + you can only use one of child or attrs (if both are set child is used)
    + __child__: `Schema`, list of dictionaries of child
    + __attrs__: `dict`, list of dictionaries of attrs, `text` key is used for actual content of a element
        + key as attr and value as `int` or `str` (for sanitize purpose)

```python
list_ = ListItem('ul li')
list_.extract(soup) # ['1', '2', '3']

list_attrs = ListItem('ul li', attrs=dict(num=int))
list_attrs.extract(soup)
# [{'text': '1', 'num': 1}, {'text': '2', 'num': 2}, {'text': '3', 'num': 3}]
```


### HtmlItem
`Item` for manipulating HTML before extraction
* __\__init____ (self, css, use_parent=False, translate=False, sanitizer=None, remove_elems=None)
    + __remove_elems__: `str`, removes certain elements beforehand
* __to_string__: returns string representation of HTML
* __elem__: returns extracted HTML soup

```python
div = HtmlItem('div', remove_elems='h2, ul')
div.extract(soup)
# <div>
#    <h1>Hello <span>World</span></h1>
#
#
#    <p id="name">Name: <span>Ji
#    </span></p><p id="gender">Gender: <span>Male</span></p>
# </div>
div.to_string()
# <div> <h1>Hello <span>World</span></h1> <p id="name">Name: <span>Ji </span></p><p id="gender">Gender: <span>Male</span></p> </div>
```
