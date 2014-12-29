
__license__   = 'GPL v3'
__copyright__ = '2014, Emily Palmieri <silentfuzzle@gmail.com>'

# This object determines returns a TOC given a SpineItem for all sections in an ebook.
class TOCSections (object):

    # Constructor
    # toc - (calibre.ebooks.metadata.toc.TOC) the current ebook's TOC
    # spine - (List(SpineItem)) the current ebook's order of sections
    def __init__(self, toc, spine):
        self.toc = toc
        self.spine = spine
        
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