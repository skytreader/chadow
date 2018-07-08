package net.skytreader.chadow.models;

public class Config{
    private String version;
    private Library[] libraries;

    public Config(String version, Library[] libraries){
        this.version = version;
        this.libraries = libraries;
    }

    public String getVersion(){
        return version;
    }

    public Library[] getLibraries(){
        return libraries;
    }

    public void setVersion(String version){
        this.version = version;
    }

    public void setLibraries(Library[] libraries){
        this.libraries = libraries;
    }
}
