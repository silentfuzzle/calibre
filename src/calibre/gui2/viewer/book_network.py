
__license__   = 'GPL v3'
__copyright__ = '2014, Emily Palmieri <silentfuzzle@gmail.com>'

from sets import Set
import json, os
from networkx.classes import digraph
from networkx.readwrite.json_graph import node_link
from networkx.classes.function import degree

# This class stores data to display in the TOCNetworkView
class EBookNetwork (object):
    SCROLL_LINK = "scroll"
    HYPERLINK_LINK = "hyperlink"

    # Constructor
    # toc_sections (TOCSections) - a object that determines how the HTML files of the ebook are grouped
    # title (string) - the title of the ebook
    # basedir (string) - the full path to the ebook's location
    def __init__(self, toc_sections, title, basedir):
        self.savePath = str(os.path.dirname(basedir)) + "/" + str(title) + " Network.json"
        self.toc_sections = toc_sections
        
        # Stores the users last search
        self.start_search = 0
        self.prev_search = None
        
        refresh = False
        if os.path.exists(self.savePath):
            try:
                # Read the existing ebook's network file
                json_data = open(self.savePath).read()
                self.data = json.loads(json_data)
                self.bookGraph = node_link.node_link_graph(self.data)
                self.data = json.dumps(self.data)
            except Exception:
                # The JSON is unreadable, regenerate it
                refresh = True
        else:
            # Create a new file to store the ebook's network in
            refresh = True
        
        self.pages_viewed = 0
        if (refresh):
            self.refresh_network()
        else:
            # Calculate the number of pages viewed so far
            # Nodes with links are considered viewed
            for n in self.bookGraph.node:
                node_degree = degree(self.bookGraph, n)
                
                if (node_degree > 0):
                    self.pages_viewed = self.pages_viewed + self.bookGraph.node[n]['pages']
            
    # Search the titles of the nodes in the network by a user query
    # text (string) - the text the user has searched for
    def search (self, text):
        text = text.lower()
        
        # The user has searched for a new term, reset the search
        if (self.prev_search != text):
            self.prev_search = text
            self.start_search = 0
            
        # Attempt to search forward through the nodes for the term
        found_page = self.perform_search()
        if (found_page == -1 and self.start_search != 0):
            # The search failed, begin searching at the start of the node list
            self.start_search = 0
            found_page = self.perform_search()
        
        return found_page
    
    # Search through the titles in a list of nodes starting from the last node containing the search term
    def perform_search(self):
        curr_search = 0
        for t in self.bookGraph.node:
            if (curr_search >= self.start_search and
                    self.bookGraph.node[t]['title'].lower().find(self.prev_search) != -1):
                # Note the index to begin the next search on if the user searches for the same term again
                self.start_search = curr_search + 1
                return float(t)
                
            curr_search = curr_search + 1
        
        # The search term wasn't found in any titles after the starting position
        return -1
            
    # Add an edge from a start to an end node/section
    # start_page (float) - the first page of the start section
    # end_page (float) - the first page of the end section
    # link_type (string) - A string representing the type of link to create
    #       "hyperlink" - A link representing a hyperlink between sections
    #       "scroll" - A link representing that the user can scroll between sections
    def add_edge(self, start_page, end_page, link_type):
        str_start_page = str(start_page)
        str_end_page = str(end_page)
        
        if (str_end_page not in self.bookGraph.node or 
                str_start_page not in self.bookGraph.node):
            # The JSON or e-book has been modified, regenerate the graph of nodes
            old_edges = self.bookGraph.edges()
            self.generate_network()
            self.bookGraph.add_edges_from(old_edges)
        
        if (str_end_page in self.bookGraph[str_start_page]):
            if (self.bookGraph[str_start_page][str_end_page]['type'] == EBookNetwork.SCROLL_LINK and
                    link_type == EBookNetwork.HYPERLINK_LINK):
                # Allow "scroll" type links to be replaced with "hyperlink" type links
                self.bookGraph.remove_edge(str_start_page, str_end_page)
                
                # Decrement the number of pages viewed
                # if nodes that did have links no longer have links
                if (degree(self.bookGraph, str_start_page) == 0):
                    self.pages_viewed = self.pages_viewed - self.bookGraph.node[str_start_page]['pages']
                if (degree(self.bookGraph, str_end_page) == 0):
                    self.pages_viewed = self.pages_viewed - self.bookGraph.node[str_end_page]['pages']
            else:
                # Don't add an edge if it already exists
                return False
                
        # Increment the number of pages viewed
        # if nodes that didn't have links now have links
        if (degree(self.bookGraph, str_start_page) == 0):
            self.pages_viewed = self.pages_viewed + self.bookGraph.node[str_start_page]['pages']
        if (degree(self.bookGraph, str_end_page) == 0):
            self.pages_viewed = self.pages_viewed + self.bookGraph.node[str_end_page]['pages']
            
        # Add an edge from the start to the end node
        self.bookGraph.add_edge(str_start_page, str_end_page,
                type=link_type)
        self.update_network()
        return True
            
    # Generate a new network of nodes
    def refresh_network(self):
        self.generate_network()
        self.update_network()
        self.pages_viewed = 0
                
    # Generate a new network of nodes from sections in the TOC
    def generate_network(self):
        spine = self.toc_sections.spine
        self.toc_sections.generate_toc_sections()
        first_section = self.toc_sections.get_section(0)
        seen_sections = Set()
        self.bookGraph = digraph.DiGraph()
        curr_index = 0
        for t in self.toc_sections.toc.flat():
            if (t.parent is not None and t.abspath in spine):
            
                # Mark nodes that are scrollable from the beginning of the book
                spine_index = spine.index(t.abspath)
                if (spine_index not in seen_sections):
                    seen_sections.add(spine_index)
                    
                    # Calculate node properties
                    in_first = first_section.includes_section(spine_index)
                    node_type = 2
                    if (in_first):
                        node_type = 1
                    curr_index = curr_index + 1
                    num_pages = self.toc_sections.get_pages_in_node(spine_index)
                        
                    # Add node to network
                    self.bookGraph.add_node(str(spine[spine_index].start_page),
                            label=str(spine[spine_index].start_page),
                            title=t.text,
                            type=node_type,
                            spine=curr_index,
                            pages=num_pages)
            
    # Updates the network JSON data with newly added/removed links
    def update_network(self):
        self.data = node_link.node_link_data(self.bookGraph)
        self.data = json.dumps(self.data)
        
    # Saves the network JSON data to a file
    def save_network(self):
        self.data = node_link.node_link_data(self.bookGraph)
        json.dump(self.data, open(self.savePath, 'w'))