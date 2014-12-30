
__license__   = 'GPL v3'
__copyright__ = '2014, Emily Palmieri <silentfuzzle@gmail.com>'

from calibre.gui2.viewer.behavior.base_behavior import BaseBehavior

# This class defines an Adventurous Reader behavior where users can only view one section of the ebook at a time.
class BaseAdventurousBehavior (BaseBehavior):
    
    # Constructor
    # default_number_of_pages (number) - the total number of pages in the ebook
    # setup_vscrollbar_method (method) - the method setting up the scrollbar and the position displayed in the upper left
    def __init__(self, default_number_of_pages, setup_vscrollbar_method):
        BaseBehavior.__init__(self, default_number_of_pages)
        self.setup_vscrollbar_method = setup_vscrollbar_method
        
    # Sets the current section of the book the user is viewing
    # and the number of pages in that section
    # curr_index (integer) - the index of the current section in the spine
    # curr_sec (SpineItem) - the current section being displayed
    def set_curr_sec(self, curr_index, curr_sec):
        if (self.curr_sec != curr_sec):
            super(BaseAdventurousBehavior, self).set_curr_sec(curr_index, curr_sec)
        
        # Only setup the scrollbar and position label if this object is an instance of this class
        if (type(self) is BaseAdventurousBehavior):
            self.num_pages = curr_sec.pages
            self.setup_vscrollbar_method()
        
    # Returns whether the user can move from the current section to the passed section
    # next_sec (string) - the section to check
    def allow_page_turn(self, next_sec):
        if (self.curr_sec is None):
            # The book doesn't have a bookmark with the user's last position
            # Allow returning to the beginning of the book 
            return True
        
        return False

    # Returns the user's position relative to the section  and update the absolute position
    # Sets the new absolute position in the book
    # frac (number) - the scrollbar's position in relation to the current displayed section of the book
    def calculate_page_label(self, frac):
        section_position = frac*float(self.get_section_pages(self.curr_sec))
        self.absolute_position = self.curr_sec.start_page + section_position
        print (self.absolute_position)
        return section_position + 1
            
    # Moves the user to the passed page number using the passed method
    # new_page (number) - the page to move the user to as set by the scrollbar or position label
    # goto_page_method (method) - the method to use to move with
    def goto_page(self, new_page, goto_page_method):
        abs_pos = self.update_page_label(new_page)
        goto_page_method(abs_pos, allow_page_turn=False)
            
    # Returns the user's absolute position in the ebook given a position set by the scrollbar or position label
    # new_page (number) - the page to move the user to as set by the scrollbar or position label
    def update_page_label(self, new_page):
        return new_page + self.curr_sec.start_page - 1
         
            