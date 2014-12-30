
__license__   = 'GPL v3'
__copyright__ = '2014, Emily Palmieri <silentfuzzle@gmail.com>'

from calibre.gui2.viewer.behavior.base_behavior import BaseBehavior
from calibre.gui2.viewer.behavior.adventurous_behavior import AdventurousBehavior
from calibre.gui2.viewer.behavior.adventurous_base_behavior import BaseAdventurousBehavior
from calibre.gui2.viewer.behavior.calibre_behavior import CalibreBehavior
from calibre.gui2.viewer.toc_sections import TOCSections

# This class allows users to switch between the Calibre and Adventurous Reader behaviors.
class BehaviorManager (BaseBehavior):

    # Constructor
    # number_of_pages (number) - the total pages found in the ebook
    # manager (EbookViewer) - the ebook viewer interface
    # toc_sections (TOCSections) - a object that determines how the sections of the ebook are grouped
    def __init__(self, number_of_pages, manager, toc_sections):
        BaseBehavior.__init__(self, number_of_pages)
        self.calibre_behavior = CalibreBehavior(number_of_pages)
        self.adventurous_behavior = None
        if (manager.iterator.toc):
            if (toc_sections is None):
                toc_sections = TOCSections(manager.iterator.toc, manager.iterator.spine)
            self.adventurous_behavior = AdventurousBehavior(
                    toc_sections, manager.iterator.spine, 
                    number_of_pages, manager.setup_vscrollbar)
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
        self.manager.setup_vscrollbar()
        self.manager.set_vscrollbar_value(self.current_behavior.last_label)
            
    # Sets the history offset for the correct behavior
    # offset (int) - the new value of the history offset
    def set_history_offset(self, offset):
        if (self.adventurous_behavior is not None):
            self.manager.adventurous_toc_container.history_offset = offset
            
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
            self.manager.adventurous_toc_container.check_add_network_edge(
                    self.current_behavior.curr_sec, next_sec)
            
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
        self.calibre_behavior.set_curr_sec(curr_index, curr_sec)
        if (self.adventurous_behavior is not None):
            self.adventurous_behavior.set_curr_sec(curr_index, curr_sec)
            self.manager.adventurous_toc_container.update_network_pos()