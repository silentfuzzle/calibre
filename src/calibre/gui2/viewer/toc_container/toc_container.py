
__license__   = 'GPL v3'
__copyright__ = '2014, Emily Palmieri <silentfuzzle@gmail.com>'

from PyQt5.Qt import QWidget
import abc

# This class sets the default behaviors of all table of contents interfaces.
class TOCContainer(QWidget):

    # toc_sections (TOCSections) - a object that determines how the sections of the ebook are grouped
    # toc_model (calibre.gui2.viewer.TOC) - the object storing all information about the TOC hierarchy
    # title (string) - the title of the ebook
    # pathtoebook (string) - the full path to the ebook's location
    @abc.abstractmethod
    def setup_ebook(self, toc_sections, toc_model, title, pathtoebook):
        return

    # Performs any actions required before closing an ebook
    def close_ebook(self):
        return
        
    # If the table of contents interface is a network,
    # check if a connection should be added
    # curr_sec (SpineItem) - the current section
    # next_sec (SpineItem) - the section the user just navigated to
    def check_update_connection(self, curr_sec, next_sec):
        return
        
    # If the table of contents interface is a network,
    # add a connection between sections
    # start_sec (SpineItem) - the node/section to start the edge from
    # end_sec (string) - the node/section to end the edge at
    # start_sec_checked (boolean) - true if the passed start section was already checked for existence in the ebook's TOC
    def update_connection(self, start_sec, end_sec, start_sec_checked=False):
        return
        
    # If the table of contents interface is a network,
    # update the current section/node highlighted
    # curr_index (int) - the position if the current section in the spine
    # curr_sec (SpineItem) - the current section the user is viewing
    def update_curr_sec(self, curr_index, curr_sec):
        return
        
    # If the table of contents interface is a hierarchy,
    # update the highlighted index if needed
    # item_index (int) - the index to highlight
    def scroll_to(self, item_index):
        return
        