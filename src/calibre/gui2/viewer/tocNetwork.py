#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2012, Kovid Goyal <kovid@kovidgoyal.net>'
__docformat__ = 'restructuredtext en'
# Adventurous Reader modifications added by Emily Palmieri <silentfuzzle@gmail.com>

import re
from PyQt5.Qt import (Qt, QWebView, pyqtSlot)
from calibre.ebooks.oeb.display.webview import load_html
       
class TOCNetworkView (QWebView):

    def __init__(self, *args):
        QWebView.__init__(self, *args)
        
        self.manager = None
        self.loadFinished.connect(self.load_finished)
        
    def load_network(self, jsonCode):
        self.jsonCode = jsonCode
        path = 'C:/Users/Emily/Documents/GitHub/calibre/resources/adventurous_map_viewer/book_renderer.html'
        load_html(path, self, codec=getattr(path, 'encoding', 'utf-8'), mime_type=getattr(path,
        'mime_type', 'text/html'))
        
    def load_finished(self):
        self.page().mainFrame().addToJavaScriptWindowObject("container", self)
        
        jScript = """dataLoaded({jsonCode}); """
        jScriptFormat = jScript.format(jsonCode=str(self.jsonCode))
        self.page().mainFrame().evaluateJavaScript(jScriptFormat)
        
    def set_manager(self, manager):
        self.manager = manager
        
    @pyqtSlot(float)
    def change_page(self, page):
        print ("changed page: " + str(page))
        if self.manager is not None:
            self.manager.goto_page(page)
            