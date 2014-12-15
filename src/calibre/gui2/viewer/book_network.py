
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
        if os.path.exists(self.savePath):
            # Read the existing ebook's network file
            json_data = open(self.savePath).read()
            self.data = json.loads(json_data)
            self.bookGraph = node_link.node_link_graph(self.data)
            self.data = json.dumps(self.data)
        else:
            # Create a new file to store the ebook's network in
            # Include all sections with a TOC entry in the network
            self.generate_network()
            self.save_graph()
            
    # Add an edge from a start to an end node/section
    # start_page (float) - the first page of the start section
    # end_page (float) - the first page of the end section
    def add_edge(self, start_page, end_page):
        if (str(end_page) in self.bookGraph[str(start_page)]):
            # Don't add an edge if it already exists
            return False
        else:
            if (str(end_page) not in self.bookGraph.node or str(start_page) not in self.bookGraph.node):
                # The JSON or e-book has been modified, regenerate the graph of nodes
                old_edges = self.bookGraph.edges()
                self.generate_network()
                
                # Add the edges the user created to the new network
                self.bookGraph.add_edges_from(old_edges)
                
            # Add an edge from the start to the end node
            self.bookGraph.add_edge(str(start_page), str(end_page))
            self.save_graph()
            return True
                
    # Generate a new network of nodes from sections in the TOC
    def generate_network(self):
        self.bookGraph = digraph.DiGraph()
        for t in self.toc.flat():
            if (t.parent is not None):
                spine_index = self.spine.index(t.abspath)
                self.bookGraph.add_node(str(self.spine[spine_index].start_page),
                        label=str(self.spine[spine_index].start_page),
                        title=t.text)
            
    # Reloads the network display
    def save_graph(self):
        self.data = node_link.node_link_data(self.bookGraph)
        json.dump(self.data, open(self.savePath, 'w'))
        self.data = json.dumps(self.data)