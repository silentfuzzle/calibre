
__license__   = 'GPL v3'
__copyright__ = '2014, Emily Palmieri <silentfuzzle@gmail.com>'

from sets import Set
from calibre.gui2.viewer.toc_section import TOCSection

# This object determines how all the HTML files in the spine are displayed in sections.
class TOCSections (object):

    # Constructor
    # toc - (calibre.ebooks.metadata.toc.TOC) the current ebook's TOC
    # spine - (List(SpineItem)) the current ebook's order of sections
    def __init__(self, toc, spine):
        self.toc = toc
        self.spine = spine
        
        self.toc_sections = []
        self.curr_section = None
        self.generate_toc_sections()
        
    # Generate all the sections found in the e-book
    def generate_toc_sections(self):
        found_sections = Set()
        for t in self.toc.flat():
            if (t.parent is not None and t.abspath in self.spine):
                spine_index = self.spine.index(t.abspath)
                if (spine_index not in found_sections):
                    include_sections = self.find_include_sections(t)
                    toc_section = TOCSection(include_sections, self.spine)
                    self.toc_sections.append(toc_section)
                    
                    for s in include_sections:
                        found_sections.add(s)
        
    # Set the sections included in the current group, returns True if included sections were updated
    # curr_index (int) - the index of the current section in the spine
    # curr_sec (SpineItem) - the currect section being viewed
    def set_curr_sec(self, curr_index, curr_sec):
        curr_toc, self.corrected_curr_sec = self.check_and_get_toc(curr_sec)
        if (self.curr_section is None):
            self.curr_section = self.get_curr_sec(curr_index, curr_toc)
            return True
            
        if (self.curr_section.includes_section(curr_index) == False):
            self.curr_section = self.get_curr_sec(curr_index, curr_toc)
            
            return True
        return False
        
    # Return the section that contains the given index
    # curr_index (int) - the index of the current section in the spine
    # curr_toc (calibre.ebooks.metadata.toc.TOC) - the TOC entry of the current section
    def get_curr_sec(self, curr_index, curr_toc):
    
        # Check if the entry appears in any sections that have been calculated already
        done = False
        i = 0
        while done == False:
            sec = self.toc_sections[i]
            if (sec.includes_section(curr_index)):
                done = True
            else:
                i = i + 1
        
        if done:
            return sec
        else:
            # Calculate the section containing the file
            include_sections = self.find_include_sections(curr_toc)
            toc_section = TOCSection(include_sections, self.spine)
            self.toc_sections.append(toc_section)
            return toc_section
 
    # Returns the sections to include in this group of sections
    # curr_toc (calibre.ebooks.metadata.toc.TOC) - the TOC entry of the current section
    def find_include_sections(self, curr_toc):
        include_sections = Set()
        
        # Include the root of the TOC tree with this section and all TOC entries in it
        curr_parent = curr_toc
        while (curr_parent.parent.parent is not None):
            curr_parent = curr_parent.parent
            
        for t in curr_parent.flat():
            include_sections.add(t.abspath)
        
        # Determine where to check for sections that aren't in the toc
        in_toc = Set()
        spine_len = len(self.spine)
        for s in include_sections:
            spine_index = self.spine.index(s)
            in_toc.add(spine_index)
        
        # Include adjacent sections that aren't in the toc
        in_toc = self.search_in_toc(0, 0, in_toc)
        return in_toc
        
    # Find adjacent sections in the spine that aren't in the TOC that should be included in the section group
    # index (integer) - the index to search from
    # num_found (integer) - the number of entries in the section group that were found in this recursive search
    # in_toc (List(integer)) - the indicies of the sections included in the section group
    # found_first_toc_entry (boolean) - whether the first section in the TOC has been found yet
    def search_in_toc(self, index, num_found, in_toc, found_first_toc_entry=False):
        next_index = index + 1
        
        if (index not in in_toc):
            # Check if the first section in the toc has been found
            page_in_toc = self.get_in_toc(self.spine[index])
            if (found_first_toc_entry == False):
                if (page_in_toc is not None):
                    found_first_toc_entry = True
                    
            # Add this section if the previous section is in the included sections
            # and this section isn't in the toc
            if (index - 1 in in_toc):
                if (page_in_toc is None):
                    in_toc.add(index)
                
            # Only check the next section if not all the sections included in the toc have been found
            if (next_index < len(self.spine) and num_found < len(in_toc)):
                in_toc = self.search_in_toc(next_index, num_found, in_toc, 
                        found_first_toc_entry)
        else:
            # Include all sections not included in the toc at the beginning of the book
            if (found_first_toc_entry == False):
                found_first_toc_entry = True
                i = index - 1
                while (i >= 0):
                    in_toc.add(i)
                    
                    i = i - 1
                    
            num_found = num_found + 1
            
            # Always check the section after the last included in the toc
            if (next_index < len(self.spine)):
                in_toc = self.search_in_toc(next_index, num_found, in_toc, 
                        found_first_toc_entry)
            
        return in_toc  
        
    # Return a section's TOC and SpineItem entries if it exists in the TOC
    # Return the section's parent's TOC and SpineItem entries if it doesn't exist in the TOC
    # path_sec (string) - the section of the ebook to find the SpineItem and TOC for
    def check_and_get_toc(self, path_sec):
        # Attempt to get the section's TOC entry
        path_toc = self.get_in_toc(path_sec)
        corrected_path_sec = path_sec
        
        if (path_toc is None):
            # Get the TOC entry of the section's parent
            path_toc = self.get_non_toced_parent(self.spine.index(path_sec))
            
            # Get the SpineItem of the section's parent
            corrected_path_sec = self.spine[self.spine.index(path_toc.abspath)]
        
        return (path_toc, corrected_path_sec)
            
    # Returns the TOC entry of a section's parent
    # A section's parent is the nearest previous section in the ebook's spine that exists in the TOC
    # If such a section doesn't exist, it is the nearest next section in the book's spine that exists in the TOC
    # current_index (integer) - location of the section in the spine or the previous location checked
    # back (boolean) - true if the previous section from the current index should be checked
    def get_non_toced_parent(self, current_index, back=True):
        check_in_toc_index = current_index - 1
        if (back == False):
            check_in_toc_index = current_index + 1
            
        if (check_in_toc_index < 0):
            # The beginning of the ebook was passed, check the next sections in the following recusive calls
            back = False
        else:
            curr_toc = self.get_in_toc(self.spine[check_in_toc_index])
            if (curr_toc is not None):
                return curr_toc
        
        return self.get_non_toced_parent(check_in_toc_index, back)
        
    # Returns the TOC entry of a section if it exists in the TOC
    # Returns None if the passed section doesn't exist in the TOC
    # page (string) - the full path to the section of the ebook to check
    def get_in_toc(self, page):
        for t in self.toc.flat():
            if (page == t.abspath):
                return t
        return None