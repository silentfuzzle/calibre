#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
from future_builtins import map

__license__   = 'GPL v3'
__copyright__ = '2010, Kovid Goyal <kovid@kovidgoyal.net>'
__docformat__ = 'restructuredtext en'

import json
from functools import wraps
from binascii import hexlify, unhexlify

import cherrypy

from calibre.utils.date import isoformat
from calibre.utils.config import prefs
from calibre.ebooks.metadata.book.json_codec import JsonCodec
from calibre.utils.icu import sort_key
from calibre.library.server import custom_fields_to_display
from calibre import force_unicode
from calibre.library.field_metadata import category_icon_map

class Endpoint(object): # {{{
    'Manage mime-type json serialization, etc.'

    def __init__(self, mimetype='application/json; charset=utf-8',
            set_last_modified=True):
        self.mimetype = mimetype
        self.set_last_modified = set_last_modified

    def __call__(eself, func):

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Remove AJAX caching disabling jquery workaround arg
            # This arg is put into AJAX queries by jQuery to prevent
            # caching in the browser. We dont want it passed to the wrapped
            # function
            kwargs.pop('_', None)

            ans = func(self, *args, **kwargs)
            cherrypy.response.headers['Content-Type'] = eself.mimetype
            if eself.set_last_modified:
                updated = self.db.last_modified()
                cherrypy.response.headers['Last-Modified'] = \
                    self.last_modified(max(updated, self.build_time))
            if 'application/json' in eself.mimetype:
                ans = json.dumps(ans, indent=2,
                        ensure_ascii=False).encode('utf-8')
            return ans

        return wrapper
# }}}

def category_icon(category, meta): # {{{
    if category in category_icon_map:
        icon = category_icon_map[category]
    elif meta['is_custom']:
        icon = category_icon_map['custom:']
    elif meta['kind'] == 'user':
        icon = category_icon_map['user:']
    else:
        icon = 'blank.png'
    return icon
# }}}

def encode_name(name):
    if isinstance(name, unicode):
        name = name.encode('utf-8')
    return hexlify(name)

def decode_name(name):
    return unhexlify(name).decode('utf-8')

def absurl(prefix, url):
    return prefix + url

def category_url(prefix, cid):
    return absurl(prefix, '/ajax/category/'+encode_name(cid))

def icon_url(prefix, name):
    return absurl(prefix, '/browse/icon/'+name)

class AjaxServer(object):

    def __init__(self):
        self.ajax_json_codec = JsonCodec()

    def add_routes(self, connect):
        base_href = '/ajax'

        # Metadata for a particular book
        connect('ajax_book', base_href+'/book/{book_id}', self.ajax_book)

        # The list of top level categories
        connect('ajax_categories', base_href+'/categories',
                self.ajax_categories)

        # The list of sub-categories and items in each category
        connect('ajax_category', base_href+'/category/{name}',
                self.ajax_category)

        # List of books in specified category
        connect('ajax_books_in', base_href+'/books_in/{category}/{item}',
                self.ajax_books_in)


    # Get book metadata {{{
    @Endpoint()
    def ajax_book(self, book_id):
        '''
        Return the metadata of the book as a JSON dictionary.
        '''
        cherrypy.response.headers['Content-Type'] = \
                'application/json; charset=utf-8'
        try:
            book_id = int(book_id)
            mi = self.db.get_metadata(book_id, index_is_id=True)
        except:
            raise cherrypy.HTTPError(404, 'No book with id: %r'%book_id)
        try:
            mi.rating = mi.rating/2.
        except:
            mi.rating = 0.0
        cherrypy.response.timeout = 3600
        cherrypy.response.headers['Last-Modified'] = \
                self.last_modified(mi.last_modified)

        data = self.ajax_json_codec.encode_book_metadata(mi)
        for x in ('publication_type', 'size', 'db_id', 'lpath', 'mime',
                'rights', 'book_producer'):
            data.pop(x, None)

        data['cover'] = absurl(self.opts.url_prefix, u'/get/cover/%d'%book_id)
        data['thumbnail'] = absurl(self.opts.url_prefix, u'/get/thumb/%d'%book_id)
        mi.format_metadata = {k.lower():dict(v) for k, v in
                mi.format_metadata.iteritems()}
        for v in mi.format_metadata.itervalues():
            mtime = v.get('mtime', None)
            if mtime is not None:
                v['mtime'] = isoformat(mtime, as_utc=True)
        data['format_metadata'] = mi.format_metadata
        fmts = set(x.lower() for x in mi.format_metadata.iterkeys())
        pf = prefs['output_format'].lower()
        other_fmts = list(fmts)
        try:
            fmt = pf if pf in fmts else other_fmts[0]
        except:
            fmt = None
        if fmts and fmt:
            other_fmts = [x for x in fmts if x != fmt]
        data['formats'] = sorted(fmts)
        if fmt:
            data['main_format'] = {fmt: absurl(self.opts.url_prefix, u'/get/%s/%d'%(fmt, book_id))}
        else:
            data['main_format'] = None
        data['other_formats'] = {fmt: absurl(self.opts.url_prefix, u'/get/%s/%d'%(fmt, book_id)) for fmt
                in other_fmts}

        return data
    # }}}

    # Top level categories {{{
    @Endpoint()
    def ajax_categories(self):
        '''
        Return the list of top-level categories as a list of dictionaries. Each
        dictionary is of the form::
            {
            'name': Display Name,
            'url':URL that gives the JSON object corresponding to all entries in this category,
            'icon': URL to icon of this category,
            'is_category': False for the All Books and Newest categories, True for everything else
            }

        '''
        ans = {}
        categories = self.categories_cache()
        category_meta = self.db.field_metadata

        def getter(x):
            return category_meta[x]['name']

        displayed_custom_fields = custom_fields_to_display(self.db)


        for category in sorted(categories, key=lambda x: sort_key(getter(x))):
            if len(categories[category]) == 0:
                continue
            if category in ('formats', 'identifiers'):
                continue
            meta = category_meta.get(category, None)
            if meta is None:
                continue
            if meta['is_custom'] and category not in displayed_custom_fields:
                continue
            display_name = meta['name']
            if category.startswith('@'):
                category = category.partition('.')[0]
                display_name = category[1:]
            url = force_unicode(category)
            icon = category_icon(category, meta)
            ans[url] = (display_name, icon)

        ans = [{'url':k, 'name':v[0], 'icon':v[1], 'is_category':True}
                for k, v in ans.iteritems()]
        ans.sort(key=lambda x: sort_key(x['name']))
        for name, url, icon in  [
                (_('All books'), 'allbooks', 'book.png'),
                (_('Newest'), 'newest', 'forward.png'),
                ]:
            ans.insert(0, {'name':name, 'url':url, 'icon':icon,
                'is_category':False})

        for c in ans:
            c['url'] = category_url(self.opts.url_prefix, c['url'])
            c['icon'] = icon_url(self.opts.url_prefix, c['icon'])

        return ans
    # }}}

    # Items in the specified category {{{
    @Endpoint()
    def ajax_category(self, name, sort='title', num=100, offset=0,
            sort_order='asc'):
        '''
        Return a dictionary describing the category specified by name. The
        dictionary looks like::

            {
                'category_name': Category display name,
                'base_url': Base URL for this category,
                'total_num': Total numberof items in this category,
                'offset': The offset for the items returned in this result,
                'num': The number of items returned in this result,
                'sort': How the returned items are sorted,
                'sort_order': asc or desc
                'subcategories': List of sub categories of this category.
                'items': List of items in this category,
            }

        Each subcategory is a dictionary of the same form as those returned by
        ajax_categories().

        Each  item is a dictionary of the form::

            {
                'name': Display name,
                'average_rating': Average rating for books in this item,
                'count': Number of books in this item,
                'url': URL to get list of books in this item,
                'has_children': If True this item contains sub categories, look
                for an entry corresponding to this item in subcategories int he
                main dictionary,
            }

        :param sort: How to sort the returned items. CHoices are: name, rating,
                     popularity
        :param sort_order: asc or desc

        To learn how to create subcategories see
        http://manual.calibre-ebook.com/sub_groups.html
        '''
        try:
            num = int(num)
        except:
            raise cherrypy.HTTPError(404, "Invalid num: %r"%num)
        try:
            offset = int(offset)
        except:
            raise cherrypy.HTTPError(404, "Invalid offset: %r"%offset)

        base_url = absurl(self.opts.url_prefix, '/ajax/category/'+name)

        if sort not in ('rating', 'name', 'popularity'):
            sort = 'name'

        if sort_order not in ('asc', 'desc'):
            sort_order = 'asc'

        try:
            dname = decode_name(name)
        except:
            raise cherrypy.HTTPError(404, 'Invalid encoding of category name'
                    ' %r'%name)

        if dname in ('newest', 'allbooks'):
            if dname == 'newest':
                sort, sort_order = 'timestamp', 'desc'
            raise cherrypy.InternalRedirect(
                '/ajax/books_in/%s/%s?sort=%s&sort_order=%s'%(
                    encode_name(dname), encode_name('0'), sort, sort_order))

        fm = self.db.field_metadata
        categories = self.categories_cache()
        hierarchical_categories = self.db.prefs['categories_using_hierarchy']

        subcategory = dname
        toplevel = subcategory.partition('.')[0]
        if toplevel == subcategory:
            subcategory = None
        if toplevel not in categories or toplevel not in fm:
            raise cherrypy.HTTPError(404, 'Category %r not found'%toplevel)

        # Find items and sub categories
        subcategories = []
        meta = fm[toplevel]
        item_names = {}
        children = set()

        if meta['kind'] == 'user':
            fullname = ((toplevel + '.' + subcategory) if subcategory is not
                                None else toplevel)
            try:
                # User categories cannot be applied to books, so this is the
                # complete set of items, no need to consider sub categories
                items = categories[fullname]
            except:
                raise cherrypy.HTTPError(404,
                        'User category %r not found'%fullname)

            parts = fullname.split('.')
            for candidate in categories:
                cparts = candidate.split('.')
                if len(cparts) == len(parts)+1 and cparts[:-1] == parts:
                    subcategories.append({'name':cparts[-1],
                        'url':candidate,
                        'icon':category_icon(toplevel, meta)})

            category_name = toplevel[1:].split('.')
            # When browsing by user categories we ignore hierarchical normal
            # columns, so children can be empty

        elif toplevel in hierarchical_categories:
            items = []

            category_names = [x.original_name.split('.') for x in categories[toplevel] if
                    '.' in x.original_name]

            if subcategory is None:
                children = set(x[0] for x in category_names)
                category_name = [meta['name']]
                items = [x for x in categories[toplevel] if '.' not in x.original_name]
            else:
                subcategory_parts = subcategory.split('.')[1:]
                category_name = [meta['name']] + subcategory_parts

                lsp = len(subcategory_parts)
                children = set('.'.join(x) for x in category_names if len(x) ==
                        lsp+1 and x[:lsp] == subcategory_parts)
                items = [x for x in categories[toplevel] if x.original_name in
                        children]
                item_names = {x:x.original_name.rpartition('.')[-1] for x in
                        items}
                # Only mark the subcategories that have children themselves as
                # subcategories
                children = set('.'.join(x[:lsp+1]) for x in category_names if len(x) >
                        lsp+1 and x[:lsp] == subcategory_parts)
            subcategories = [{'name':x.rpartition('.')[-1],
                'url':toplevel+'.'+x,
                'icon':category_icon(toplevel, meta)} for x in children]
        else:
            items = categories[toplevel]
            category_name = meta['name']

        for x in subcategories:
            x['url'] = category_url(self.opts.url_prefix, x['url'])
            x['icon'] = icon_url(self.opts.url_prefix, x['icon'])
            x['is_category'] = True

        sort_keygen = {
                'name': lambda x: sort_key(x.sort if x.sort else x.original_name),
                'popularity': lambda x: x.count,
                'rating': lambda x: x.avg_rating
        }
        items.sort(key=sort_keygen[sort], reverse=sort_order == 'desc')
        total_num = len(items)
        items = items[offset:offset+num]
        items = [{
            'name':item_names.get(x, x.original_name),
            'average_rating': x.avg_rating,
            'count': x.count,
            'url': absurl(self.opts.url_prefix, '/ajax/books_in/%s/%s'%(
                encode_name(x.category if x.category else toplevel),
                encode_name(x.original_name if x.id is None else unicode(x.id)))),
            'has_children': x.original_name in children,
            } for x in items]

        return {
                'category_name': category_name,
                'base_url': base_url,
                'total_num': total_num,
                'offset':offset, 'num':len(items), 'sort':sort,
                'sort_order':sort_order,
                'subcategories':subcategories,
                'items':items,
        }


    # }}}

    # Books in the specified category {{{
    @Endpoint()
    def ajax_books_in(self, category, item, sort='title', num=25, offset=0,
            sort_order='asc'):
        try:
            dname, ditem = map(decode_name, (category, item))
        except:
            raise cherrypy.HTTPError(404, 'Invalid encoded param: %r'%category)

        try:
            num = int(num)
        except:
            raise cherrypy.HTTPError(404, "Invalid num: %r"%num)
        try:
            offset = int(offset)
        except:
            raise cherrypy.HTTPError(404, "Invalid offset: %r"%offset)

        if sort_order not in ('asc', 'desc'):
            sort_order = 'asc'

        if dname in ('allbooks', 'newest'):
            ids = self.search_cache('')
        elif dname == 'search':
            try:
                ids = self.search_cache('search:"%s"'%ditem)
            except:
                raise cherrypy.HTTPError(404, 'Search: %r not understood'%ditem)
        else:
            try:
                cid = int(ditem)
            except:
                raise cherrypy.HTTPError(404,
                        'Category id %r not an integer'%ditem)

            if dname == 'news':
                dname = 'tags'
            ids = self.db.get_books_for_category(dname, cid)
            all_ids = set(self.search_cache(''))
            # Implement restriction
            ids = ids.intersection(all_ids)

        ids = list(ids)
        sfield = self.db.data.sanitize_sort_field_name(sort)
        if sfield not in self.db.field_metadata.sortable_field_keys():
            raise cherrypy.HTTPError(404, '%s is not a valid sort field'%sort)
        self.db.data.multisort(fields=[(sfield, sort_order == 'asc')], subsort=True,
                only_ids=ids)
        total_num = len(ids)
        ids = ids[offset:offset+num]
        return {
                'total_num': total_num, 'sort_order':sort_order,
                'offset':offset, 'num':len(ids), 'sort':sort,
                'base_url':'/ajax/books_in/%s/%s'%(category, item),
                'book_ids':ids
        }


    # }}}

