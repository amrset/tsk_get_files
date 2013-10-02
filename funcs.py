"""

Copyright (c) 2013, Los Alamos National Security, LLC
All rights reserved.

Copyright 2013. Los Alamos National Security, LLC. This software
was produced under U.S. Government contract DE-AC52-06NA25396 for Los Alamos 
National Laboratory (LANL), which is operated by Los Alamos National Security, 
LLC for the U.S. Department of Energy. The U.S. Government has rights to use, 
reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR LOS ALAMOS 
NATIONAL SECURITY, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR ASSUMES ANY 
LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is modified to produce 
derivative works, such modified software should be clearly marked, so as not 
to confuse it with the version available from LANL.
 
Additionally, permission is hereby granted, free of charge, to any person 
obtaining a copy of this software and associated documentation files (the 
"Software"), to deal in the Software without restriction, including without 
limitation the rights to use, copy, modify, merge, publish, distribute, 
sublicense, and/or sell copies of the Software, and to permit persons to whom 
the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
SOFTWARE.

----------------------------------------------------------

File/Library with useful functions

@author: Roy Nielsen
"""
import os
import re
import sys
import inspect
from subprocess import call, Popen, PIPE

def log_message(message="", level="normal", priority="debug", syslog_level=None) :
    """
    Logs a message to both stdout and to syslog via logger

    message - the message to log
    
    level - print the message if this value is less than or equal to
            the \"priority\" 
    
    priority - defined value to used to compare with the \"level\".  If 
               the level is less than or equal to the priority value,
               the message will be printed to stdout and via logger
    
    syslog_level - the syslog level to log with

    Author: Roy Nielsen
    """
    if syslog_level is None :
        syslog_level = ""
    else :
        syslog_level = "-p " + syslog_level + " "

    if not re.match("^normal$", level) :
        prog = sys.argv[0]
        # message to be in the format: 
        # <calling_script_name> : <name_of_calling_function> (<line number of calling function>) - <LEVEL>: <message to print>
        message = str(prog) + " : " + \
        inspect.stack()[1][3] + " (" + str(inspect.stack()[1][2]) + ") - " + \
        level.upper() + ": " + str(message)
    else :
        prog = sys.argv[0]
        message = str(prog) + " - " + inspect.stack()[1][3] + \
        " (" + str(inspect.stack()[1][2]) + ") - " + " : " + str(message)
    
    levels = ['quiet', 'normal', 'verbose', 'debug']
    
    if levels.index(level) <= levels.index(priority) :

        print message
        cmd_string = "/usr/bin/logger " + syslog_level + "\"" + message +"\""
        retcode = ""
        try :
            retcode = call(cmd_string, shell=True)
            if retcode < 0 :
                print >> sys.stderr, \
                         "logger Child was terminated by signal", \
                        -retcode
            else :
                pass

        except OSError, err :
            print >> sys.stderr, \
                     "Execution of " + \
                     str(cmd_string) + \
                     " failed: ", \
                     err        


def system_call_retval(cmd="", message_level="normal") :
    """
    Use the subprocess module to execute a command, returning
    the output of the command
    
    Author: Roy Nielsen
    """
    retval = ""
    reterr = ""
#    mycmd = cmd.split()
    if isinstance(cmd, types.ListType) :
        printcmd = " ".join(cmd)
    if isinstance(cmd, types.StringTypes) :
        printcmd = cmd
    
    try :
        pipe = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        
        (stdout_out, stderr_out) = pipe.communicate()

        if stdout_out :
            for line in stdout_out : 
                if line is not None :
                    line.strip("\n")
                    retval = retval + line

        if stderr_out :
            for line in stderr_out : 
                if line is not None :
                    line.strip("\n")
                    reterr = reterr + line            
            
    except ValueError, err :
        log_message("system_call_retval - ValueError: " + str(err) + " command: " + printcmd, "normal", message_level)
    except OSError, err :
        log_message("system_call_retval - OSError: " + str(err) + " command: " + printcmd, "normal", message_level)
    except IOError, err :
        log_message("system_call_retval - IOError: " + str(err) + " command: " + printcmd, "normal", message_level)
    except Exception, err :
        log_message("system_call_retval - Unexpected Exception: "  + str(err)  + " command: " + printcmd, "normal", message_level)
    else :
        log_message(printcmd + \
                    " Returned with error/returncode: " + \
                    str(pipe.returncode), \
                    "debug", \
                    message_level)
        pipe.stdout.close()
    finally:
        log_message("Done with command: " + printcmd, \
                    "verbose", \
                    message_level)
    return (retval, reterr)
        
