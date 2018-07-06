package net.skytreader.chadow.models;

public class Sector{
    private String sectorName;
    private String sectorPath;

    public Sector(String sectorName, String sectorPath){
        this.sectorName = sectorName;
        this.sectorPath = sectorPath;
    }

    public String getSectorName(){
        return sectorName;
    }

    public String getSectorPath(){
        return sectorPath;
    }
    
    public void setSectorName(String sectorName){
        this.sectorName = sectorName;
    }

    public void setSectorPath(String sectorPath){
        this.sectorPath = sectorPath;
    }
}
