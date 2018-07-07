package net.skytreader.chadow.models;

public class Library{
    private String name;
    private String comparator;
    private Sector[] sectors;

    public Library(String name, String comparator, Sector[] sectors){
        this.name = name;
        this.comparator = comparator;
        this.sectors = sectors;
    }

    public String getName(){
        return name;
    }

    public String getComparator(){
        return comparator;
    }

    public Sector[] getSectors(){
        return sectors;
    }

    public void setName(String name){
        this.name = name;
    }

    public void setComparator(String comparator){
        this.comparator = comparator;
    }

    public void setSectors(Sector[] sectors){
        this.sectors = sectors;
    }
}
