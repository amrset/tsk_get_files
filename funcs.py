"""

Los Alamos National Security, LLC owns the copyright to "tsk_get_files". 
The license for the software is BSD with standard clauses regarding 
modifications and redistribution.

tsk_get_files has been assigned the Los Alamos Computer Code Number LA-CC-13-102.

Copyright (c) 2013, Los Alamos National Security, LLC All rights reserved.

This software was produced under U.S. Government contract DE-AC52-06NA25396
for Los Alamos National Laboratory (LANL), which is operated by Los Alamos
National Security, LLC for the U.S. Department of Energy. The U.S. Government
has rights to use, reproduce, and distribute this software. NEITHER THE 
GOVERNMENT NOR LOS ALAMOS NATIONAL SECURITY, LLC MAKES ANY WARRANTY, 
EXPRESS OR IMPLIED, OR ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.

If software is modified to produce derivative works, such modified software
should be clearly marked, so as not to confuse it with the version available 
from LANL.

Additionally, redistribution and use in source and binary forms, with or
without modification, are permitted provided that the following conditions
are met:

- Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.

- Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

- Neither the name of Los Alamos National Security, LLC, Los Alamos National
  Laboratory, LANL, the U.S. Government, nor the names of its contributors
  may be used to endorse or promote products derived from this software
  without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY LOS ALAMOS NATIONAL SECURITY, LLC AND 
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, 
BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS 
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL LOS ALAMOS 
NATIONAL SECURITY, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT 
NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY 
OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING 
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, 
EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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
        
