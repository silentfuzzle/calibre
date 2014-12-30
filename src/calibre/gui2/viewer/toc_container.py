
__license__   = 'GPL v3'
__copyright__ = '2014, Emily Palmieri <silentfuzzle@gmail.com>'

from PyQt5.Qt import (QVBoxLayout, QWidget, QModelIndex)
from functools import partial
from calibre.gui2.viewer.toc import TOCView, TOCSearch

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
        