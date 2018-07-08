package net.skytreader.chadow.models;

public class Library{
    private String comparator;
    private Sector[] sectors;

    public Library(String comparator, Sector[] sectors){
        this.comparator = comparator;
        this.sectors = sectors;
    }

    public String getComparator(){
        return comparator;
    }

    public Sector[] getSectors(){
        return sectors;
    }

    public void setComparator(String comparator){
        this.comparator = comparator;
    }

    public void setSectors(Sector[] sectors){
        this.sectors = sectors;
    }
}
