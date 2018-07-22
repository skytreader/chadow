package net.skytreader.chadow;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;

import java.util.Stack;

public class NaiveConsistencyChecker implements ChadowConsistencyChecker{
    
    /**
    The directory containing the chadow config file. It is assumed that this
    directory is then exclusively for chadow behind-the-scenes stuff. This
    <em>never</em> ends with the OS-specific file separator.
    */
    private String configLocation;
    
    public NaiveConsistencyChecker(String configLocation){
        if (!configLocation.endsWith(File.separator)){
            this.configLocation = configLocation;
        } else{
            this.configLocation = configLocation.substring(0, configLocation.length());
        }
    }

    @Override
    public void indexSector(String library, String sectorName, String sectorPath) throws IOException{
        String sectorId = createSectorId(sectorName, sectorPath);
        String chadowIndexPath = this.configLocation + File.separator + library + File.separator + sectorId;
        File chadowIndexDir = new File(chadowIndexPath);

        if (chadowIndexDir.isDirectory()){
            createIndex(library, sectorName, sectorPath);
        } else if (chadowIndexDir.exists()){
            System.out.println(chadowIndexPath + " exists but is not a directory.");
        } else{
            // Not a directory, and does not exist.
            System.out.println("Directory does not exist...creating.");
            chadowIndexDir.mkdirs();
            createIndex(library, sectorName, sectorPath);
        }
    }

    private void createIndex(String library, String sectorName, String sectorPath) throws IOException{
        String sectorId = createSectorId(sectorName, sectorPath);
        String indexPath = this.configLocation + File.separator + library + File.separator + sectorId + File.separator + "index";
        PrintWriter pw = new PrintWriter(new FileWriter(indexPath));

        try{
            Stack<File> directories = new Stack<File>();
            directories.push(new File(sectorPath));

            while (directories.size() > 0){
                File curDir = directories.pop();
                pw.println(curDir.getAbsoluteFile());
                String[] curDirContents = curDir.list();

                for(String filename: curDirContents){
                    File f = new File(curDir, filename);
                    if (f.isDirectory()){
                        directories.push(f);
                    } else{
                        pw.println(f.getAbsoluteFile());
                    }
                }
            }
        } catch(Exception e){
            e.printStackTrace();
        } finally{
            pw.close();
        }
    }

    protected String createSectorId(String sectorName, String sectorPath){
        String sanitizedSectorPath = sectorPath.replace(File.separatorChar, '-');
        return sectorName + File.separator + sanitizedSectorPath;
    }
}
