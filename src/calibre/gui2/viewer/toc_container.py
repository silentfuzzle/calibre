
__license__   = 'GPL v3'
__copyright__ = '2014, Emily Palmieri <silentfuzzle@gmail.com>'

from PyQt5.Qt import (QVBoxLayout, QWidget, QModelIndex)
from functools import partial
from calibre.gui2.viewer.tocNetwork import TOCNetworkView, TOCNetworkSearch, TOCNetworkTools
from calibre.gui2.viewer.toc import TOCView, TOCSearch
from calibre.gui2.viewer.book_network import EBookNetwork

# This class defines a hierarchical table of contents interface and control set.
class CalibreTOCContainer(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        w = self
        w.l = QVBoxLayout(w)
        self.toc = TOCView(w)
        self.toc_search = TOCSearch(self.toc, parent=w)
        w.l.addWidget(self.toc)
        w.l.addWidget(self.toc_search)
        w.l.setContentsMargins(0, 0, 0, 0)
        
    # Connects the click method of the TOC interface to a method from EBookViewer
    # toc_clicked_method (method) - the method to connect the action to
    def connect_toc_actions(self, toc_clicked_method):
        self.toc.pressed[QModelIndex].connect(toc_clicked_method)
        self.toc.searched.connect(partial(toc_clicked_method, force=True))
        
    # Sets the hierarchy of information for display
    # toc_model (calibre.gui2.viewer.TOC) - the object storing all information about the hierarchy
    def setup_ebook(self, toc_model):
        self.toc.setModel(toc_model)

# This class defines a network table of contents interface and control set.
class AdventurousTOCContainer(QWidget):

    # Constructor
    # manager (EBookViewer) - the ebook viewer interface
    # parent (EBookViewer) - the parent of this container
    def __init__(self, manager, parent=None):
        QWidget.__init__(self, parent)
        w = self
                    
        # Build the network interface
        self.toc = TOCNetworkView(w)
        self.toc.set_manager(manager)
        
        # Build the network interface tools
        tools = TOCNetworkTools(self.toc, parent=w)                
        self.toc_search = TOCNetworkSearch(self.toc, parent=w)
        
        # Layout the interface
        w.l = QVBoxLayout(w)
        w.l.addWidget(self.toc)
        w.l.addWidget(tools)
        w.l.addWidget(self.toc_search)
        w.l.setContentsMargins(0, 0, 0, 0)
        
    # Sets the network of information for display
    # spine - (List(SpineItem)) the current ebook's ordering of sections
    # toc - (calibre.ebooks.metadata.toc.TOC) the current ebook's TOC
    # title (string) - the title of the ebook
    # pathtoebook (string) - the full path to the ebook's location
    def setup_ebook(self, spine, toc, title, pathtoebook):
        ebook_network = EBookNetwork(spine, toc, title, pathtoebook)
        self.toc.set_ebook_network(ebook_network)