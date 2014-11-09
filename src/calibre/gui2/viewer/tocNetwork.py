#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2014, Emily Palmieri <silentfuzzle@gmail.com>'

import os
from PyQt5.Qt import (Qt, QWebView, pyqtSlot)
from calibre.ebooks.oeb.display.webview import load_html
       
# This class displays an ebook network using an embedded Javascript application.
class TOCNetworkView (QWebView):

    # Constructor
    def __init__(self, *args):
        QWebView.__init__(self, *args)
        
        self.manager = None
        self.setMinimumWidth(80)
        self.loadFinished.connect(self.load_finished)
        self.curr_page = -1;
        
    # Update the network displayed in the Javascript application
    # jsonCode (string) - the data defining the edges and nodes in the network
    def load_network(self, jsonCode):
        self.jsonCode = jsonCode
        path = P(u'adventurous_map_viewer/book_renderer.html').replace(os.sep, '/')
        path = str(path)
        load_html(path, self, codec=getattr(path, 'encoding', 'utf-8'), mime_type=getattr(path,
        'mime_type', 'text/html'))
        self.loaded = False;
        
    # Displays the network when the Javascript code has finished loading
    def load_finished(self):
        self.loaded = True;
        self.page().mainFrame().addToJavaScriptWindowObject("container", self)
        self.create_toc_network()
            
    # Adds a new edge to the displayed network
    # newJSON (string) - the data defining the edges and nodes in the network
    def add_edge(self, newJSON):
        self.jsonCode = newJSON
        if (self.loaded):
            self.create_toc_network()
        
    # Update the network with the the current stored json code
    def create_toc_network(self):
        jScript = """dataLoaded({jsonCode}, {page}); """
        jScriptFormat = jScript.format(jsonCode=str(self.jsonCode), page=self.curr_page)
        self.page().mainFrame().evaluateJavaScript(jScriptFormat)
        
    # Update the network to show the user's new position
    # page (float) - the first page of the section the user is viewing
    # history_offset (int) - An integer representing how the user navigated to the section
    #      0 - the user clicked a link in the e-book or a node in the network
    #      1 - the user navigated to the next section in their history
    #      -1 - the user navigated to the previous section in their history
    def set_curr_page(self, page, history_offset):
        self.curr_page = page
        if (self.loaded): 
            jScript = """changePage({page}, {offset}); """
            jScriptFormat = jScript.format(page=page, offset=history_offset)
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
            