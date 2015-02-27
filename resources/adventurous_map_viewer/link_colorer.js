function LinkColorer() {
    this.linkDictionary = new Object();
    this.minNodeID = -1;
    
    this.updateMinNodeID = function(nodeID) {
        if (this.minNodeID == -1 || nodeID < this.minNodeID) {
            this.minNodeID = nodeID;
        }
    };
    
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
    
    this.buildLinkDictionary = function(link) {
        var tempDictionary = new Object();
        var addNodeMethod = this.addNode;
        
        link.each(function(d) {
            var sourceID = parseFloat(d.source.id);
            var targetID = parseFloat(d.target.id);
            
            var target = addNodeMethod(tempDictionary, targetID);
            var source = addNodeMethod(tempDictionary, sourceID);
            
            var linkInfo = new NetworkLink(source, target, this);
            target.inLinks.push(linkInfo);
            source.outLinks.push(linkInfo);
        });
        
        this.linkDictionary = tempDictionary;
        if (this.linkDictionary.hasOwnProperty(this.minNodeID)) {
            this.linkDictionary[this.minNodeID].followOutLinks(new Crumb());
        }
    };
    
    this.colorLinksFromRecentHistory = function(historyNode, endNodeID, 
            endPoints, nodesOnPath) {
        var currHistoryNode = historyNode;
        var colorInfo = { endPoints: endPoints, lastHistory: currHistoryNode, 
                nodesOnPath: nodesOnPath };
        
        var currNodeID = currHistoryNode.pos;
        if (currNodeID != endNodeID) {
            var currNode = this.linkDictionary[currNodeID];
            var prevHistoryNode = currHistoryNode.prev;
            var currLink = currNode.getLink(prevHistoryNode.pos);
            endPoints.push(currLink.linkSVG);
            nodesOnPath[currLink.target.nodeID] = 1;
            nodesOnPath[currLink.source.nodeID] = 1;
            colorInfo = this.colorLinksFromRecentHistory(prevHistoryNode, endNodeID, 
                    endPoints, nodesOnPath);
        }
        
        return colorInfo;
    };
    
    this.colorLinksFromAllHistory = function(startNodeID, historyNode, 
            seenNodes, endPoints, nodesOnPath) {
        var currHistoryNode = historyNode;
        var colorInfo = { endPoints: endPoints, lastHistory: currHistoryNode, 
                nodesOnPath: nodesOnPath };
                
        if (currHistoryNode != null) {
            var currNodeID = currHistoryNode.pos;
            if (seenNodes.indexOf(currNodeID) != -1) {
                endPoints = [];
                seenNodes = [];
                nodesOnPath = new Object();
                
                currHistoryNode = currHistoryNode.next;
                while (currHistoryNode.pos != startNodeID) {
                    currHistoryNode = currHistoryNode.next;
                }
                colorInfo = this.colorLinksFromRecentHistory(currHistoryNode, 
                        currNodeID, endPoints, nodesOnPath);
            }
            else {
                if (this.linkDictionary.hasOwnProperty(currNodeID)) {
                    seenNodes.push(currNodeID);
                    var currNode = this.linkDictionary[currNodeID];
                    var prevHistoryNode = currHistoryNode.prev;
                    if (prevHistoryNode != null) {
                        var currLink = currNode.getLink(prevHistoryNode.pos);
                        if (currLink != null) {
                            endPoints.push(currLink.linkSVG);
                            nodesOnPath[currLink.target.nodeID] = 1;
                            nodesOnPath[currLink.source.nodeID] = 1;
                            colorInfo = this.colorLinksFromAllHistory(
                                    startNodeID, prevHistoryNode, seenNodes, 
                                    endPoints, nodesOnPath);
                        }
                    }
                }
            }
        }
        
        return colorInfo;
    };
    
    this.mergeEndPointLists = function(endpoints, crumb, nodesOnPath, 
            historyNode) {
        var restart = false;
        var link = crumb.link;
        var historyOnDistance = [];
        while (link != null) {
            var sourceID = link.source.nodeID;
            var targetID = link.target.nodeID;
            
            var sourceOnPath = nodesOnPath.hasOwnProperty(sourceID);
            var targetOnPath = nodesOnPath.hasOwnProperty(targetID);
            if (targetID != crumb.link.target.nodeID && 
                    (sourceOnPath || targetOnPath)) {
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
        
        if (restart) {
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
            
            var colorInfo = this.colorLinksFromRecentHistory(historyNode, 
                    minID, [], new Object());
            endpoints = this.colorLinksFromDistance(historyNode, 
                    colorInfo.lastHistory.pos, colorInfo.endPoints, 
                    new Object());
        }
        
        return endpoints;
    };
    
    this.colorLinksFromMinNodeDistance = function(historyNode, currNodeID, 
            endpoints, nodesOnPath) {
        var crumb = this.linkDictionary[currNodeID].crumb;
        endpoints = this.mergeEndPointLists(endpoints, crumb, nodesOnPath, 
                historyNode);
        
        return endpoints;
    };
    
    this.colorLinksFromCurrNodeDistance = function(historyNode, currNodeID, 
            endpoints, nodesOnPath) {
        this.linkDictionary[currNodeID].clearSearch();
        this.linkDictionary[this.minNodeID].clearSearch();

        this.linkDictionary[currNodeID].followInLinks(this.minNodeID, 
                new Crumb());
        var crumb = this.linkDictionary[this.minNodeID].crumb;
        
        endpoints = this.mergeEndPointLists(endpoints, crumb, nodesOnPath, 
                historyNode);        
        return endpoints;
    };
    
    this.getPathToColor = function(historyNode) {
        var endpoints = [];
        
        var colorInfo = this.colorLinksFromAllHistory(historyNode.pos, 
                historyNode, [], [], new Object());
        endpoints = colorInfo.endPoints;
        
        if (colorInfo.lastHistory != null) {
            var currNodeID = colorInfo.lastHistory.pos;
            if (currNodeID != this.minNodeID &&
                    this.linkDictionary.hasOwnProperty(this.minNodeID) && 
                    this.linkDictionary.hasOwnProperty(currNodeID)) {
                endpoints = this.colorLinksFromDistance(historyNode, 
                        currNodeID, endpoints, colorInfo.nodesOnPath);
            }
        }
        
        return endpoints;
    };
    
    this.colorLinksFromDistance = this.colorLinksFromMinNodeDistance;
}
