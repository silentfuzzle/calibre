
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
            
    # Return a page behavior given if the current ebook should be display in a single document
    # single_document (bool) - True if the page behavior should display all the book's text in a single document
    # toc_sections (TOCSections) - an object defining how the sections of the book in the toc are separated into groups
    # spine (List(SpineItem)) - the list of sections in the book
    # setup_vscrollbar_method (method) - the method from EBookViewer to use when updating the scrollbar and page numbers
    def get_page_behavior(self, single_document, toc_sections, spine, 
            setup_vscrollbar_method):
        if (single_document):
            # Display the book in a single document
            page_behavior = CalibreBehavior()
        else:
            # Break the book into groups and display each group as a separate document
            page_behavior = AdventurousBehavior(toc_sections, 
                    spine, setup_vscrollbar_method)
        return page_behavior
                
    # Return a TOC interface given if it should be displayed as a network or a hierarchy
    # use_hierarchy (bool) - True if the TOC interface should display the TOC in a hierarchy
    # toc_sections (TOCSections) - an object defining how the sections of the book in the toc are separated into groups
    # title (string) - the title of the book
    # pathtoebook (string) - the path to the ebook on the user's file system
    # main (EBookViewer) - the ebook viewer interface
    def get_toc_interface(self, use_hierarchy, toc_sections, title, 
            pathtoebook, main):
        if (use_hierarchy):
            # Display the ebook's TOC as a hierarchy of sections
            toc_container = TreeTOCContainer(main)
            toc_container.setup_ebook(main.toc_model)
            toc_container.connect_toc_actions(main.toc_clicked)
        else:
            # Display the ebook's TOC as a network of sections
            toc_container = NetworkTOCContainer(main)
            toc_container.setup_ebook(main.iterator.spine, main.iterator.toc, 
                    toc_sections, title, pathtoebook)
        return toc_container
        
    # Returns a behavior manager from the given parameters
    # main (EBookViewer) - the ebook viewer interface
    # number_of_pages (int) - the total number of pages in the ebook
    # title (string) - the title of the ebook
    # pathtoebook (string) - the path to the ebook on the user's file system
    def build_behavior_manager(self, main, number_of_pages, title, pathtoebook):
        toc = main.iterator.toc
        spine = main.iterator.spine
        toc_sections = TOCSections(toc, spine)
        
        # If there isn't a TOC, display the ebook in a single document with a
        # hierarchical TOC interface at all times
        if (not toc):
            self.switch = False
            self.b1_single_document = True
            self.b1_use_hierarchy = True
            
        # Create the main interface behavior
        b1_page_behavior = self.get_page_behavior(self.b1_single_document, 
                toc_sections, spine, main.setup_vscrollbar)
        b1_toc_interface = self.get_toc_interface(
                self.b1_use_hierarchy, toc_sections, title, pathtoebook, main)
        
        if (self.switch):
            # Create the second interface behavior if specified
            b2_page_behavior = self.get_page_behavior(self.b2_single_document,
                    toc_sections, spine, main.setup_vscrollbar)
            b2_toc_interface = self.get_toc_interface(
                    self.b2_use_hierarchy, toc_sections, title, pathtoebook, 
                    main)
            
            # Create a behavior manager to switch between the main and second behavior
            behavior_manager = SwitchBehaviorManager(
                    main.set_behavior_manager, b1_page_behavior, 
                    b1_toc_interface, b2_page_behavior, 
                    b2_toc_interface)
        else:
            # Disable the behavior toggle
            main.action_toggle_adventurous_mode.setVisible(False)
            behavior_manager = BehaviorManager(b1_page_behavior, 
                    b1_toc_interface)
        
        behavior_manager.setup_ebook(number_of_pages, main)
        return behavior_manager
        