
__license__   = 'GPL v3'
__copyright__ = '2014, Emily Palmieri <silentfuzzle@gmail.com>'
__docformat__ = 'restructuredtext en'

from calibre.gui2.viewer.behavior.base_behavior import BaseBehavior
from calibre.gui2.viewer.book_network import EBookNetwork

class BaseAdventurousBehavior (BaseBehavior):
    def __init__(self, toc, spine, default_number_of_pages, title, pathtoebook, toc_view, setup_vscrollbar_method):
        BaseBehavior.__init__(self, default_number_of_pages)
        self.toc = toc
        self.spine = spine
        self.setup_vscrollbar_method = setup_vscrollbar_method
        
        self.toc_view = toc_view
        self.ebook_network = EBookNetwork(spine, toc, title, pathtoebook)
        self.toc_view.load_network(self.ebook_network.data)
        
    def allow_page_turn(self, next_sec):
        print ("allow_page_turn")
        return False
        
    def set_curr_sec(self, curr_index, curr_sec):
        print ("AdventurousBase curr_sec set")
        super(BaseAdventurousBehavior, self).set_curr_sec(curr_index, curr_sec)
        self.num_pages = curr_sec.pages
        
        if (type(self) is BaseAdventurousBehavior):
            print ("BaseAdventurous set scrollbar")
            self.setup_vscrollbar_method()
        
        
        
    def add_network_edge(self, start_sec, end_sec, start_sec_checked=False):
        end_toc, corrected_end_sec = self.check_and_get_toc(end_sec)
        
        if (start_sec_checked == False):
            start_toc, start_sec = self.check_and_get_toc(start_sec)
        
        if (corrected_end_sec != start_sec):
            edge_added = self.ebook_network.add_edge(start_sec.start_page, corrected_end_sec.start_page)
        
            if (edge_added):
                self.toc_view.load_network(self.ebook_network.data)
            
    def check_and_get_toc(self, path_sec):
        path_toc = self.get_in_toc(path_sec, self.toc)
        corrected_path_sec = path_sec
        if (path_toc is None):
            path_toc = self.get_non_toced_parent(self.spine.index(path_sec))
            corrected_path_sec = self.spine[self.spine.index(path_toc.abspath)]
        
        return (path_toc, corrected_path_sec)
            
    def get_non_toced_parent(self, current_index, back=True):
        check_in_toc_index = current_index - 1
        if (back == False):
            check_in_toc_index = current_index + 1
            
        if (check_in_toc_index < 0):
            back = False
        else:
            curr_toc = self.get_in_toc(self.spine[check_in_toc_index], self.toc)
            if (curr_toc is not None):
                return curr_toc
        
        return self.get_non_toced_parent(check_in_toc_index, back)
        
    def get_in_toc(self, page, toc):
        for t in toc.flat():
            if (page == t.abspath):
                return t
        return None
         

         
    def get_page_label(self, frac):
        section_position = frac*float(self.get_section_pages(self.curr_sec))
        self.absolute_position = self.curr_sec.start_page + section_position
        print (self.absolute_position)
        return section_position + 1
            
    def update_page_label(self, user_input):
        return user_input + self.curr_sec.start_page - 1
            
    def get_section_pages(self, sec):
        if (sec.pages == 1):
            return 0.8
        else:
            return sec.pages-1
            
    def goto_page(self, new_page, goto_page_method):
        abs_pos = self.update_page_label(new_page)
        goto_page_method(abs_pos, allow_page_turn=False)
        
    def check_pages(self, new_page, page):
        return (new_page >= page.start_page and new_page < page.max_page + 1)
        
    def link_clicked(self, path):
        self.add_network_edge(self.curr_sec, path)
        return
            