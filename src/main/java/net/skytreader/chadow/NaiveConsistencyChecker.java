package net.skytreader.chadow;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;

import java.util.Stack;

public class NaiveConsistencyChecker implements ChadowConsistencyChecker{
    @Override
    public void indexSector(String library, String sectorName, String sectorPath) throws IOException{
        String chadowIndexPath = "/home/chad/" + library + "/" + sectorPath;
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
        String indexPath = "/home/chad/" + library + "/" + sectorPath + "/index";
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
}
