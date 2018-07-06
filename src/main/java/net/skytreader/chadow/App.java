package net.skytreader.chadow;

import java.io.File;

import java.util.Stack;

/**
 * Hello world!
 *
 */
public class App 
{
    public static void main( String[] args )
    {
        Stack<File> directories = new Stack<File>();
        directories.push(new File("/home/chad/Documents"));

        while (directories.size() > 0){
            File curDir = directories.pop();
            System.out.println(curDir.getAbsoluteFile());
            String[] curDirContents = curDir.list();

            for(String filename : curDirContents){
                File f = new File(curDir, filename);
                if (f.isDirectory()){
                    directories.push(f);
                } else{
                    System.out.println(f.getAbsoluteFile());
                }
            }
        }
    }
}
