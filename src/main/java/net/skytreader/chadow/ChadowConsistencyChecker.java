package net.skytreader.chadow;

/**
Interface for methods that will check the consistency of libraries across sectors.
All sectorPaths are expected to be absolute paths from the root directory ("/",
in this case as we are currently constrained to Linuxland).
*/

import java.io.IOException;

public interface ChadowConsistencyChecker{

    /**
    Creates an index file for the given sector. The index file is expected to
    be somewhere inside the chadow installation directory.
    */
    public void indexSector(String library, String sectorName, String sectorPath) throws IOException; 
}
