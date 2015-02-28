/*
 * Copyright 2015 Emily Palmieri <silentfuzzle@gmail.com>
 * License: GNU GPL v3
 */
 
// Colors the links in a network given the user's history and current position
function LinkColorer() {
    this.linkDictionary = new Object();
    this.minNodeID = -1;
    
    ///////////////////////////////////////////////////////////////////////////
    // PATH SEARCH PREPARATION
    ///////////////////////////////////////////////////////////////////////////
    
    // Set the section with the smallest page number
    // nodeID - The first page/ID of the section to check
    this.updateMinNodeID = function(nodeID) {
        if (this.minNodeID == -1 || nodeID < this.minNodeID) {
            this.minNodeID = nodeID;
        }
    };
    
    // Add a node to a dictionary of links between nodes
    // linkDictionary - The dictionary of links
    // nodeID - The ID of the node to add
    this.addNode = function(linkDictionary, nodeID) {
        var node;
        if (linkDictionary.hasOwnProperty(nodeID)) {
            node = linkDictionary[nodeID];
        }
        else {
            node = new NetworkNode(nodeID);
            linkDictionary[nodeID] = node;
        }
        
        return node;
    };
    
    // Builds a dictionary of links between nodes from a list
    // link - A list of links generated by d3
    this.buildLinkDictionary = function(link) {
        var tempDictionary = new Object();
        var addNodeMethod = this.addNode;
        
        link.each(function(d) {
            // Store the linked nodes
            var sourceID = parseFloat(d.source.id);
            var targetID = parseFloat(d.target.id);
            var target = addNodeMethod(tempDictionary, targetID);
            var source = addNodeMethod(tempDictionary, sourceID);
            
            // Store the link between the two nodes
            var linkInfo = new NetworkLink(source, target, this);
            target.inLinks.push(linkInfo);
            source.outLinks.push(linkInfo);
        });
        
        // Store the dictionary of links
        this.linkDictionary = tempDictionary;
        if (this.linkDictionary.hasOwnProperty(this.minNodeID)) {
            // Calculate the minimum distance and path to the minimum node from all nodes
            this.linkDictionary[this.minNodeID].followOutLinks(new Crumb());
        }
    };
    
    ///////////////////////////////////////////////////////////////////////////
    // GET PATH FROM HISTORY
    ///////////////////////////////////////////////////////////////////////////
    
    // Return the links from a position to another position in history
    // endNodeID - The position in history to stop at
    // colorInfo - An object containing the links found and the links left to search
    this.colorLinksFromRecentHistory = function(endNodeID, colorInfo) {
        var currHistoryNode = colorInfo.lastHistory;
        
        var currNodeID = currHistoryNode.pos;
        if (currNodeID != endNodeID) {
            // Add the link from this position to the next position in history
            var currNode = this.linkDictionary[currNodeID];
            var prevHistoryNode = currHistoryNode.prev;
            var currLink = currNode.getLink(prevHistoryNode.pos);
            colorInfo.lastHistory = prevHistoryNode;
            colorInfo.addLink(currLink);
            
            // Go to the next position in history
            colorInfo = this.colorLinksFromRecentHistory(endNodeID, colorInfo);
        }
        
        // Return the link list when the end node is found
        return colorInfo;
    };
    
    // Return the links from the user's current position to their last position in history
    // startNodeID - The ID of the user's current position
    // colorInfo - An object containing the links found and the links left to search
    this.colorLinksFromAllHistory = function(startNodeID, colorInfo) {
        var currHistoryNode = colorInfo.lastHistory;
        
        if (currHistoryNode != null) {
            var currNodeID = currHistoryNode.pos;
            if (colorInfo.contains(currNodeID)) {
            
                // If the user's history contains a loop,
                // only include the links from the user's current position
                // to where the loop begins
                colorInfo.reset(startNodeID);
                colorInfo = this.colorLinksFromRecentHistory(currNodeID, 
                        colorInfo);
            }
            else {
            
                // Make sure the node in history has links
                if (this.linkDictionary.hasOwnProperty(currNodeID)) {
                    var currNode = this.linkDictionary[currNodeID];
                    var prevHistoryNode = currHistoryNode.prev;
                    if (prevHistoryNode != null) {
                    
                        // Make sure this node is connected to the user's current path
                        var currLink = currNode.getLink(prevHistoryNode.pos);
                        if (currLink != null) {
                            colorInfo.lastHistory = prevHistoryNode;
                            colorInfo.addLink(currLink);
                            colorInfo = this.colorLinksFromAllHistory(
                                    startNodeID, colorInfo);
                        }
                    }
                }
            }
        }
        
        // Return the links when all the links in the history have been added
        // or when a node is found that is disconnected from the user's current path
        return colorInfo;
    };
    
    ///////////////////////////////////////////////////////////////////////////
    // GET PATH FROM DISTANCE
    ///////////////////////////////////////////////////////////////////////////
    
    // Return the links from the user's current position to the beginning of the book
    // using a shortest path search from the beginning of the book
    // currNodeID - The position to start the shortest path search from
    // historicLinks - The links from the user's current position to currNodeID
    this.colorLinksFromMinNodeDistance = function(currNodeID, historicLinks) {
        
        // Get the shortest path from the given position to the beginning of the book
        var crumb = this.linkDictionary[currNodeID].crumb;
        
        // Merge the paths found from the user's history and the shortest path
        var endpoints = this.mergeEndPointLists(historicLinks, crumb);
        return endpoints;
    };
    
    // Return the links from a given position to the beginning of the book
    // using a shortest path search from the given position
    // currNodeID - The position to start the shortest path search from
    // historicLinks - The links from the user's current position to currNodeID
    this.colorLinksFromCurrNodeDistance = function(currNodeID, historicLinks) {
    
        // Clear crumbs from the last search
        this.linkDictionary[currNodeID].clearSearch();
        this.linkDictionary[this.minNodeID].clearSearch();

        // Perform the search and get the path
        this.linkDictionary[currNodeID].followInLinks(new Crumb());
        var crumb = this.linkDictionary[this.minNodeID].crumb;
        
        // Merge the paths found from the user's history and the shortest path
        var endpoints = this.mergeEndPointLists(historicLinks, crumb);        
        return endpoints;
    };
    
    // Set which search method to use here
    this.colorLinksFromDistance = this.colorLinksFromMinNodeDistance;
    
    ///////////////////////////////////////////////////////////////////////////
    // GET PATH FROM BEGINNING TO POSITION
    ///////////////////////////////////////////////////////////////////////////
    
    // Merges a list of links from the user's current position to the last position in their history
    // and a list of links from the last position in the user's history to the beginning of the book
    // historicLinks - The links from the user's history
    // crumb - A pointer to the shortest path from the last position in the user's history to the beginning of the book
    this.mergeEndPointLists = function(historicLinks, crumb) {
        var endpoints = historicLinks.endPoints;
        var restart = false;
        var link = crumb.link;
        var historyOnDistance = [];
        
        // Get the links from the shortest distance path
        while (link != null) {
            var sourceID = link.source.nodeID;
            var targetID = link.target.nodeID;
            
            // Check if the shortest distance path intersects the path through the user's history
            var sourceOnPath = historicLinks.contains(sourceID);
            var targetOnPath = historicLinks.contains(targetID);
            if (targetID != crumb.link.target.nodeID && 
                    (sourceOnPath || targetOnPath)) {
                
                // An intersection was found, note what intersected and end the search
                link = null;
                restart = true;
                if (sourceOnPath) {
                    historyOnDistance.push(sourceID);
                }
                if (targetOnPath) {
                    historyOnDistance.push(targetID);
                }
            }
            else {
                endpoints.push(link.linkSVG);
                
                // Advance to the next link in the shortest distance path
                var tempLink = link.source.crumb.link;
                if (tempLink != null && 
                        tempLink.source.nodeID == link.source.nodeID) {
                    link = link.target.crumb.link;
                }
                else {
                    link = tempLink;
                }
            }
        }
        
        // Rebuild the search lists if an intersection occurred
        if (restart) {
            // From the nodes on the shortest distance path that intersected the history path
            // find the one that is the shortest distance from the beginning
            var minID = historyOnDistance[0];
            var minDistance = this.linkDictionary[minID].crumb.length;
            for (var n = 1; n < historyOnDistance.length; n++) {
                var currNodeID = historyOnDistance[n];
                var currDistance = this.linkDictionary[currNodeID].crumb.length;
                if (currDistance < minDistance) {
                    minID = currNodeID;
                    minDistance = currDistance;
                }
            }
            
            // Get the links from the user's history from their current position
            // to the position where the intersection occurred
            var historyNode = historicLinks.lastHistory;
            historicLinks = new HistoricLinks([], historyNode);
            var colorInfo = this.colorLinksFromRecentHistory(minID, 
                    historicLinks);
                    
            // Get the links from the position where the intersection occurred
            // to the beginning of the book and merge the two lists of links
            var lastNodeID = colorInfo.lastHistory.pos;
            historicLinks = new HistoricLinks(colorInfo.endPoints, historyNode);
            endpoints = this.colorLinksFromDistance(lastNodeID, historicLinks);
        }
        
        return endpoints;
    };
    
    // Returns a list of links to color from the user's current position to the beginning of the book
    // historyNode - A linked list of the user's history
    this.getPathToColor = function(historyNode) {
        var endpoints = [];
        
        // Get the links to color from the user's history
        var historicLinks = new HistoricLinks([], historyNode);
        var colorInfo = this.colorLinksFromAllHistory(historyNode.pos, 
                historicLinks);
        endpoints = colorInfo.endPoints;
        
        // Get the links to color from the last position in the user's history
        // to the beginning of the book if a path exists
        if (colorInfo.lastHistory != null) {
            var currNodeID = colorInfo.lastHistory.pos;
            if (currNodeID != this.minNodeID &&
                    this.linkDictionary.hasOwnProperty(this.minNodeID) && 
                    this.linkDictionary.hasOwnProperty(currNodeID)) {
                colorInfo.lastHistory = historyNode;
                endpoints = this.colorLinksFromDistance(currNodeID, colorInfo);
            }
        }
        
        return endpoints;
    };
}
