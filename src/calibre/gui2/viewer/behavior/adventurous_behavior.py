
__license__   = 'GPL v3'
__copyright__ = '2014, Emily Palmieri <silentfuzzle@gmail.com>'
__docformat__ = 'restructuredtext en'

from sets import Set
from calibre.gui2.viewer.behavior.adventurous_base_behavior import BaseAdventurousBehavior

class AdventurousBehavior (BaseAdventurousBehavior):
    def __init__(self, toc, spine, ebook_network):
        BaseAdventurousBehavior.__init__(self, toc, spine, ebook_network)
        self.include_sections = Set()
        
    def set_curr_sec(self, curr_index, curr_sec, toc_view):
        super(AdventurousBehavior, self).set_curr_sec(curr_index, curr_sec, toc_view)
        
        print ("set curr_sec ")
        curr_toc, self.corrected_curr_sec = self.check_and_get_toc(curr_sec)
        if (curr_sec not in self.include_sections):
            parent_set = self.get_parent_set(curr_index, curr_toc)
            self.include_sections, in_toc = self.find_include_sections(parent_set)
            
            self.start_spine = -1
            self.end_spine = -1
            for i in in_toc:
                if (self.start_spine == -1 or self.start_spine > i):
                    self.start_spine = i
                if (self.end_spine == -1 or self.end_spine < i):
                    self.end_spine = i
        
        self.num_pages = self.calculate_num_pages(self.curr_sec)
        
    def allow_page_turn(self, next_sec):
        print ("allow_page_turn")
        if (self.curr_sec != next_sec):
            if (next_sec in self.include_sections):
                next_index = self.spine.index(next_sec)
                if (next_index == self.curr_index + 1 or next_index == self.curr_index - 1):
                    self.add_network_edge(self.corrected_curr_sec, next_sec, True)
                return True
            else:
                print ("False")
                return False
                
    def get_num_pages(self):
        if (self.curr_sec in self.include_sections):
            return self.num_pages
        else:
            return calculate_num_pages(self.curr_sec)
            
    def calculate_num_pages(self, curr_sec):      
        num_pages = 0
        num_found = 0
        spine_index = 0
        start = False
        end = False
        num_sections = len(self.include_sections)
        while (num_found < num_sections and end == False):
            curr_path = self.spine[spine_index]
            if (curr_path in self.include_sections):
                start = True
                num_found = num_found + 1
                num_pages = num_pages + curr_path.pages
            else:
                if (start == True):
                    end = True
            spine_index = spine_index + 1
        
        if (num_pages == 0):
            num_pages = 1
            
        return num_pages
     
    def find_include_sections(self, parent_set):
        include_sections = Set()
        
        # Include the parent sections and all their children
        for p in parent_set:
            include_sections = self.find_include_sub_sections(p, include_sections)
        
        # Include the parent section if it has no children
        if (len(include_sections) == 0 and len(parent_set) > 0):
            include_sections.add(parent_set[0].abspath)
        
        # Determine where to check for sections that aren't in the toc
        in_toc = Set()
        spine_len = len(self.spine)
        for s in include_sections:
            spine_index = self.spine.index(s)
            in_toc.add(spine_index)
        
        # Include adjacent sections that aren't in the toc
        include_sections, in_toc = self.search_in_toc(0, 0, in_toc, include_sections)
        return include_sections, in_toc
            
    def find_include_sub_sections(self, toc, include_sections):
        if (len(toc) > 0):
            include_sections.add(toc.abspath)
            
        for t in toc:
            include_sections.add(t.abspath)
            include_sections = self.find_include_sub_sections(t, include_sections)
        return include_sections
        
    def search_in_toc(self, index, num_found, in_toc, include_sections, found_first_toc_entry=False):
        next_index = index + 1
        
        if (index not in in_toc):
            # Check if the first section in the toc has been found
            page_in_toc = None
            if (found_first_toc_entry == False):
                page_in_toc = self.get_in_toc(self.spine[index], self.toc)
                if (page_in_toc is not None):
                    found_first_toc_entry = True
                    
            # Add this section if it isn't in the toc and is adjacent to a section in the tree that is
            if (index - 1 in in_toc):
                if (page_in_toc is None):
                    page_in_toc = self.get_in_toc(self.spine[index], self.toc)
                    
                if (page_in_toc is None):
                    include_sections.add(self.spine[index])
                    in_toc.add(index)
                
            # Only check the next section if not all the sections included in the toc have been found
            if (next_index < len(self.spine) and num_found < len(in_toc)):
                include_sections, in_toc = self.search_in_toc(next_index, num_found, in_toc, include_sections, found_first_toc_entry)
        else:
            # Include all sections not included in the toc at the beginning of the book
            if (found_first_toc_entry == False):
                found_first_toc_entry = True
                i = index - 1
                while (i >= 0):
                    include_sections.add(self.spine[i])
                    in_toc.add(i)
                    
                    i = i - 1
                    
            num_found = num_found + 1
            
            # Always check the section after the last included in the toc
            if (next_index < len(self.spine)):
                include_sections, in_toc = self.search_in_toc(next_index, num_found, in_toc, include_sections, found_first_toc_entry)
            
        return include_sections, in_toc
        
    def get_parent_set(self, current_index, curr_toc):            
        parent_set = []
        curr_parent = curr_toc
        while (curr_parent is not None):
            if (curr_parent.parent is not None):
                parent_set.append(curr_parent)
            curr_parent = curr_parent.parent
        
        return parent_set
         

         
    def get_page_label(self, frac):
        return (self.curr_sec.start_page + frac*float(self.get_section_pages(self.curr_sec))+1) - self.spine[self.start_spine].start_page
            
    def update_page_label(self, userInput):
        return userInput + self.spine[self.start_spine].start_page - 1
            
    def get_scrollbar_frac(self, new_page):
        print (new_page)
        return new_page+self.spine[self.start_spine].start_page-1
        