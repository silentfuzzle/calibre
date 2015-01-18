        
__license__   = 'GPL v3'
__copyright__ = '2014, Emily Palmieri <silentfuzzle@gmail.com>'

from functools import partial
from PyQt5.Qt import (QVBoxLayout, QWidget, QModelIndex)
from calibre.gui2.viewer.toc import TOCView, TOCSearch
from calibre.gui2.viewer.toc_container.toc_container import TOCContainer

# This class defines a hierarchical table of contents interface and control set.
class TreeTOCContainer(TOCContainer):

    # Constructor
    # parent (EBookViewer) - the main interface
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
    # toc_sections (TOCSections) - a object that determines how the sections of the ebook are grouped
    # toc_model (calibre.gui2.viewer.TOC) - the object storing all information about the hierarchy
    # title (string) - the title of the ebook
    # pathtoebook (string) - the full path to the ebook's location
    def setup_ebook(self, toc_sections, toc_model, title, pathtoebook):
        self.toc.setModel(toc_model)
        
    # Updates the selected item in the hierarchy
    # item_index (int) - the index to highlight
    def scroll_to(self, item_index):
        self.toc.scrollTo(item_index)
        