package net.skytreader.chadow;

import java.io.File;

public class NaiveConsistencyChecker implements ChadowConsistencyChecker{
    @Override
    public void indexSector(String library, String sectorName, String sectorPath){
        String chadowIndexPath = "/home/chad/" + library + "/" + sectorPath;
        File chadowIndexDir = new File(chadowIndexPath);

        if (chadowIndexDir.isDirectory()){
            // We can safely work.
        } else if (chadowIndexDir.exists()){
            System.out.println(chadowIndexPath + " exists but is not a directory.");
        } else{
            // Not a directory, and does not exist.
            chadowIndexDir.mkdirs();
        }
    }
}
