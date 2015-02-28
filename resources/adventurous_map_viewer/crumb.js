/*
 * Copyright 2015 Emily Palmieri <silentfuzzle@gmail.com>
 * License: GNU GPL v3
 */
 
 // Stores a pointer to the shortest path to reach a NetworkNode
function Crumb() {
    this.numOnHistLinks = 0;
    this.length = 0;
    this.link = null;
    
    // Returns a copy of this object
    this.copy = function() {
        var copyCrumb = new Crumb();
        copyCrumb.numOnHistLinks = this.numOnHistLinks;
        copyCrumb.length = this.length;
        copyCrumb.link = this.link;
        
        return copyCrumb;
    };
}

// Stores information about a link
// s - The source NetworkNode object
// t - The target NetworkNode object
// l - The SVG element representing the link in the interface
function NetworkLink(s, t, l) {
    this.source = s;
    this.target = t;
    this.linkSVG = l;
}
