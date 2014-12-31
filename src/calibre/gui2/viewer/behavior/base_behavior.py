
__license__   = 'GPL v3'
__copyright__ = '2014, Emily Palmieri <silentfuzzle@gmail.com>'

import abc

# This class defines methods and attributes that all page behaviors must have.
class BaseBehavior (object):
    PAGE_STEP = 100.
    
    # Constructor
    def __init__(self):
        self.absolute_position = 1.
        self.curr_sec = None
        self.last_label = 1.
        
    # Set the default/total number of pages found in the ebook
    # number_of_pages (number) - the total pages found in the ebook
    def setup_ebook(self, number_of_pages):
        self.num_pages = number_of_pages

    # Returns the page number to display in the upper left
    # Sets the new absolute position in the book
    # frac (number) - the scrollbar's position in relation to the current displayed section of the book
    def get_page_label(self, frac):
        self.last_label = self.calculate_page_label(frac)
        return self.last_label

    # Calculate the page number to display in the upper left and update the absolute position
    # Sets the new absolute position in the book
    # frac (number) - the scrollbar's position in relation to the current displayed section of the book        
    @abc.abstractmethod
    def calculate_page_label(self, frac):
        return
    
    # Returns whether the user can move from the current section to the passed section
    # next_sec (string) - the section to check
    @abc.abstractmethod
    def allow_page_turn(self, next_sec):
        return
    
    # Moves the user to the passed page number as set by the scrollbar or position label, using the passed method
    # new_page (number) - the page to move the user to
    # goto_page_method (method) - the method to use to move with
    @abc.abstractmethod
    def goto_page(self, new_page, goto_page_method):
        return
    
    # Sets the current section of the book the user is viewing
    # curr_index (integer) - the index of the current section in the spine
    # curr_sec (SpineItem) - the current section being displayed
    def set_curr_sec(self, curr_index, curr_sec):
        self.curr_sec = curr_sec
        self.curr_index = curr_index
    
    # Returns whether a position is within the range of a section
    # new_page (number) - the position to check
    # page (SpineItem) - the page
    def check_pages(self, new_page, page):
        return (new_page >= page.start_page and new_page < page.max_page + 1)
        
    # Returns the number of pages in the passed section
    # sec (SpineItem) - the section to return pages for
    def get_section_pages(self, sec):
        if (sec.pages == 1):
            return 0.8
        else:
            return sec.pages-1
        