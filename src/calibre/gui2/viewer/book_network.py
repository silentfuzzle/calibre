
__license__   = 'GPL v3'
__copyright__ = '2014, Emily Palmieri <silentfuzzle@gmail.com>'

import json, os
from networkx.classes import digraph
from networkx.readwrite.json_graph import node_link

# This class stores data to display in the TOCNetworkView
class EBookNetwork (object):

    # Constructor
    # spine - (List(SpineItem)) the current ebook's ordering of sections
    # toc - (calibre.ebooks.metadata.toc.TOC) the current ebook's TOC
    # title (string) - the title of the ebook
    # basedir (string) - the full path to the ebook's location
    def __init__(self, spine, toc, title, basedir):
        self.savePath = str(os.path.dirname(basedir)) + "/" + str(title) + "Network.json"
        self.toc = toc
        self.spine = spine
        
        # Stores the users last search
        self.start_search = 0
        self.prev_search = None
        
        if os.path.exists(self.savePath):
            try:
                # Read the existing ebook's network file
                json_data = open(self.savePath).read()
                self.data = json.loads(json_data)
                self.bookGraph = node_link.node_link_graph(self.data)
                self.data = json.dumps(self.data)
            except Exception:
                # The JSON is unreadable, regenerate it
                self.refresh_network()
        else:
            # Create a new file to store the ebook's network in
            self.refresh_network()
            
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
    def add_edge(self, start_page, end_page):
        if (str(end_page) in self.bookGraph[str(start_page)]):
            # Don't add an edge if it already exists
            return False
        else:
            if (str(end_page) not in self.bookGraph.node or 
                    str(start_page) not in self.bookGraph.node):
                # The JSON or e-book has been modified, regenerate the graph of nodes
                old_edges = self.bookGraph.edges()
                self.generate_network()
                
                # Add the edges the user created to the new network
                self.bookGraph.add_edges_from(old_edges)
                
            # Add an edge from the start to the end node
            self.bookGraph.add_edge(str(start_page), str(end_page))
            self.update_network()
            return True
            
    # Generate a new network of nodes
    def refresh_network(self):
        self.generate_network()
        self.update_network()
                
    # Generate a new network of nodes from sections in the TOC
    def generate_network(self):
        self.bookGraph = digraph.DiGraph()
        for t in self.toc.flat():
            if (t.parent is not None):
                spine_index = self.spine.index(t.abspath)
                self.bookGraph.add_node(str(self.spine[spine_index].start_page),
                        label=str(self.spine[spine_index].start_page),
                        title=t.text)
            
    # Updates the network JSON data with newly added/removed links
    def update_network(self):
        self.data = node_link.node_link_data(self.bookGraph)
        self.data = json.dumps(self.data)
        
    # Saves the network JSON data to a file
    def save_network(self):
        self.data = node_link.node_link_data(self.bookGraph)
        json.dump(self.data, open(self.savePath, 'w'))