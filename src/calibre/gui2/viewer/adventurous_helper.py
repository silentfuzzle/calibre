from sets import Set

class AdventurousHelper (object):
    def __init__(self, allow_sub_sections, toc, spine, ebook_network):
        self.allow_sub_sections = allow_sub_sections
        self.toc = toc
        self.spine = spine
        self.ebook_network = ebook_network
        self.include_sections = Set()
        
    def set_curr_sec(self, curr_index, curr_sec, toc_view):
        self.curr_sec = curr_sec
        
        if (curr_sec not in self.include_sections):
            curr_toc, self.corrected_curr_sec = self.check_and_get_toc(curr_sec)
            parent_set = self.get_parent_set(curr_index, curr_toc)
            self.include_sections, in_toc = self.find_include_sections(parent_set)
            
            self.start_spine = -1
            self.end_spine = -1
            for i in in_toc:
                if (self.start_spine == -1 or self.start_spine > i):
                    self.start_spine = i
                if (self.end_spine == -1 or self.end_spine < i):
                    self.end_spine = i
            print ("Start index: " + str(self.start_spine))
            print ("End index: " + str(self.end_spine))
        
        self.num_pages = self.calculate_num_pages(self.curr_sec)
        
    def get_allow_page_turn(self, curr_index, next_sec, toc_view, add_edge):
        return self.allow_page_turn(next_sec, toc_view, add_edge)
        
    def allow_page_turn(self, next_sec, toc_view, add_edge):
        print ("allow_page_turn " + next_sec)
        if (self.allow_sub_sections and self.curr_sec != next_sec):
            if (next_sec in self.include_sections):
                if (add_edge):
                    self.add_network_edge(self.corrected_curr_sec, next_sec, toc_view, True)
                return True
            else:
                print ("False")
                return False
        else:
            return False
                
    def get_num_pages(self, curr_sec):
        if (curr_sec in self.include_sections):
            return self.num_pages
        else:
            return calculate_num_pages(curr_sec)
            
    def calculate_num_pages(self, curr_sec):
        print ("get_num_pages")
        if (self.allow_sub_sections):            
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
        else:
            num_pages = self.num_pages_adjustment(curr_sec)
            return num_pages
            
    def num_pages_adjustment(self, path_sec):
        num_pages = path_sec.pages + 1
        if (path_sec.pages == 1):
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
        print (str(len(include_sections)) + "," + str(len(in_toc)))
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
        
    def add_network_edge(self, start_sec, end_sec, toc_view, start_sec_checked=False):
        end_toc, end_sec = self.check_and_get_toc(end_sec)
        
        if (start_sec_checked == False):
            start_toc, start_sec = self.check_and_get_toc(start_sec)
        
        if (end_sec != start_sec):
            edge_added = self.ebook_network.add_edge(start_sec.start_page, end_sec.start_page)
        
            if (edge_added):
                toc_view.load_network(self.ebook_network.data)
            
    def check_and_get_toc(self, path_sec):
        path_toc = self.get_in_toc(path_sec, self.toc)
        if (path_toc is None):
            print ("path_toc is None")
            path_toc = self.get_non_toced_parent(self.spine.index(path_sec))
            path_sec = self.spine[self.spine.index(path_toc.abspath)]
            
        return (path_toc, path_sec)
            
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
         

         
    def get_page_label(self, frac, current_page):
        if (self.allow_sub_sections):
            return (current_page.start_page + frac*float(self.get_section_pages(current_page))+1) - self.spine[self.start_spine].start_page
        else:
            return frac*float(self.get_section_pages(current_page)) + 1
            
    def update_page_label(self, userInput, current_page):
        if (self.allow_sub_sections):
            return userInput + self.spine[self.start_spine].start_page - 1
        else:
            return userInput + current_page.start_page
            
    def get_section_pages(self, curr_sec):
        if (self.allow_sub_sections):
            if (curr_sec.pages == 1):
                return 0.8
            else:
                return curr_sec.pages-1
        else:
            return curr_sec.pages
            
    def get_scrollbar_frac(self, new_page, current_page):
        print (new_page)
        if (self.allow_sub_sections):
            return new_page+self.spine[self.start_spine].start_page-1
        else:
            return new_page+current_page.start_page-1
        