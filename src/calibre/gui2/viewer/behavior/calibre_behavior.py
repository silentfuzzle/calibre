
__license__   = 'GPL v3'
__copyright__ = '2014, Emily Palmieri <silentfuzzle@gmail.com>'

from calibre.gui2.viewer.behavior.base_behavior import BaseBehavior

# This class defines the default Calibre page behavior.
class CalibreBehavior (BaseBehavior):
        
    # Returns the page number to display in the upper left
    # Sets the new absolute position in the book
    # frac (number) - the scrollbar's position in relation to the current displayed section of the book
    def get_page_label(self, frac):
        self.absolute_position = self.curr_sec.start_page + frac*float(self.curr_sec.pages-1)
        return self.absolute_position
        
    # Returns whether the user can move from the current section to the passed section
    # Always true in Calibre's original viewer
    # next_sec (string) - the section to check
    def allow_page_turn(self, next_sec):
        return True
        
    # Moves the user to the passed page number using the passed method
    # new_page (number) - the page to move the user to
    # goto_page_method (method) - the method to use to move with
    def goto_page(self, new_page, goto_page_method):
        goto_page_method(new_page)
        
    # Returns the maximum number of pages to display to the user
    # Always the number of pages in the ebook
    def get_num_pages(self):
        return self.num_pages
        
        
        
    # Originally defined in Calibre but don't appear to work under certain conditions
    #def get_section_pages(self, sec):
        #return sec.pages-1
    #def check_pages(self, new_page, page):
        #return (new_page >= page.start_page and new_page <= page.max_page)