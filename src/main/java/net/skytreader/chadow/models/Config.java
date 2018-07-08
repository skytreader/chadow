package net.skytreader.chadow.models;

public class Config{
    private String version;
    private LibraryMapping libraryMapping;

    public Config(String version, LibraryMapping libraryMapping){
        this.version = version;
        this.libraryMapping = libraryMapping;
    }

    public String getVersion(){
        return version;
    }

    public LibraryMapping getLibraries(){
        return libraryMapping;
    }

    public void setVersion(String version){
        this.version = version;
    }

    public void setLibraries(LibraryMapping libraryMapping){
        this.libraryMapping = libraryMapping;
    }
}
