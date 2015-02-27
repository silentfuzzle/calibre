function NetworkNode(nID) {
    this.nodeID = nID;
    this.visited = false;
    this.crumb = new Crumb();
    this.inLinks = [];
    this.outLinks = [];
    
    this.getLink = function(sourceID) {
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
    
    this.followInLinks = function(minNodeID, lastCrumb) {
        if (!this.visited || lastCrumb.length < this.crumb.length) {
            //alert("visiting " + this.nodeID);
            this.visited = true;
            this.crumb = lastCrumb;
            
            if (minNodeID != this.nodeID) {                
                for (var n=0; n < this.inLinks.length; n++) {
                    var currCrumb = this.crumb.copy();
                    currCrumb.link = this.inLinks[n];
                    currCrumb.length++;
                    
                    //alert("calling " + prevNode.nodeID + " from " + this.nodeID);
                    var prevNode = this.inLinks[n].source;
                    prevNode.followInLinks(minNodeID, currCrumb);
                }
            }
        }
    };
    
    this.followOutLinks = function(lastCrumb) {
        if (!this.visited || lastCrumb.length < this.crumb.length) {
            //alert("visiting " + this.nodeID);
            this.visited = true;
            this.crumb = lastCrumb;
                          
            for (var n=0; n < this.outLinks.length; n++) {
                var currCrumb = this.crumb.copy();
                currCrumb.link = this.outLinks[n];
                currCrumb.length++;
                
                //alert("calling " + prevNode.nodeID + " from " + this.nodeID);
                var nextNode = this.outLinks[n].target;
                nextNode.followOutLinks(currCrumb);
            }
        }
    };
    
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
