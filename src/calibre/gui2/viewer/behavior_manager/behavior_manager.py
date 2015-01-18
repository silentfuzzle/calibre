
__license__   = 'GPL v3'
__copyright__ = '2014, Emily Palmieri <silentfuzzle@gmail.com>'

from calibre.gui2.viewer.behavior.base_behavior import BaseBehavior

# This class displays an ebook using the specified page behavior and TOC interface.
class BehaviorManager (BaseBehavior):

    # Constructor
    # page_behavior (BaseBehavior) - the behavior to use in displaying page numbers and book text
    # toc_interface (TOCContainer) - the TOC interface to use
    def __init__(self, page_behavior, toc_interface):
        self.page_behavior = page_behavior
        self.toc_interface = toc_interface
        
    # Sets up the ebook for display using this behavior manager
    # number_of_pages (int) - the total number of pages in the ebook
    # toc_sections (TOCSections) - a object that determines how the sections of the ebook are grouped
    # toc_model (calibre.gui2.viewer.TOC) - the object storing all information about the visual TOC hierarchy
    # title (string) - the title of the ebook
    # pathtoebook (string) - the full path to the ebook's location
    def setup_ebook(self, number_of_pages, toc_sections, toc_model, title, 
            pathtoebook):
        self.page_behavior.setup_ebook(number_of_pages, toc_sections)
        self.toc_interface.setup_ebook(toc_sections, toc_model, title, pathtoebook)
        
    # Sets the history offset for the correct behavior
    # offset (int) - the new value of the history offset
    def set_history_offset(self, offset):
        self.toc_interface.history_offset = offset
        
    # Updates the TOC scrollbar if the TOC interface is hierarchical
    # item_index (int) - the index of the item in the hierarchy to scroll to
    def scroll_to(self, item_index):
        self.toc_interface.scroll_to(item_index)
        
    # Creates a connection between sections/nodes if a network TOC interface is in use
    # start_sec (SpineItem) - the node/section to start the edge from
    # end_sec (string) - the node/section to end the edge at
    def update_connection(self, start_sec, end_sec):
        self.toc_interface.update_connection(start_sec, end_sec)
            
    # Returns the users current position in the ebook
    def get_absolute_position(self):
        return self.page_behavior.absolute_position
    
    # Returns the total number of pages to display
    def get_num_pages(self):
        return self.page_behavior.num_pages
                        
    ###########################################################################
    #BaseBehavior Methods
    ###########################################################################
        
    # Returns whether a position is within the range of a section
    # new_page (number) - the position to check
    # page (SpineItem) - the page
    def check_pages(self, new_page, page):
        return self.page_behavior.check_pages(new_page, page)
        
    # Returns the number of pages in the passed section
    # sec (SpineItem) - the section to return pages for
    def get_section_pages(self, sec):
        return self.page_behavior.get_section_pages(sec)
        
    # Moves the user to the passed page number as set by the scrollbar or position label, using the passed method
    # new_page (number) - the page to move the user to
    # goto_page_method (method) - the method to use to move with
    def goto_page(self, new_page, goto_page_method):
        return self.page_behavior.goto_page(new_page, goto_page_method)
        
    # Returns the page number to display in the upper left
    # Sets the new absolute position in the book
    # frac (number) - the scrollbar's position in relation to the current displayed section of the book
    def get_page_label(self, frac):
        return self.page_behavior.get_page_label(frac)
    
    # Returns whether the user can move from the current section to the passed section
    # next_sec (string) - the section to check
    def allow_page_turn(self, next_sec):
        # Add a connection between the current and next section if a network TOC interface is in use
        curr_sec = self.page_behavior.curr_sec
        self.toc_interface.check_update_connection(curr_sec, next_sec)
        
        return self.page_behavior.allow_page_turn(next_sec)
    
    # Sets the current section of the book the user is viewing
    # curr_index (integer) - the index of the current section in the spine
    # curr_sec (SpineItem) - the current section being displayed
    def set_curr_sec(self, curr_index, curr_sec):
        self.page_behavior.set_curr_sec(curr_index, curr_sec)
        self.toc_interface.update_curr_sec(curr_index, curr_sec)
            