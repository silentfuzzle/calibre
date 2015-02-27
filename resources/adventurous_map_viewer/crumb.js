function Crumb() {
    this.numOnHistLinks = 0;
    this.length = 0;
    this.link = null;
    
    this.copy = function() {
        var copyCrumb = new Crumb();
        copyCrumb.numOnHistLinks = this.numOnHistLinks;
        copyCrumb.length = this.length;
        copyCrumb.link = this.link;
        
        return copyCrumb;
    };
}

function NetworkLink(s, t, l) {
    this.source = s;
    this.target = t;
    this.linkSVG = l;
}
