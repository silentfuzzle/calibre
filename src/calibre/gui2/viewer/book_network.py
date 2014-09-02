
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
            self.testCount = 0
            for t in toc:
                self.process_toc(spine,t)
            print (self.testCount)
            
            self.save_graph()
            
    def process_toc(self, spine, toc):
        self.testCount = self.testCount + 1
        spine_index = spine.index(toc.abspath)
        self.bookGraph.add_node(str(spine[spine_index].start_page),label=str(spine[spine_index].start_page),title=toc.text)
        for t in toc:
            self.process_toc(spine, t)
            
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