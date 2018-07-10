package net.skytreader.chadow;

import java.io.IOException;

interface ChadowConsistencyChecker{

    public void indexSector(String library, String sectorName, String sectorPath) throws IOException; 
}
