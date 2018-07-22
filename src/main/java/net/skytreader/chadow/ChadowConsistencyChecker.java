package net.skytreader.chadow;

import java.io.IOException;

public interface ChadowConsistencyChecker{

    /**
    Creates an index file for the given sector. The index file is expected to
    be in `$CHADOW_CONFIG_LOCATION/$library_name/$sector_name/index`.
    */
    public void indexSector(String library, String sectorName, String sectorPath) throws IOException; 
}
