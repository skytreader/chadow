package net.skytreader.chadow;

import com.alibaba.fastjson.JSON;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStreamReader;

import java.util.Stack;

import net.skytreader.chadow.models.Config;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.Options;

/**
 * Hello world!
 *
 */
public class App 
{
    public static void listDirs(){
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

    public static void jsonTest() throws Exception{
        BufferedReader br = new BufferedReader(new InputStreamReader(new FileInputStream("/home/chad/.chadow/config.json")));
        // It's just one line, for now
        String jsonConfig = br.readLine();
        br.close();
        Config c = JSON.parseObject(jsonConfig, Config.class);
    }

    public static void cli(String[] args) throws Exception{
        Options opt = new Options();
        opt.addOption("cmd", true, "command to run");

        CommandLineParser clp = new DefaultParser();
        CommandLine cmdLine = clp.parse(opt, args);
    }

    public static void main(String[] args){
        try{
            cli(args);
        } catch(Exception e){
            e.printStackTrace();
        }
    }
}
