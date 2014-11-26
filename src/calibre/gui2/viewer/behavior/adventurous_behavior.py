
__license__   = 'GPL v3'
__copyright__ = '2014, Emily Palmieri <silentfuzzle@gmail.com>'

from sets import Set
from calibre.gui2.viewer.behavior.adventurous_base_behavior import BaseAdventurousBehavior

# This class defines an Adventurous Reader behavior where users can view a group of sections at a time. This group includes sub-sections
# and adjacent sections not included in the TOC.
class AdventurousBehavior (BaseAdventurousBehavior):

    ###########################################################################
    #PAGE BEHAVIOR DEFINITION
    ###########################################################################

    # Constructor
    # toc - (calibre.ebooks.metadata.toc.TOC) the current ebook's TOC
    # spine - (List(SpineItem)) the current ebook's order of sections
    # default_number_of_pages (number) - the total number of pages in the ebook
    # title (string) - the title of the ebook
    # pathtoebook (string) - the full path to the ebook on the user's file system
    # toc_view (TOCNetworkView) - the interface displaying the ebook's network of sections
    # setup_vscrollbar_method (method) - the method setting up the scrollbar and the position displayed in the upper left
    def __init__(self, toc, spine, default_number_of_pages, title, pathtoebook, toc_view, setup_scrollbar_method):
        BaseAdventurousBehavior.__init__(self, toc, spine, default_number_of_pages, title, pathtoebook, toc_view, setup_scrollbar_method)
        self.include_sections = Set()
        
    # Sets the current section of the book the user is viewing, the sections the user can view from that section,
    # and the total pages in those sections
    # curr_index (integer) - the index of the current section in the spine
    # curr_sec (SpineItem) - the current section being displayed
    def set_curr_sec(self, curr_index, curr_sec):
        super(AdventurousBehavior, self).set_curr_sec(curr_index, curr_sec)
        
        # Make sure the current section exists in the TOC
        curr_toc, self.corrected_curr_sec = self.check_and_get_toc(curr_sec)
        self.update_network_pos(self.corrected_curr_sec)
        
        if (curr_index not in self.include_sections):
            # Determine the sections to include in the group if the user moved outside the previous group
            self.include_sections = self.find_include_sections(curr_toc)
            
            # Determine the part of the spine included in the sections
            self.start_spine = -1
            self.end_spine = -1
            for i in self.include_sections:
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
        if (next_index in self.include_sections):            
            # Don't add an edge if the user skipped sections in the book using the scrollbar or position label
            if (next_index == self.curr_index + 1 or next_index == self.curr_index - 1):
                self.add_network_edge(self.corrected_curr_sec, next_sec, True)
                    
                return True
                
        return False
         
    # Returns the user's position relative to the number of pages in the section group
    # Sets the new absolute position in the book
    # frac (number) - the scrollbar's position in relation to the current displayed section of the book
    def get_page_label(self, frac):
        section_position = super(AdventurousBehavior, self).get_page_label(frac)
        return (self.curr_sec.start_page + section_position) - self.spine[self.start_spine].start_page
            
    # Returns the user's absolute position in the ebook given a position set by the scrollbar or position label
    # new_page (number) - the page to move the user to as set by the scrollbar or position label
    def update_page_label(self, user_input):
        return user_input + self.spine[self.start_spine].start_page - 1

    ###########################################################################
    #SECTION GROUP UPKEEP
    ###########################################################################
            
    # Calculates the number of pages in the current group of sections
    def calculate_num_pages(self):      
        num_pages = 0
        num_found = 0
        spine_index = 0
        start = False
        end = False
        num_sections = len(self.include_sections)
        while (num_found < num_sections and end == False):
            if (spine_index in self.include_sections):
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
     
    # Returns the sections to include in this group of sections
    # curr_toc (calibre.ebooks.metadata.toc.TOC) - the TOC entry of the current section
    def find_include_sections(self, curr_toc):
        include_sections = Set()
        
        # Include the root of the TOC tree with this section and all TOC entries in it
        curr_parent = curr_toc
        while (curr_parent.parent.parent is not None):
            curr_parent = curr_parent.parent
            
        for t in curr_parent.flat():
            include_sections.add(t.abspath)
        
        # Determine where to check for sections that aren't in the toc
        in_toc = Set()
        spine_len = len(self.spine)
        for s in include_sections:
            spine_index = self.spine.index(s)
            in_toc.add(spine_index)
        
        # Include adjacent sections that aren't in the toc
        in_toc = self.search_in_toc(0, 0, in_toc)
        return in_toc
        
    # Find adjacent sections in the spine that aren't in the TOC that should be included in the section group
    # index (integer) - the index to search from
    # num_found (integer) - the number of entries in the section group that were found in this recursive search
    # in_toc (List(integer)) - the indicies of the sections included in the section group
    # found_first_toc_entry (boolean) - whether the first section in the TOC has been found yet
    def search_in_toc(self, index, num_found, in_toc, found_first_toc_entry=False):
        next_index = index + 1
        
        if (index not in in_toc):
            # Check if the first section in the toc has been found
            page_in_toc = self.get_in_toc(self.spine[index], self.toc)
            if (found_first_toc_entry == False):
                if (page_in_toc is not None):
                    found_first_toc_entry = True
                    
            # Add this section if the previous section is in the included sections
            # and this section isn't in the toc
            if (index - 1 in in_toc):
                if (page_in_toc is None):
                    in_toc.add(index)
                
            # Only check the next section if not all the sections included in the toc have been found
            if (next_index < len(self.spine) and num_found < len(in_toc)):
                in_toc = self.search_in_toc(next_index, num_found, in_toc, found_first_toc_entry)
        else:
            # Include all sections not included in the toc at the beginning of the book
            if (found_first_toc_entry == False):
                found_first_toc_entry = True
                i = index - 1
                while (i >= 0):
                    in_toc.add(i)
                    
                    i = i - 1
                    
            num_found = num_found + 1
            
            # Always check the section after the last included in the toc
            if (next_index < len(self.spine)):
                in_toc = self.search_in_toc(next_index, num_found, in_toc, found_first_toc_entry)
            
        return in_toc         
