
__license__   = 'GPL v3'
__copyright__ = '2014, Emily Palmieri <silentfuzzle@gmail.com>'
__docformat__ = 'restructuredtext en'

import json, os
from networkx.classes import digraph
from networkx.readwrite.json_graph import node_link

class EBookNetwork (object):
    def __init__(self, spine, toc, title, basedir):
        self.savePath = str(os.path.dirname(basedir)) + "/" + str(title) + "Network.json"
        if os.path.exists(self.savePath):
            json_data = open(self.savePath).read()
            self.data = json.loads(json_data)
            self.bookGraph = node_link.node_link_graph(self.data)
            self.data = json.dumps(self.data)
        else:
            self.bookGraph = digraph.DiGraph()
            for s, t in zip(spine, toc):
                self.bookGraph.add_node(str(s.start_page),label=str(s.start_page),title=t.text)
            self.save_graph()
            
    def add_edge(self, start_page, end_page):
        if (str(end_page) in self.bookGraph[str(start_page)]):
            print ("existing edge: " + str(start_page) + " to " + str(end_page))
            return False
        else:
            print ("added edge: " + str(start_page) + " to " + str(end_page))
            self.bookGraph.add_edge(str(start_page), str(end_page))
            self.save_graph()
            return True
            
    def save_graph(self):
        self.data = node_link.node_link_data(self.bookGraph)
        json.dump(self.data, open(self.savePath, 'w'))
        self.data = json.dumps(self.data)