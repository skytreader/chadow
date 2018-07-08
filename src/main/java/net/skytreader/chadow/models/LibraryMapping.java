package net.skytreader.chadow.models;

import java.util.Map;
import java.util.Hashtable;

public class LibraryMapping{
    private Map<String, Library> mapping;

    public LibraryMapping(){
        this.mapping = new Hashtable<String, Library>();
    }

    public void addLibrary(String name, Library l){
        this.mapping.put(name, l);
    }

    public Library getLibrary(String name){
        return this.mapping.get(name);
    }
}
