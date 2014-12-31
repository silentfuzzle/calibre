
__license__   = 'GPL v3'
__copyright__ = '2014, Emily Palmieri <silentfuzzle@gmail.com>'

from calibre.gui2.viewer.behavior_manager.behavior_manager import BehaviorManager

# This class allows users to switch between two defined interface behaviors.
class SwitchBehaviorManager (BehaviorManager):

    # Constructor
    # set_behavior_manager_method (method) - the method to call in EBookViewer after switching interface behaviors
    # b1_page_behavior (BaseBehavior) - the main page behavior to toggle between
    # b1_toc_interface (TOCContainer) - the main TOC interface to toggle between
    # b2_page_behavior (BaseBehavior) - the second page behavior to toggle between
    # b2_toc_interface (TOCContainer) - the second TOC interface to toggle between
    def __init__(self, set_behavior_manager_method, b1_page_behavior, 
            b1_toc_interface, b2_page_behavior, b2_toc_interface):
        BehaviorManager.__init__(self, b1_page_behavior, b1_toc_interface)
        self.b1_page_behavior = b1_page_behavior
        self.b1_toc_interface = b1_toc_interface
        self.b2_page_behavior = b2_page_behavior
        self.b2_toc_interface = b2_toc_interface
        self.set_behavior_manager_method = set_behavior_manager_method
            
    # Returns the value from the current page behavior
    # b1_return (object) - the value returned by a method from the main page behavior
    # b2_return (object) - the value returned by a method from the second page behavior
    def get_return_value(self, b1_return, b2_return):
        if (self.page_behavior == self.b1_page_behavior):
            return b1_return
        else:
            return b2_return
    
    # Toggle between using the main and second interface behaviors
    # checked (bool) - True if the interface behavior switch is pressed
    def toggle_adventurous_mode(self, checked):
        if (not checked):
            new_toc_view = self.b1_toc_interface
            self.page_behavior = self.b1_page_behavior
        else:
            new_toc_view = self.b2_toc_interface
            self.page_behavior = self.b2_page_behavior
                
        # Set the new TOC interface in EBookViewer
        self.set_behavior_manager_method(checked, new_toc_view)
        
    ###########################################################################
    #BehaviorManager Methods
    ###########################################################################
    
    # Sets up the ebook for display using this behavior manager
    # number_of_pages (int) - the total number of pages in the ebook
    # main (EBookViewer) - the ebook viewer interface
    def setup_ebook(self, number_of_pages, main):
        self.b1_page_behavior.setup_ebook(number_of_pages)
        self.b2_page_behavior.setup_ebook(number_of_pages)
                    
        # Setup the interface behavior toggle button and the selected interface
        main.action_toggle_adventurous_mode.toggled[bool].connect(
                self.toggle_adventurous_mode)
        self.toggle_adventurous_mode(
                main.action_toggle_adventurous_mode.isChecked())
        
    # Sets the history offset for any network TOC interfaces
    # offset (int) - the new value of the history offset
    def set_history_offset(self, offset):
        self.b1_toc_interface.history_offset = offset
        self.b2_toc_interface.history_offset = offset
        
    # Updates the TOC scrollbar for any hierarchical TOC interfaces
    # item_index (int) - the index of the item in the hierarchy to scroll to
    def scroll_to(self, item_index):
        self.b1_toc_interface.scroll_to(item_index)
        self.b2_toc_interface.scroll_to(item_index)
        
    # Creates a connection between sections/nodes for any network TOC interfaces
    # start_sec (SpineItem) - the node/section to start the edge from
    # end_sec (string) - the node/section to end the edge at
    def update_connection(self, start_sec, end_sec):
        self.b1_toc_interface.update_connection(start_sec, end_sec)
        self.b2_toc_interface.update_connection(start_sec, end_sec)
        
    ###########################################################################
    #BaseBehavior Methods
    ###########################################################################
    
    # Returns the page number to display in the upper left
    # Sets the new absolute position in the book
    # frac (number) - the scrollbar's position in relation to the current displayed section of the book
    def get_page_label(self, frac):
        # Calculate the absolute position in both behaviors
        b1_label = self.b1_page_behavior.get_page_label(frac)
        b2_label = self.b2_page_behavior.get_page_label(frac)
            
        return self.get_return_value(b1_label, b2_label)
    
    # Returns whether the user can move from the current section to the passed section
    # next_sec (string) - the section to check
    def allow_page_turn(self, next_sec):
        # Updated sections included in a group for any Adventurous Reader behaviors
        b1_allow = self.b1_page_behavior.allow_page_turn(next_sec)
        b2_allow = self.b2_page_behavior.allow_page_turn(next_sec)
        
        # Add an edge to the network in any network TOC interfaces if needed
        curr_sec = self.page_behavior.curr_sec
        self.b1_toc_interface.check_update_connection(curr_sec, next_sec)
        self.b2_toc_interface.check_update_connection(curr_sec, next_sec)
            
        return self.get_return_value(b1_allow, b2_allow)
                
    # Sets the current section of the book the user is viewing for both behaviors
    # curr_index (integer) - the index of the current section in the spine
    # curr_sec (SpineItem) - the current section being displayed
    def set_curr_sec(self, curr_index, curr_sec):
        self.b1_page_behavior.set_curr_sec(curr_index, curr_sec)
        self.b2_page_behavior.set_curr_sec(curr_index, curr_sec)
        
        self.b1_toc_interface.update_curr_sec(curr_index, curr_sec)
        self.b2_toc_interface.update_curr_sec(curr_index, curr_sec)
        