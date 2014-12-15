
__license__   = 'GPL v3'
__copyright__ = '2014, Emily Palmieri <silentfuzzle@gmail.com>'

from calibre.gui2.viewer.behavior.base_behavior import BaseBehavior

# This class defines an Adventurous Reader behavior where users can only view one section of the ebook at a time.
class BaseAdventurousBehavior (BaseBehavior):

    ###########################################################################
    #PAGE BEHAVIOR DEFINITION
    ###########################################################################
    
    # Constructor
    # toc - (calibre.ebooks.metadata.toc.TOC) the current ebook's TOC
    # spine - (List(SpineItem)) the current ebook's ordering of sections
    # default_number_of_pages (number) - the total number of pages in the ebook
    # toc_view (TOCNetworkView) - the interface displaying the ebook's network of sections
    # setup_vscrollbar_method (method) - the method setting up the scrollbar and the position displayed in the upper left
    def __init__(self, toc, spine, default_number_of_pages, toc_view, setup_vscrollbar_method):
        BaseBehavior.__init__(self, default_number_of_pages)
        self.toc = toc
        self.spine = spine
        self.setup_vscrollbar_method = setup_vscrollbar_method
        
        # Setup the interface view of the TOC
        self.toc_view = toc_view
        self.history_offset = 0
        
    # Sets the current section of the book the user is viewing
    # and the number of pages in that section
    # curr_index (integer) - the index of the current section in the spine
    # curr_sec (SpineItem) - the current section being displayed
    def set_curr_sec(self, curr_index, curr_sec):
        if (self.curr_sec != curr_sec):
            super(BaseAdventurousBehavior, self).set_curr_sec(curr_index, curr_sec)
            self.num_pages = curr_sec.pages
        
        # Only setup the scrollbar and position label if this object is an instance of this class
        if (type(self) is BaseAdventurousBehavior):
            self.setup_vscrollbar_method()
            self.update_network_pos(curr_sec)
        
    # Returns whether the user can move from the current section to the passed section
    # next_sec (string) - the section to check
    def allow_page_turn(self, next_sec):
        if (self.curr_sec is None):
            # The book doesn't have a bookmark with the user's last position
            # Allow returning to the beginning of the book 
            return True
        
        return False

    # Returns the user's position relative to the current section
    # Sets the new absolute position in the book
    # frac (number) - the scrollbar's position in relation to the current displayed section of the book
    def get_page_label(self, frac):
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
        
    # When a link is clicked in the ebook, add an edge to the ebook network
    # path (string) - the path in the ebook the link pointed to
    def link_clicked(self, path):
        self.add_network_edge(self.curr_sec, path)
        return
        
    ###########################################################################
    #NETWORK TOC UPKEEP
    ###########################################################################
    
    # Adds an edge to the ebook network
    # start_sec (SpineItem) - the node/section to start the edge from
    # end_sec (string) - the node/section to end the edge at
    # start_sec_checked (boolean) - true if the passed start section was already checked for existence in the ebook's TOC
    def add_network_edge(self, start_sec, end_sec, start_sec_checked=False):
        # Get the TOC and SpineItem entries for the passed end section
        end_toc, corrected_end_sec = self.check_and_get_toc(end_sec)
        
        if (start_sec_checked == False):
            # Get the TOC and SpineItem entries for the passed start section
            start_toc, start_sec = self.check_and_get_toc(start_sec)
        
        # Add an edge to the network
        if (corrected_end_sec != start_sec):
            self.toc_view.add_edge(start_sec, corrected_end_sec)
                
    # Update the user's position and history in the network view
    # curr_sec (SpineItem) - the current section the user is viewing
    def update_network_pos(self, curr_sec):
        self.toc_view.set_curr_page(curr_sec.start_page, self.history_offset)
        self.history_offset = -2
        
    # Perform any required actions after the history is modified
    def update_history(self):
        self.update_network_pos(self.curr_sec)
    
    # Return a section's TOC and SpineItem entries if it exists in the TOC
    # Return the section's parent's TOC and SpineItem entries if it doesn't exist in the TOC
    # path_sec (string) - the section of the ebook to find the SpineItem and TOC for
    def check_and_get_toc(self, path_sec):
        # Attempt to get the section's TOC entry
        path_toc = self.get_in_toc(path_sec, self.toc)
        corrected_path_sec = path_sec
        
        if (path_toc is None):
            # Get the TOC entry of the section's parent
            path_toc = self.get_non_toced_parent(self.spine.index(path_sec))
            
            # Get the SpineItem of the section's parent
            corrected_path_sec = self.spine[self.spine.index(path_toc.abspath)]
        
        return (path_toc, corrected_path_sec)
            
    # Returns the TOC entry of a section's parent
    # A section's parent is the nearest previous section in the ebook's spine that exists in the TOC
    # If such a section doesn't exist, it is the nearest next section in the book's spine that exists in the TOC
    # current_index (integer) - location of the section in the spine or the previous location checked
    # back (boolean) - true if the previous section from the current index should be checked
    def get_non_toced_parent(self, current_index, back=True):
        check_in_toc_index = current_index - 1
        if (back == False):
            check_in_toc_index = current_index + 1
            
        if (check_in_toc_index < 0):
            # The beginning of the ebook was passed, check the next sections in the following recusive calls
            back = False
        else:
            curr_toc = self.get_in_toc(self.spine[check_in_toc_index], self.toc)
            if (curr_toc is not None):
                return curr_toc
        
        return self.get_non_toced_parent(check_in_toc_index, back)
        
    # Returns the TOC entry of a section if it exists in the TOC
    # Returns None if the passed section doesn't exist in the TOC
    # page (string) - the full path to the section of the ebook to check
    # toc - (calibre.ebooks.metadata.toc.TOC) the current ebook's TOC
    def get_in_toc(self, page, toc):
        for t in toc.flat():
            if (page == t.abspath):
                return t
        return None
         
            