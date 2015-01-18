
__license__   = 'GPL v3'
__copyright__ = '2014, Emily Palmieri <silentfuzzle@gmail.com>'

from calibre.gui2.viewer.behavior.adventurous_behavior import AdventurousBehavior
from calibre.gui2.viewer.behavior.adventurous_base_behavior import BaseAdventurousBehavior
from calibre.gui2.viewer.behavior.calibre_behavior import CalibreBehavior
from calibre.gui2.viewer.toc_sections import TOCSections
from calibre.gui2.viewer.behavior_manager.behavior_manager import BehaviorManager
from calibre.gui2.viewer.behavior_manager.behavior_manager_switch import SwitchBehaviorManager
from calibre.gui2.viewer.toc_container.toc_hierarchy_container import TreeTOCContainer
from calibre.gui2.viewer.toc_container.toc_network_container import NetworkTOCContainer

# This class builds the TOC interface(s) and page numbering behavior(s) to use in the ebook viewer interface
class BehaviorManagerBuilder (object):

    # Constructor
    # main (EBookViewer) - the ebook viewer interface
    # b1_single_document (bool) - True if the main page behavior should display all the book's text in a single document
    # b1_use_hierarchy (bool) - True if the main TOC interface should display the TOC in a hierarchy
    # switch (bool) - True if the user can switch between two ebook viewer behaviors
    # b2_single_document (bool) - True if the second page behavior should display all the book's text in a single document
    # b2_use_hierarchy (bool) - True if the second TOC interface should display the TOC in a hierarchy
    def __init__(self, main, b1_single_document=True, 
            b1_use_hierarchy=True, switch=False, b2_single_document=False, 
            b2_use_hierarchy=False):
            
        # If both interface behaviors are the same, don't create a switch between the two
        if (b1_single_document == b2_single_document and
                b1_use_hierarchy == b2_use_hierarchy):
            switch = False
                
        self.b1_single_document = b1_single_document
        self.b1_use_hierarchy = b1_use_hierarchy
        self.switch = switch
        self.b2_single_document = b2_single_document
        self.b2_use_hierarchy = b2_use_hierarchy
        
        # Create a default TOC interface to use until the user selects an ebook
        self.default_manager = BehaviorManager(CalibreBehavior(), 
                TreeTOCContainer(main))
        self.network_container = NetworkTOCContainer(main)
            
    # Return a page behavior given if the current ebook should be display in a single document
    # single_document (bool) - True if the page behavior should display all the book's text in a single document
    # setup_vscrollbar_method (method) - the method from EBookViewer to use when updating the scrollbar and page numbers
    def get_page_behavior(self, single_document, setup_vscrollbar_method):
        if (single_document):
            # Display the book in a single document
            page_behavior = CalibreBehavior()
        else:
            # Break the book into groups and display each group as a separate document
            page_behavior = AdventurousBehavior(setup_vscrollbar_method)
        return page_behavior
                
    # Return a TOC interface given if it should be displayed as a network or a hierarchy
    # use_hierarchy (bool) - True if the TOC interface should display the TOC in a hierarchy
    # main (EBookViewer) - the ebook viewer interface
    def get_toc_interface(self, use_hierarchy, main):
        if (use_hierarchy):
            # Display the ebook's TOC as a hierarchy of sections
            toc_container = TreeTOCContainer(main)
            toc_container.connect_toc_actions(main.toc_clicked)
        else:
            # Display the ebook's TOC as a network of sections
            toc_container = self.network_container
        return toc_container
        
    # Returns a behavior manager from the given parameters
    # main (EBookViewer) - the ebook viewer interface
    def build_behavior_manager(self, main):
        
        # Create the main interface behavior
        b1_page_behavior = self.get_page_behavior(self.b1_single_document, 
                main.setup_vscrollbar)
        b1_toc_interface = self.get_toc_interface(
                self.b1_use_hierarchy, main)
        
        if (self.switch):
            # Create the second interface behavior if specified
            b2_page_behavior = self.get_page_behavior(self.b2_single_document,
                    main.setup_vscrollbar)
            b2_toc_interface = self.get_toc_interface(
                    self.b2_use_hierarchy, main)
            
            # Create a behavior manager to switch between the main and second behavior
            behavior_manager = SwitchBehaviorManager(
                    main, b1_page_behavior, 
                    b1_toc_interface, b2_page_behavior, 
                    b2_toc_interface)
        else:
            # Disable the behavior toggle
            main.action_toggle_adventurous_mode.setVisible(False)
            behavior_manager = BehaviorManager(b1_page_behavior, 
                    b1_toc_interface)
        
        self.behavior_manager = behavior_manager
        return behavior_manager

    # main (EBookViewer) - the ebook viewer interface
    # title (string) - the title of the ebook
    # pathtoebook (string) - the path to the ebook on the user's file system
    def setup_behavior_manager(self, main, title, pathtoebook):
        toc = main.iterator.toc
        toc_sections = None
    
        # If there isn't a TOC, display the ebook in a single document with a
        # hierarchical TOC interface at all times
        if (not toc):
            main.action_toggle_adventurous_mode.setEnabled(False)
            behavior_manager = self.default_manager
        else:
            main.action_toggle_adventurous_mode.setEnabled(True)
            behavior_manager = self.behavior_manager
            toc_sections = TOCSections(toc, main.iterator.spine)
        
        total_num_pages = sum(main.iterator.pages)
        behavior_manager.setup_ebook(total_num_pages, toc_sections, main.toc_model, title, 
                pathtoebook)
               
        # Return the behavior manager to use if it has changed
        return behavior_manager
