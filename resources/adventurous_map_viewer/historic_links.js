/*
 * Copyright 2015 Emily Palmieri <silentfuzzle@gmail.com>
 * License: GNU GPL v3
 */
 
 // Stores information about links that may be colored in the interface later
function HistoricLinks(endPoints, historyNode) {
    this.endPoints = endPoints;
    this.lastHistory = historyNode;
    this.nodesOnPath = [];
    
    // Adds a link to this object
    // currLink - A NetworkLink object to add information from
    this.addLink = function(currLink) {
        this.endPoints.push(currLink.linkSVG);
        this.nodesOnPath.push(currLink.target.nodeID);
    };
    
    // Clears the links stored in this object and
    // returns the history linked list to the given position
    // startNodeID - The ID of the node to return to in the history list
    this.reset = function(startNodeID) {
        this.endPoints = [];
        this.nodesOnPath = [];
        
        this.lastHistory = this.lastHistory.next;
        while (this.lastHistory.pos != startNodeID) {
            this.lastHistory = this.lastHistory.next;
        }
    };
    
    // Checks if the given nodeID is included in the path in this object
    // nodeID - The ID of the node to check
    this.contains = function(nodeID) {
        if (this.nodesOnPath.indexOf(nodeID) != -1) {
            return true;
        }
        return false;
    };
}