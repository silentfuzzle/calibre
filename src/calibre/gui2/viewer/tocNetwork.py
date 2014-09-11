#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2014, Emily Palmieri <silentfuzzle@gmail.com>'

import os
from PyQt5.Qt import (Qt, QWebView, pyqtSlot)
from calibre.ebooks.oeb.display.webview import load_html
from calibre.constants import iswindows
       
# This class displays an ebook network using an embedded Javascript application.
class TOCNetworkView (QWebView):

    # Constructor
    def __init__(self, *args):
        QWebView.__init__(self, *args)
        
        self.manager = None
        self.loadFinished.connect(self.load_finished)
        
    # Update the network displayed in the Javascript application
    # jsonCode (string) - the data defining the edges and nodes in the network
    def load_network(self, jsonCode):
        self.jsonCode = jsonCode
        path = P(u'adventurous_map_viewer/book_renderer.html').replace(os.sep, '/')
        path = str(path)
        load_html(path, self, codec=getattr(path, 'encoding', 'utf-8'), mime_type=getattr(path,
        'mime_type', 'text/html'))
        
    # Displays the network when the Javascript code has finished loading
    def load_finished(self):
        self.page().mainFrame().addToJavaScriptWindowObject("container", self)
        
        jScript = """dataLoaded({jsonCode}); """
        jScriptFormat = jScript.format(jsonCode=str(self.jsonCode))
        self.page().mainFrame().evaluateJavaScript(jScriptFormat)
        
    # Sets the pointer to the EbookViewer object
    # manager (EbookViewer) - the class controlling the ebook viewer interface
    def set_manager(self, manager):
        self.manager = manager
        
    # Called from the Javascript application when the user clicks a node
    # Changes the user's position in the book to the node/section that was clicked
    # page (float) - the page to send the user to
    @pyqtSlot(float)
    def change_page(self, page):
        print ("changed page: " + str(page))
        if self.manager is not None:
            self.manager.internal_link_clicked(0)
            self.manager.goto_page(page)
            