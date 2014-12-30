
__license__   = 'GPL v3'
__copyright__ = '2014, Emily Palmieri <silentfuzzle@gmail.com>'

from PyQt5.Qt import (QVBoxLayout, QWidget)
from calibre.gui2.viewer.book_network import EBookNetwork
from calibre.gui2.viewer.tocNetwork import TOCNetworkView, TOCNetworkSearch, TOCNetworkTools

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
    # toc_sections (TOCSections) - a object that determines how the sections of the ebook are grouped
    # title (string) - the title of the ebook
    # pathtoebook (string) - the full path to the ebook's location
    def setup_ebook(self, spine, toc, toc_sections, title, pathtoebook):
        ebook_network = EBookNetwork(spine, toc, title, pathtoebook)
        self.toc.set_ebook_network(ebook_network)
        self.toc_sections = toc_sections
        self.history_offset = 0
        
    # Check if an edge should be added to the network before adding it
    # curr_sec (SpineItem) - the current section
    # next_sec (SpineItem) - the section the user just navigated to
    def check_add_network_edge(self, curr_sec, next_sec):
        curr_index = self.toc_sections.spine.index(curr_sec)
        next_index = self.toc_sections.spine.index(next_sec)
        if (curr_sec is not None and next_index in self.toc_sections.include_sections):            
            # Don't add an edge if the user skipped sections in the book using the scrollbar or position label
            if (next_index == curr_index + 1 or next_index == curr_index - 1):
                self.add_network_edge(self.toc_sections.corrected_curr_sec, 
                        next_sec, True)

    # Adds an edge to the ebook network
    # start_sec (SpineItem) - the node/section to start the edge from
    # end_sec (string) - the node/section to end the edge at
    # start_sec_checked (boolean) - true if the passed start section was already checked for existence in the ebook's TOC
    def add_network_edge(self, start_sec, end_sec, start_sec_checked=False):
        # Get the TOC and SpineItem entries for the passed end section
        end_toc, corrected_end_sec = self.toc_sections.check_and_get_toc(end_sec)
        
        if (start_sec_checked == False):
            # Get the TOC and SpineItem entries for the passed start section
            start_toc, start_sec = self.toc_sections.check_and_get_toc(start_sec)
        
        # Add an edge to the network
        if (corrected_end_sec != start_sec):
            self.toc.add_edge(start_sec, corrected_end_sec)
                 
    # Update the user's position and history in the network view
    # curr_sec (SpineItem) - the current section the user is viewing
    def update_network_pos(self):
        self.toc.set_curr_page(self.toc_sections.corrected_curr_sec.start_page, 
                self.history_offset)
        self.history_offset = -2
        