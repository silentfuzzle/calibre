
__license__   = 'GPL v3'
__copyright__ = '2014, Emily Palmieri <silentfuzzle@gmail.com>'

from calibre.gui2.viewer.behavior.adventurous_base_behavior import BaseAdventurousBehavior

# This class defines an Adventurous Reader behavior where users can view a group of sections at a time. This group includes sub-sections
# and adjacent sections not included in the TOC.
class AdventurousBehavior (BaseAdventurousBehavior):

    # Constructor
    # toc_sections (TOCSections) - a object that determines how the sections of the ebook are separated
    # spine - (List(SpineItem)) the current ebook's order of sections
    # setup_vscrollbar_method (method) - the method setting up the scrollbar and the position displayed in the upper left
    def __init__(self, toc_sections, spine, setup_scrollbar_method):
        BaseAdventurousBehavior.__init__(self, setup_scrollbar_method)
        self.toc_sections = toc_sections
        self.spine = spine
        self.start_spine = 1
        
    # Sets the current section of the book the user is viewing, the sections the user can view from that section,
    # and the total pages in those sections
    # curr_index (integer) - the index of the current section in the spine
    # curr_sec (SpineItem) - the current section being displayed
    def set_curr_sec(self, curr_index, curr_sec):
        super(AdventurousBehavior, self).set_curr_sec(curr_index, curr_sec)
        
        # Make sure the current section exists in the TOC
        updated_include_sections = self.toc_sections.set_curr_sec(curr_index, curr_sec)
        if (updated_include_sections):
            # Determine the part of the spine included in the sections
            self.start_spine = -1
            self.end_spine = -1
            for i in self.toc_sections.include_sections:
                if (self.start_spine == -1 or self.start_spine > i):
                    self.start_spine = i
                if (self.end_spine == -1 or self.end_spine < i):
                    self.end_spine = i
        
            # Determine the number of pages in the group of sections
            self.num_pages = self.calculate_num_pages()
            self.setup_vscrollbar_method()
        
    # Returns whether the user can move from the current section to the passed section
    # True if the passed section is in the group of sections the user can view
    # next_sec (string) - the section to check
    def allow_page_turn(self, next_sec):
        if (self.curr_sec is None):
            # The book doesn't have a bookmark with the user's last position
            # Allow returning to the beginning of the book 
            return True
        
        next_index = self.spine.index(next_sec)
        if (next_index in self.toc_sections.include_sections):            
            # Don't add an edge if the user skipped sections in the book using the scrollbar or position label
            if (next_index == self.curr_index + 1 or next_index == self.curr_index - 1):                    
                return True
                
        return False
         
    # Returns the user's position relative to the section and update the absolute position
    # Sets the new absolute position in the book
    # frac (number) - the scrollbar's position in relation to the current displayed section of the book
    def calculate_page_label(self, frac):
        section_position = super(AdventurousBehavior, self).calculate_page_label(frac)
        return ((self.curr_sec.start_page + section_position) 
                - self.spine[self.start_spine].start_page)
            
    # Returns the user's absolute position in the ebook given a position set by the scrollbar or position label
    # new_page (number) - the page to move the user to as set by the scrollbar or position label
    def update_page_label(self, user_input):
        return user_input + self.spine[self.start_spine].start_page - 1
            
    # Calculates the number of pages in the current group of sections
    def calculate_num_pages(self):      
        num_pages = 0
        num_found = 0
        spine_index = 0
        start = False
        end = False
        num_sections = len(self.toc_sections.include_sections)
        while (num_found < num_sections and end == False):
            if (spine_index in self.toc_sections.include_sections):
                start = True
                num_found = num_found + 1
                curr_path = self.spine[spine_index]
                num_pages = num_pages + curr_path.pages
            else:
                if (start == True):
                    end = True
            spine_index = spine_index + 1
        
        if (num_pages == 0):
            num_pages = 1
            
        return num_pages       
