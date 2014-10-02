
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
        if os.path.exists(self.savePath):
            # Read the existing ebook's network file
            json_data = open(self.savePath).read()
            self.data = json.loads(json_data)
            self.bookGraph = node_link.node_link_graph(self.data)
            self.data = json.dumps(self.data)
        else:
            # Create a new file to store the ebook's network in
            # Include all sections with a TOC entry in the network
            self.bookGraph = digraph.DiGraph()
            self.testCount = 0
            for t in toc.flat():
                if (t.parent is not None):
                    self.testCount = self.testCount + 1
                    spine_index = spine.index(t.abspath)
                    self.bookGraph.add_node(str(spine[spine_index].start_page),label=str(spine[spine_index].start_page),title=t.text)
            
            self.save_graph()
            
    # Add an edge from a start to an end node/section
    # start_page (float) - the first page of the start section
    # end_page (float) - the first page of the end section
    def add_edge(self, start_page, end_page):
        if (str(end_page) in self.bookGraph[str(start_page)]):
            # Don't add an edge if it already exists
            return False
        else:
            self.bookGraph.add_edge(str(start_page), str(end_page))
            self.save_graph()
            return True
            
    # Reloads the network display
    def save_graph(self):
        self.data = node_link.node_link_data(self.bookGraph)
        json.dump(self.data, open(self.savePath, 'w'))
        self.data = json.dumps(self.data)