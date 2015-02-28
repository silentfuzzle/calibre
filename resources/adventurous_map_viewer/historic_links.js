function HistoricLinks(endPoints, historyNode) {
    this.endPoints = endPoints;
    this.lastHistory = historyNode;
    this.nodesOnPath = [];
    
    this.addLink = function(currLink) {
        this.endPoints.push(currLink.linkSVG);
        this.nodesOnPath.push(currLink.target.nodeID);
    };
    
    this.reset = function(startNodeID) {
        this.endPoints = [];
        this.nodesOnPath = [];
        
        this.lastHistory = this.lastHistory.next;
        while (this.lastHistory.pos != startNodeID) {
            this.lastHistory = this.lastHistory.next;
        }
    };
    
    this.contains = function(nodeID) {
        if (this.nodesOnPath.indexOf(nodeID) != -1) {
            return true;
        }
        return false;
    };
}