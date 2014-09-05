
__license__   = 'GPL v3'
__copyright__ = '2014, Emily Palmieri <silentfuzzle@gmail.com>'
__docformat__ = 'restructuredtext en'

import abc

class BaseBehavior (object):
    PAGE_STEP = 100.
    
    def __init__(self, number_of_pages):
        self.absolute_position = 1.
        self.num_pages = number_of_pages

    @abc.abstractmethod
    def get_page_label(self, frac):
        return
    
    @abc.abstractmethod
    def allow_page_turn(self, next_sec):
        return
        
    @abc.abstractmethod
    def get_section_pages(self, sec):
        return
        
    @abc.abstractmethod
    def check_pages(self, new_page, page):
        return
    
    @abc.abstractmethod
    def get_num_pages(self):
        return
        
    @abc.abstractmethod
    def goto_page(self, user_input, goto_page_method):
        return
    
    def set_curr_sec(self, curr_index, curr_sec):
        print ("Base curr_sec set")
        self.curr_sec = curr_sec
        self.curr_index = curr_index
        
    def link_clicked(self, path):
        return