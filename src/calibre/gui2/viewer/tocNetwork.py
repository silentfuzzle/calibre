#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2014, Emily Palmieri <silentfuzzle@gmail.com>'

import os
from PyQt5.Qt import (Qt, QWebView, pyqtSlot)
from calibre.ebooks.oeb.display.webview import load_html
from calibre.gui2.viewer.toc import TOCSearch
       
# This class controls the widget that allows users to search through node titles.
class TOCNetworkSearch(TOCSearch):

    # Searches for text input by the user
    def do_search(self, text):
        if not text or not text.strip():
            return
        index = self.toc_view.search(text)
        if index != -1:
            error_dialog(self.toc_view, _('No matches found'), _(
                'There are no Table of Contents entries matching: %s') % text, show=True)
        self.search.search_done(True)
        
# This class displays an ebook network using an embedded Javascript application.
class TOCNetworkView (QWebView):

    # Constructor
    def __init__(self, *args):
        QWebView.__init__(self, *args)
        
        self.manager = None
        self.setMinimumWidth(80)
        self.loadFinished.connect(self.load_finished)
        self.curr_page = -1
        
    # Update the network displayed in the Javascript application
    def load_network(self):
        path = P(u'adventurous_map_viewer/book_renderer.html').replace(os.sep, '/')
        path = str(path)
        load_html(path, self, codec=getattr(path, 'encoding', 'utf-8'), mime_type=getattr(path,
        'mime_type', 'text/html'))
        self.loaded = False
        self.toc_created = False
        
    # Displays the network when the Javascript code has finished loading
    def load_finished(self):
        self.loaded = True
        self.page().mainFrame().addToJavaScriptWindowObject("container", self)
        if (self.curr_page != -1 and self.toc_created == False):
            self.create_toc_network(0)
            
    # Stores a new edge to add to the network
    # start_sec (SpineItem) - the source node
    # end_sec (SpineItem) - the target node
    def add_edge(self, start_sec, end_sec):
        edge_added = self.ebook_network.add_edge(start_sec.start_page, end_sec.start_page)
        
        # Add the new edge to the network display
        if (edge_added):
            self.toc_created = False
        
    # Update the network with the the current stored json code and page number
    # history_offset (int) - An integer representing how the user navigated to the section
    #      0 - the user clicked a link in the e-book or a node in the network
    #      1 - the user navigated to the next section in their history
    #      -1 - the user navigated to the previous section in their history
    #      -2 - the user navigated to another section without adding to their history
    def create_toc_network(self, history_offset):
        jScript = """dataLoaded({jsonCode}, {page}, {offset}); """
        jScriptFormat = jScript.format(jsonCode=str(self.ebook_network.data), page=self.curr_page, offset=history_offset)
        self.page().mainFrame().evaluateJavaScript(jScriptFormat)
        self.toc_created = True
        
    # Update the network to show the user's new position
    # page (float) - the first page of the section the user is viewing
    # history_offset (int) - An integer representing how the user navigated to the section
    #      0 - the user clicked a link in the e-book or a node in the network
    #      1 - the user navigated to the next section in their history
    #      -1 - the user navigated to the previous section in their history
    #      -2 - the user navigated to another section without adding to their history
    def set_curr_page(self, page, history_offset):
        self.curr_page = page
        if (self.loaded):
            if (self.toc_created):
                # The network doesn't need to be reloaded, change the page
                jScript = """changePage({page}, {offset}); """
                jScriptFormat = jScript.format(page=page, offset=history_offset)
                self.page().mainFrame().evaluateJavaScript(jScriptFormat)
            else:
                # The user clicked a link or the Javascript finished
                # loading before this method was called, reload the network data
                self.create_toc_network(history_offset)
                
    # Searches through the titles of the nodes in the network for the given search term
    # text (string) - the text to search for
    def search(self, text):
        found_page = self.ebook_network.search(text)
        if (found_page != -1):
            self.set_curr_page(found_page, -2)
            
        return found_page
    
    # Sets the object containing the json data to display in the network interface
    # ebook_network (EBookNetwork) - the object
    def set_ebook_network(self, ebook_network):
        self.ebook_network = ebook_network
        self.load_network()
        
    # Sets the pointer to the EbookViewer object
    # manager (EbookViewer) - the class controlling the ebook viewer interface
    def set_manager(self, manager):
        self.manager = manager
        
    # Called from the Javascript application when the user clicks a node
    # Changes the user's position in the book to the node/section that was clicked
    # page (float) - the page to send the user to
    @pyqtSlot(float)
    def change_page(self, page):
        if self.manager is not None:
            self.manager.internal_link_clicked(0)
            self.manager.goto_page(page)
            