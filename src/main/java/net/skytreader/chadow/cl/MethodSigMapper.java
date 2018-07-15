package net.skytreader.chadow.cl;

/**
This class maps command line arguments to methods provided by a
ChadowConsistencyChecker object. It handles parsing and converting CL args to
the appropriate types and calls the appropriate ChadowConsistencyChecker
method.
*/

import java.util.Map;
import java.util.Hashtable;

import net.skytreader.chadow.ChadowConsistencyChecker;
import net.skytreader.chadow.NaiveConsistencyChecker;

import org.apache.commons.cli.CommandLine;

public class MethodSigMapper{
    interface Caller {
        void callMethod(String[] args, ChadowConsistencyChecker cmdSrc) throws Exception;
    }

    private static Caller indexSectorCaller = (String[] args, ChadowConsistencyChecker cmdSrc) -> cmdSrc.indexSector(args[0], args[1], args[2]);

    private static Map<String, Caller> CMD_CALLER_MAP = new Hashtable();

    static{
        CMD_CALLER_MAP.put("indexSector", indexSectorCaller);
    }

    public static void interpret(CommandLine cmdLine) throws Exception{
        String cmd = cmdLine.getOptionValue("cmd");
        Caller c = CMD_CALLER_MAP.get(cmd);
        c.callMethod(cmdLine.getArgs(), new NaiveConsistencyChecker());
    }
}
