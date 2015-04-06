#!/usr/bin/env python
# vim:fileencoding=utf-8
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__ = 'GPL v3'
__copyright__ = '2013, Kovid Goyal <kovid at kovidgoyal.net>'

import re

from calibre.ebooks.docx.writer.container import create_skeleton
from calibre.ebooks.docx.writer.styles import w, StylesManager
from calibre.ebooks.docx.writer.images import ImagesManager
from calibre.ebooks.docx.writer.fonts import FontsManager
from calibre.ebooks.docx.writer.tables import Table
from calibre.ebooks.oeb.stylizer import Stylizer as Sz, Style as St
from calibre.ebooks.oeb.base import XPath, barename

class Style(St):

    def __init__(self, *args, **kwargs):
        St.__init__(self, *args, **kwargs)
        self._letterSpacing = None

    @property
    def letterSpacing(self):
        if self._letterSpacing is not None:
            val = self._get('letter-spacing')
            if val == 'normal':
                self._letterSpacing = val
            else:
                self._letterSpacing = self._unit_convert(val)
        return self._letterSpacing

class Stylizer(Sz):

    def style(self, element):
        try:
            return self._styles[element]
        except KeyError:
            return Style(element, self)


class TextRun(object):

    ws_pat = None

    def __init__(self, style, first_html_parent):
        self.first_html_parent = first_html_parent
        if self.ws_pat is None:
            TextRun.ws_pat = self.ws_pat = re.compile(r'\s+')
        self.style = style
        self.texts = []

    def add_text(self, text, preserve_whitespace):
        if not preserve_whitespace:
            text = self.ws_pat.sub(' ', text)
            if text.strip() != text:
                # If preserve_whitespace is False, Word ignores leading and
                # trailing whitespace
                preserve_whitespace = True
        self.texts.append((text, preserve_whitespace))

    def add_break(self, clear='none'):
        self.texts.append((None, clear))

    def add_image(self, drawing):
        self.texts.append((drawing, None))

    def serialize(self, p):
        r = p.makeelement(w('r'))
        p.append(r)
        rpr = r.makeelement(w('rPr'))
        rpr.append(rpr.makeelement(w('rStyle'), **{w('val'):self.style.id}))
        r.append(rpr)
        for text, preserve_whitespace in self.texts:
            if text is None:
                r.append(r.makeelement(w('br'), **{w('clear'):preserve_whitespace}))
            elif hasattr(text, 'xpath'):
                r.append(text)
            else:
                t = r.makeelement(w('t'))
                r.append(t)
                t.text = text or ''
                if preserve_whitespace:
                    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')

    def is_empty(self):
        if not self.texts:
            return True
        if len(self.texts) == 1 and self.texts[0] == ('', False):
            return True
        return False

class Block(object):

    def __init__(self, styles_manager, html_block, style):
        self.html_block = html_block
        self.html_style = style
        self.style = styles_manager.create_block_style(style, html_block)
        self.styles_manager = styles_manager
        self.keep_next = False
        self.page_break_before = False
        self.runs = []

    def add_text(self, text, style, ignore_leading_whitespace=False, html_parent=None, is_parent_style=False):
        ts = self.styles_manager.create_text_style(style, is_parent_style=is_parent_style)
        ws = style['white-space']
        if self.runs and ts == self.runs[-1].style:
            run = self.runs[-1]
        else:
            run = TextRun(ts, self.html_block if html_parent is None else html_parent)
            self.runs.append(run)
        preserve_whitespace = ws in {'pre', 'pre-wrap'}
        if ignore_leading_whitespace and not preserve_whitespace:
            text = text.lstrip()
        if ws == 'pre-line':
            for text in text.splitlines():
                run.add_text(text, False)
                run.add_break()
        else:
            run.add_text(text, preserve_whitespace)

    def add_break(self, clear='none'):
        if self.runs:
            run = self.runs[-1]
        else:
            run = TextRun(self.styles_manager.create_text_style(self.html_style), self.html_block)
            self.runs.append(run)
        run.add_break(clear=clear)

    def add_image(self, drawing):
        if self.runs:
            run = self.runs[-1]
        else:
            run = TextRun(self.styles_manager.create_text_style(self.html_style), self.html_block)
            self.runs.append(run)
        run.add_image(drawing)

    def serialize(self, body):
        p = body.makeelement(w('p'))
        body.append(p)
        ppr = p.makeelement(w('pPr'))
        p.append(ppr)
        if self.keep_next:
            ppr.append(ppr.makeelement(w('keepNext')))
        if self.page_break_before:
            ppr.append(ppr.makeelement(w('pageBreakBefore')))
        ppr.append(ppr.makeelement(w('pStyle'), **{w('val'):self.style.id}))
        for run in self.runs:
            run.serialize(p)

    def is_empty(self):
        for run in self.runs:
            if not run.is_empty():
                return False
        return True

class Blocks(object):

    def __init__(self, styles_manager):
        self.styles_manager = styles_manager
        self.all_blocks = []
        self.pos = 0
        self.current_block = None
        self.items = []
        self.tables = []
        self.current_table = None
        self.open_html_blocks = set()

    def current_or_new_block(self, html_tag, tag_style):
        return self.current_block or self.start_new_block(html_tag, tag_style)

    def end_current_block(self):
        if self.current_block is not None:
            self.all_blocks.append(self.current_block)
            if self.current_table is not None:
                self.current_table.add_block(self.current_block)
            else:
                self.block_map[self.current_block] = len(self.items)
                self.items.append(self.current_block)
        self.current_block = None

    def start_new_block(self, html_block, style):
        self.end_current_block()
        self.current_block = Block(self.styles_manager, html_block, style)
        self.open_html_blocks.add(html_block)
        return self.current_block

    def start_new_table(self, html_tag, tag_style=None):
        self.current_table = Table(html_tag, tag_style)
        self.tables.append(self.current_table)

    def start_new_row(self, html_tag, tag_style):
        if self.current_table is None:
            self.start_new_table(html_tag)
        self.current_table.start_new_row(html_tag, tag_style)

    def start_new_cell(self, html_tag, tag_style):
        if self.current_table is None:
            self.start_new_table(html_tag)
        self.current_table.start_new_cell(html_tag, tag_style)

    def finish_tag(self, html_tag):
        if self.current_block is not None and html_tag in self.open_html_blocks:
            self.end_current_block()
            self.open_html_blocks.discard(html_tag)

        if self.current_table is not None:
            table_finished = self.current_table.finish_tag(html_tag)
            if table_finished:
                table = self.tables[-1]
                del self.tables[-1]
                if self.tables:
                    self.current_table = self.tables[-1]
                    self.current_table.add_table(table)
                else:
                    self.current_table = None
                    self.block_map[table] = len(self.items)
                    self.items.append(table)

    def serialize(self, body):
        for item in self.items:
            item.serialize(body)

    def __enter__(self):
        self.pos = len(self.all_blocks)
        self.block_map = {}

    def __exit__(self, *args):
        if self.current_block is not None:
            self.all_blocks.append(self.current_block)
        self.current_block = None
        if len(self.all_blocks) > self.pos and self.all_blocks[self.pos].is_empty():
            # Delete the empty block corresponding to the <body> tag when the
            # body tag has no inline content before its first sub-block
            block = self.all_blocks[self.pos]
            del self.all_blocks[self.pos]
            del self.items[self.block_map.pop(block)]
        if self.pos > 0 and self.pos < len(self.all_blocks):
            # Insert a page break corresponding to the start of the html file
            self.all_blocks[self.pos].page_break_before = True

class Convert(object):

    def __init__(self, oeb, docx):
        self.oeb, self.docx = oeb, docx
        self.log, self.opts = docx.log, docx.opts

    def __call__(self):
        from calibre.ebooks.oeb.transforms.rasterize import SVGRasterizer
        self.svg_rasterizer = SVGRasterizer()
        self.svg_rasterizer(self.oeb, self.opts)

        self.styles_manager = StylesManager()
        self.images_manager = ImagesManager(self.oeb, self.docx.document_relationships)
        self.fonts_manager = FontsManager(self.oeb, self.opts)
        self.blocks = Blocks(self.styles_manager)

        for item in self.oeb.spine:
            self.process_item(item)

        self.styles_manager.finalize(self.blocks.all_blocks)
        self.write()

    def process_item(self, item):
        stylizer = self.svg_rasterizer.stylizer_cache.get(item)
        if stylizer is None:
            stylizer = Stylizer(item.data, item.href, self.oeb, self.opts, self.opts.output_profile)
        self.abshref = self.images_manager.abshref = item.abshref

        for i, body in enumerate(XPath('//h:body')(item.data)):
            with self.blocks:
                self.process_tag(body, stylizer, is_first_tag=i == 0)

    def process_tag(self, html_tag, stylizer, is_first_tag=False):
        tagname = barename(html_tag.tag)
        if tagname in {'script', 'style', 'title', 'meta'}:
            return
        tag_style = stylizer.style(html_tag)
        if tag_style.is_hidden:
            return
        display = tag_style._get('display')
        if display in {'inline', 'inline-block'} or tagname == 'br':  # <br> has display:block but we dont want to start a new paragraph
            self.add_inline_tag(tagname, html_tag, tag_style, stylizer)
        elif display == 'list-item':
            # TODO: Implement this
            self.add_block_tag(tagname, html_tag, tag_style, stylizer)
        elif display.startswith('table') or display == 'inline-table':
            if display == 'table-cell':
                self.blocks.start_new_cell(html_tag, tag_style)
                self.add_block_tag(tagname, html_tag, tag_style, stylizer)
            elif display == 'table-row':
                self.blocks.start_new_row(html_tag, tag_style)
            elif display in {'table', 'inline-table'}:
                self.blocks.start_new_table(html_tag, tag_style)
        else:
            if tagname == 'img' and tag_style['float'] in {'left', 'right'}:
                # Image is floating so dont start a new paragraph for it
                self.add_inline_tag(tagname, html_tag, tag_style, stylizer)
            else:
                self.add_block_tag(tagname, html_tag, tag_style, stylizer)

        for child in html_tag.iterchildren('*'):
            self.process_tag(child, stylizer)

        is_block = html_tag in self.blocks.open_html_blocks
        self.blocks.finish_tag(html_tag)
        if is_block and tag_style['page-break-after'] == 'avoid':
            self.blocks.all_blocks[-1].keep_next = True

        if display == 'table-row':
            return  # We ignore the tail for these tags

        if not is_first_tag and html_tag.tail and (not is_block or not html_tag.tail.isspace()):
            # Ignore trailing space after a block tag, as otherwise it will
            # become a new empty paragraph
            block = self.blocks.current_or_new_block(html_tag.getparent(), stylizer.style(html_tag.getparent()))
            block.add_text(html_tag.tail, stylizer.style(html_tag.getparent()), is_parent_style=True)

    def add_block_tag(self, tagname, html_tag, tag_style, stylizer):
        block = self.blocks.start_new_block(html_tag, tag_style)
        if tagname == 'img':
            self.images_manager.add_image(html_tag, block, stylizer)
        else:
            if html_tag.text:
                block.add_text(html_tag.text, tag_style, ignore_leading_whitespace=True, is_parent_style=True)

    def add_inline_tag(self, tagname, html_tag, tag_style, stylizer):
        if tagname == 'br':
            if html_tag.tail or html_tag is not tuple(html_tag.getparent().iterchildren('*'))[-1]:
                block = self.blocks.current_or_new_block(html_tag.getparent(), stylizer.style(html_tag.getparent()))
                block.add_break(clear={'both':'all', 'left':'left', 'right':'right'}.get(tag_style['clear'], 'none'))
        elif tagname == 'img':
            block = self.blocks.current_or_new_block(html_tag.getparent(), stylizer.style(html_tag.getparent()))
            self.images_manager.add_image(html_tag, block, stylizer)
        else:
            if html_tag.text:
                block = self.blocks.current_or_new_block(html_tag.getparent(), stylizer.style(html_tag.getparent()))
                block.add_text(html_tag.text, tag_style, is_parent_style=False)

    def write(self):
        self.docx.document, self.docx.styles, body = create_skeleton(self.opts)
        self.blocks.serialize(body)
        body.append(body[0])  # Move <sectPr> to the end
        self.styles_manager.serialize(self.docx.styles)
        self.images_manager.serialize(self.docx.images)
        self.fonts_manager.serialize(self.styles_manager.text_styles, self.docx.font_table, self.docx.embedded_fonts, self.docx.fonts)
