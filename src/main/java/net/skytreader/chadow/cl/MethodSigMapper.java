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

import org.apache.commons.cli.CommandLine;

public class MethodSigMapper{
    interface ArgConverter<T> {
        T convert(String s);
    }

    private static ArgConverter<String> stringConverter = (String s) -> s;
    private static ArgConverter<Integer> intConverter = (String s) -> Integer.parseInt(s);

    private static final Map<String, ArgConverter[]> NAME_SIG_MAPPER = new Hashtable();

    static{
        NAME_SIG_MAPPER.put("indexSector", new ArgConverter[]{stringConverter, stringConverter, stringConverter});
    }

    public static void interpret(CommandLine cmdLine){
        String cmd = cmdLine.getOptionValue("cmd");
    }
}
