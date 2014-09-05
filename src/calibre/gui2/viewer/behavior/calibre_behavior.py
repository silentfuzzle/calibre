
__license__   = 'GPL v3'
__copyright__ = '2014, Emily Palmieri <silentfuzzle@gmail.com>'
__docformat__ = 'restructuredtext en'

from calibre.gui2.viewer.behavior.base_behavior import BaseBehavior

class CalibreBehavior (BaseBehavior):
        
    def get_page_label(self, frac):
        self.absolute_position = self.curr_sec.start_page + frac*float(self.curr_sec.pages-1)
        return self.absolute_position
        
    def allow_page_turn(self, next_sec):
        return True
        
    #def get_section_pages(self, sec):
        #return sec.pages-1
        
    #def check_pages(self, new_page, page):
        #return (new_page >= page.start_page and new_page <= page.max_page)
        
    def goto_page(self, user_input, goto_page_method):
        goto_page_method(user_input)
        
    def get_num_pages(self):
        return self.num_pages
        