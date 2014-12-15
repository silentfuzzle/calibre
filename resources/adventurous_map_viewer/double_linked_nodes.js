/*
 * Copyright 2014 Emily Palmieri <silentfuzzle@gmail.com>
 * License: GNU GPL v3
 */
 
// Defines a Double-Linked List storage structure for storing the user's history
function DoubleList() {
    this.currNode = null;
    
    // Set the current position to the next position in history
    this.nextNode = function(position) {
        var tempNode = this.currNode;
        this.currNode = this.currNode.next;
        
        // Handle the event that Calibre's history is off
        if (this.currNode == null) {
            this.currNode = this.makeNode(position);
            tempNode.next = this.currNode;
            this.currNode.prev = tempNode;
        }
        
        return this.currNode;
    };
    
    // Set the current position to the previous position in history
    this.prevNode = function(position) {
        var tempNode = this.currNode;
        this.currNode = this.currNode.prev;
        
        // Handle the event that Calibre's history is off
        if (this.currNode == null) {
            this.currNode = this.makeNode(position);
            tempNode.prev = this.currNode;
            this.currNode.next = tempNode;
        }
        
        return this.currNode;
    };
    
    // Replace the position of the current node with the user's current position
    this.replaceNode = function(newPosition) {
        this.currNode.pos = newPosition;
        return this.currNode;
    };
    
    // Create a position in history
    this.makeNode = function(position) {
        var node = { pos: position, next: null, prev: null };
        return node;
    };
        
    // Add a new position in history, replacing the position after the current position
    this.addNode = function(position) {
        var node = this.makeNode(position);
        if (this.currNode != null) {
            this.currNode.next = node;
            node.prev = this.currNode;
        }
        
        // If a current position doesn't exist, set it to the new position
        this.currNode = node;
        return node;
    };
}