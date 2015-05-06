
__license__   = 'GPL v3'
__copyright__ = '2015, Emily Palmieri <silentfuzzle@gmail.com>'

# This class stores a list of HTML files that appear in a section.
class TOCSection (object):

    # Constructor
    # include_sections (Set) - A list of file indices included in this section
    # spine - (List(SpineItem)) the current ebook's order of sections
    def __init__(self, include_sections, spine):
        self.include_sections = include_sections
        self.num_pages = self.calculate_num_pages(spine)
        
        # Calculate the beginning and end file index of the section
        self.start_spine = -1
        self.end_spine = -1
        for i in self.include_sections:
            if (self.start_spine == -1 or self.start_spine > i):
                self.start_spine = i
            if (self.end_spine == -1 or self.end_spine < i):
                self.end_spine = i
    
    # Returns true if the passed file index appears in this section
    # section_index (int) - The index of the file in the spine
    def includes_section(self, section_index):
        if (section_index in self.include_sections):
            return True
        return False
        
    # Calculates the number of pages in the current group of files
    # spine - (List(SpineItem)) the current ebook's order of sections
    def calculate_num_pages(self, spine):      
        num_pages = 0
        num_found = 0
        spine_index = 0
        start = False
        end = False
        num_sections = len(self.include_sections)
        while (num_found < num_sections and end == False):
            if (spine_index in self.include_sections):
                start = True
                num_found = num_found + 1
                curr_path = spine[spine_index]
                num_pages = num_pages + curr_path.pages
            else:
                if (start == True):
                    end = True
            spine_index = spine_index + 1
        
        if (num_pages == 0):
            num_pages = 1
            
        return num_pages
