
__license__   = 'GPL v3'
__copyright__ = '2015, Emily Palmieri <silentfuzzle@gmail.com>'

from sets import Set

# This class stores a list of HTML files that appear in a section.
class TOCSection (object):

    # Constructor
    def __init__(self):
        self.include_sections = Set()
        self.num_pages = 0
        self.start_spine = -1
        self.end_spine = -1
    
    # Adds a file to the section
    # curr_index (int) - The index of the file in the spine
    # curr_sec (SpineItem) - an object containing information about the file
    def add(self, curr_index, curr_sec):
        self.include_sections.add(curr_index)
        
        # Set the beginning and end indices of this section in the spine
        if (self.start_spine == -1 or self.start_spine > curr_index):
            self.start_spine = curr_index
        if (self.end_spine == -1 or self.end_spine < curr_index):
            self.end_spine = curr_index
            
        # Add to the number of pages
        self.num_pages = self.num_pages + curr_sec.pages
        
    # Make sure there is at least one page in the section after all the files have been added
    def finish_building(self):
        if (self.num_pages == 0):
            self.num_pages = 1
    
    # Returns true if the passed file index appears in this section
    # section_index (int) - The index of the file in the spine
    def includes_section(self, section_index):
        if (section_index in self.include_sections):
            return True
        return False
        
    # Returns the number of files in this section
    def num_files(self):
        return len(self.include_sections)
