/*
 * Copyright 2015 Emily Palmieri <silentfuzzle@gmail.com>
 * License: GNU GPL v3
 */
 
 // Stores information about a node in a network for use in shortest distance searches
function NetworkNode(nID) {
    this.nodeID = nID;
    this.visited = false;
    this.crumb = new Crumb();
    this.inLinks = [];
    this.outLinks = [];
    
    // Returns the link object from the node with the given ID to this node if it exists
    // sourceID - The ID of the source node
    this.getInLink = function(sourceID) {
        var source = null;
        var n = 0;
        while (n < this.inLinks.length && source == null) {
            if (this.inLinks[n].source.nodeID == sourceID) {
                source = this.inLinks[n];
            }
            n++;
        }
        return source;
    };
    
    // Returns the link object from this node to the node with the given ID if it exists
    // targetID - The ID of the target node
    this.getOutLink = function(targetID) {
        var target = null;
        var n = 0;
        while (n < this.outLinks.length && target == null) {
            if (this.outLinks[n].target.nodeID == targetID) {
                target = this.outLinks[n];
            }
            n++;
        }
        return target;
    };
    
    // Performs a shortest distance search by following the links pointing to this node
    // lastCrumb - The pointer to the last node in the path
    this.followInLinks = function(lastCrumb) {
        if (!this.visited || lastCrumb.length < this.crumb.length) {
            this.visited = true;
            this.crumb = lastCrumb;
                          
            // Update the distance for each link to this node
            for (var n=0; n < this.inLinks.length; n++) {
                var currCrumb = this.crumb.copy();
                currCrumb.link = this.inLinks[n];
                currCrumb.length++;
                
                var prevNode = this.inLinks[n].source;
                prevNode.followInLinks(currCrumb);
            }
        }
    };
    
    // Performs a shortest distance search by following the links points away from this node
    // lastCrumb - The pointer to the last node in the path
    this.followOutLinks = function(lastCrumb) {
        if (!this.visited || lastCrumb.length < this.crumb.length) {
            this.visited = true;
            this.crumb = lastCrumb;
                          
            // Update the distance for each link from this node
            for (var n=0; n < this.outLinks.length; n++) {
                var currCrumb = this.crumb.copy();
                currCrumb.link = this.outLinks[n];
                currCrumb.length++;
                
                var nextNode = this.outLinks[n].target;
                nextNode.followOutLinks(currCrumb);
            }
        }
    };
    
    // Clears all crumbs from paths that include this node
    this.clearSearch = function() {
        if (this.visited) {
            this.visited = false;
            this.crumb = new Crumb();
            
            for (var n=0; n < this.inLinks.length; n++) {
                this.inLinks[n].source.clearSearch();
            }
        }
    };
}
