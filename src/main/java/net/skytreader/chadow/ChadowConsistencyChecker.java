package net.skytreader.chadow;

import java.io.IOException;

public interface ChadowConsistencyChecker{

    /**
    Creates an index file for the given sector. The index file is expected to
    be somewhere inside the chadow installation directory.
    */
    public void indexSector(String library, String sectorName, String sectorPath) throws IOException; 
}
