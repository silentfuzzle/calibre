
__license__   = 'GPL v3'
__copyright__ = '2014, Emily Palmieri <silentfuzzle@gmail.com>'
__docformat__ = 'restructuredtext en'

class BaseAdventurousBehavior (object):
    def __init__(self, toc, spine, ebook_network):
        self.toc = toc
        self.spine = spine
        self.ebook_network = ebook_network
        
    def set_curr_sec(self, curr_index, curr_sec, toc_view):
        self.curr_sec = curr_sec
        self.curr_index = curr_index
        self.toc_view = toc_view
        
    def allow_page_turn(self, next_sec):
        print ("allow_page_turn")
        return False
                
    def get_num_pages(self):
        return self.calculate_num_pages(self.curr_sec)
            
    def calculate_num_pages(self, curr_sec):
        num_pages = curr_sec.pages
        return num_pages
        
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
        return frac*float(self.get_section_pages(self.curr_sec)) + 1
            
    def update_page_label(self, userInput):
        return userInput + self.curr_sec.start_page
            
    def get_section_pages(self, curr_sec):
        if (curr_sec.pages == 1):
            return 0.8
        else:
            return curr_sec.pages-1
            
    def get_scrollbar_frac(self, new_page):
        print (new_page)
        return new_page+self.curr_sec.start_page-1
            