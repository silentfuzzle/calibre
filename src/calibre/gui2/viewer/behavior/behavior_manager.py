
__license__   = 'GPL v3'
__copyright__ = '2014, Emily Palmieri <silentfuzzle@gmail.com>'

from calibre.gui2.viewer.behavior.base_behavior import BaseBehavior
from calibre.gui2.viewer.behavior.adventurous_behavior import AdventurousBehavior
from calibre.gui2.viewer.behavior.adventurous_base_behavior import BaseAdventurousBehavior
from calibre.gui2.viewer.behavior.calibre_behavior import CalibreBehavior

# This class allows users to switch between the Calibre and Adventurous Reader behaviors.
class BehaviorManager (BaseBehavior):

    # Constructor
    # number_of_pages (number) - the total pages found in the ebook
    # manager (EbookViewer) - the ebook viewer interface
    def __init__(self, number_of_pages, manager):
        BaseBehavior.__init__(self, number_of_pages)
        self.calibre_behavior = CalibreBehavior(number_of_pages)
        self.adventurous_behavior = None
        if (manager.iterator.toc):
            self.adventurous_behavior = AdventurousBehavior(
                    manager.iterator.toc, manager.iterator.spine, 
                    number_of_pages, manager.adventurous_toc_container.toc, 
                    manager.setup_vscrollbar)
        self.current_behavior = self.calibre_behavior
        self.manager = manager
        
    # Sets the page behavior currently in use
    # adventurous (boolean) - True if the Adventurous Reader behavior should be used
    def set_current_behavior(self, adventurous):
        if (adventurous):
            self.current_behavior = self.adventurous_behavior
        else:
            self.current_behavior = self.calibre_behavior
        
        # Set the vertical scrollbar position
        #self.current_behavior.goto_page(
        #    self.current_behavior.absolute_position, self.manager.goto_page)
        self.manager.setup_vscrollbar()
            
    # Sets the history offset for the correct behavior
    # offset (int) - the new value of the history offset
    def set_history_offset(self, offset):
        # Only the Adventurous Reader behavior uses history offset
        if (self.adventurous_behavior is not None):
            self.adventurous_behavior.set_history_offset(offset)
            
    # Returns the users current position in the ebook
    def get_absolute_position(self):
        return self.current_behavior.get_absolute_position()
    
    # Returns the total number of pages to display
    def get_num_pages(self):
        return self.current_behavior.get_num_pages()
        
    # Returns the page number to display in the upper left
    # Sets the new absolute position in the book
    # frac (number) - the scrollbar's position in relation to the current displayed section of the book
    def get_page_label(self, frac):
        # Calculate the absolute position in both behaviors
        c_label = self.calibre_behavior.get_page_label(frac)
        if (self.adventurous_behavior is not None):
            a_label = self.adventurous_behavior.get_page_label(frac)
            
        # Return the correct label to display
        if (self.current_behavior == self.calibre_behavior):
            return c_label
        else:
            return a_label
    
    # Returns whether the user can move from the current section to the passed section
    # next_sec (string) - the section to check
    def allow_page_turn(self, next_sec):
        # Add an edge to the network in the Adventurous Reader behavior if needed
        if (self.adventurous_behavior is not None):
            a_allow = self.adventurous_behavior.allow_page_turn(next_sec)
            
        # Return the result from the correct behavior
        if (self.current_behavior == self.adventurous_behavior):
            return a_allow
        else:
            return self.current_behavior.allow_page_turn(next_sec)
    
    # Moves the user to the passed page number as set by the scrollbar or position label, using the passed method
    # new_page (number) - the page to move the user to
    # goto_page_method (method) - the method to use to move with
    def goto_page(self, new_page, goto_page_method):
        return self.current_behavior.goto_page(new_page, goto_page_method)
    
    # Sets the current section of the book the user is viewing for both behaviors
    # curr_index (integer) - the index of the current section in the spine
    # curr_sec (SpineItem) - the current section being displayed
    def set_curr_sec(self, curr_index, curr_sec):
        if (self.adventurous_behavior is not None):
            self.adventurous_behavior.set_curr_sec(curr_index, curr_sec)
        self.calibre_behavior.set_curr_sec(curr_index, curr_sec)
    
    # Pass any clicked links to the Adventurous Reader behavior for processing
    # path (string) - the path in the ebook the link pointed to
    def link_clicked(self, path):
        if (self.adventurous_behavior is not None):
            self.adventurous_behavior.link_clicked(path)
    
    # Pass any changes to the history to the Adventurous Reader behavior for processing
    # history_offset (int) - An integer representing how the user navigated to the section
    #      0 - the user clicked a link in the e-book or a node in the network
    #      1 - the user navigated to the next section in their history
    #      -1 - the user navigated to the previous section in their history
    #      -2 - the user navigated to another section without adding to their history
    def update_history(self):
        if (self.adventurous_behavior is not None):
            self.adventurous_behavior.update_history()