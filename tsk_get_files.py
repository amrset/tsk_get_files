#!/usr/bin/python 
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

Program that uses "The Sleuth Kit" commands "fls" and "icat" to rebuild
a file structure from a disk image.

@WARNING: This could be done on an attached disk, such as giving the source
path as /dev/sdb, however that can be dangerous.  It's faster than creating
a binary image first, but if not careful, the deleted data can be damaged.

@author: Roy Nielsen
"""

import os
import re
import sys
import fileinput
import tempfile

from subprocess import Popen, STDOUT, PIPE

from options import ProgramOptions
from funcs import log_message, \
                  system_call_retval

def do_fls(filesystem="", source="", fls="", message_level="normal") :
    """
    Perform fls operations on the bitstream image, writing a temporary file
    with the fls output.
    
    Parameters: program_options = ProgramOptions class, instanciated in calling
                                  function.
                                  
    Returns: temp_file = full path to temp file where fls information has been
                         collected
    
    @author: Roy Nielsen
    """    
    if re.match("^\s*$", str(filesystem)) or \
       re.match("^\s*$", str(source)) or \
       re.match("^\s*$", str(fls)) :
        log_message("Cannot process flsfile with any empty parameters:", \
                    "normal", message_level)
        log_message("filesystem:\t\"" + str(filesystem) + "\"", "normal", message_level)
        log_message("source:\t\"" + str(source) + "\"", "normal", message_level)
        log_message("fls:\t\"" + str(fls) + "\"", "normal", message_level)
        log_message("Exiting...", "normal", message_level)
        sys.exit(253)
        
    #####
    # -pr = p is report full path, r is recursive, d is only deleted files
    command = [fls, "-prd", "-f", filesystem, source]
    retval = ""
    reterr = ""    
    
    log_message("command: " + str(command), "debug", message_level)
    
    try :
        (sfile_descriptor, sfile_name) = tempfile.mkstemp() 
    except Exception, err :
        log_message("Exception making temporary directory: " + str(err), \
                    "normal", message_level)
        log_message("Exiting...", "normal", message_level)
        sys.exit(254)
    else:
        log_message("tmpfile: \"" + str(sfile_name) + "\"", "debug", message_level)
        try :
            sfile_handle = open(sfile_name, "wb")
        except Exception, err :
            log_message("Problem opening file: \"" + str(sfile_name) + "\"", "normal", message_level)
            log_message("Associated exception: \"" + str(err) + "\"", "normal", message_level)
            log_message("Exiting...", "normal", message_level)
            sys.exit(254)
        else :
            try :
                #####
                # Run the FLS command sending stdout to the "sfile_handle" filehandle,
                # opened above.
                reterr = Popen(command, stdout=sfile_handle, stderr=PIPE).communicate()[1]
            except Exception, err :
                log_message("Error attempting to run fls...", "normal", message_level)
                log_message("Associated exception: \"" + str(err) + "\"" + \
                             "normal", message_level)
                sys.exit(254)
            else :
                sfile_handle.close()
                if reterr :
                    log_message("Error running fls... \"" + str(reterr), "normal", message_level)
            sfile_handle.close()
            #####
            # Check if the file is empty... if it is, fls couldn't find any
            # deleted files...
            if os.stat(sfile_name).st_size == 0 :
                log_message("Sorry, not able to find any deleted files in " + \
                            "this image...", "normal", message_level)
                sys.exit(80)
            else :
                log_message("fls found some files...", "verbose", message_level)

    return str(sfile_name)


def is_file_valid(myfile="", message_level="normal") :
    """
    Check if the file exists
    Check if it is a file
    Check if it is non-zero
    
    @author: Roy Nielsen
    """
    is_valid = True
    
    if re.match("^\s*$", str(myfile)) :
        log_message("Cannot process file: \"" + str(myfile) + "\"", "normal", message_level)
        is_valid = False
    else :
        if not os.path.exists(str(myfile)) :
            log_message("File: \"" + str(myfile) + "\" does not exist...", "normal", message_level)
            is_valid = False
        else :
            if not os.path.isfile(str(myfile)) :
                log_message("File: \"" + str(file) + "\" is not a file...", "normal", message_level)
                is_valid = False
            else :
                if not os.stat(myfile).st_size > 0 :
                    log_message("I think \"" + str(file) + "\" is an empty file...", "normal", message_level)
                    is_valid = False
                else :
                    is_valid = True
                
    return is_valid

        
def is_root_dir_found(type1="", type2="", filename="", root_dir="", message_level="normal") :
    """
    Look for the root_dir in the filename full path...
    
    Returns True if dir found in filename full path
            False if dir not found in filename full path
            
    @author: Roy Nielsen
    """
    found = False
    if re.match("^\s*$", type1) or \
       re.match("^\s*$", type2) or \
       re.match("^\s*$", filename) or \
       re.match("^\s*$", root_dir) :
        log_message("Cannot process looking for the \"root dir\" with empty " + \
                    "parameters...", "normal", message_level)
        log_message("type1:\t " + str(type1), "normal", message_level)
        log_message("type2:\t " + str(type2), "normal", message_level)
        log_message("filename:\t " + str(filename), "normal", message_level)
        log_message("root_dir:\t " + str(root_dir), "normal", message_level)
        log_message("Exiting...", "normal", message_level)
        sys.exit(250)
    else :
        dirs = filename.split("/")
        if len(dirs) > 1 :
            if not re.match("^d$", type1) and not re.match("^d$", type2) :
                dirs = dirs[:-1]
            for dir in dirs :
                if re.match("%s"%dir, root_dir) :
                    found = True
                    break

    return found


def create_directory(name="", target="", message_level="normal") :
    """
    Create a directory in the target based on the name passed in.
    
    @author: Roy Nielsen
    """
    #####
    # Check for valid parameters passed in...
    if re.match("^\s*$", name) or re.match("^\s*$", target) :
        log_message("Sorry, you need a valid name and target...", "normal", message_level)
        log_message("name passed in: \"" + str(name) + "\"", "normal", message_level)
        log_message("target passed in: \"" + str(target) + "\"", "normal", message_level)
    else :
        #####
        # create list of dirs in dirname (if directory name passed in is something 
        # like one/two/three
        dirs = name.split("/")
        
        if len(dirs) > 0 :
            path = ""
            #####
            # Loop through dirs
            for dir in dirs :
                path = os.path.join(path, dir)
                full_path = os.path.join(target, path)
                
                #####
                # Check if name exists on target
                if os.path.exists(full_path) :
                    if not os.path.isdir(full_path) :
                        #####
                        # Log error and return...
                        log_message("ERROR: name: \"" + str(full_path) + "\" " + \
                        "exists, and is not a directory... Skipping...", \
                        "normal", message_level)
                        break
                    else :
                        #####
                        # go to the next level and try again...
                        continue
                else :
                    try :
                        #####
                        # path does not exist, so let's create it...
                        os.makedirs(full_path, 0755)
                    except Exception, err :
                        log_message("Exception attempting to create directory:" + \
                                    " \"" + str(full_path) + "\"", "normal", message_level)
                        log_message("Associated exception: \"" + str(err) + "\"", \
                                    message_level)


def recover_file(node="", 
                 filename="",
                 flsfile="",
                 filesystem="", 
                 source="", 
                 target="", 
                 rootdir="", 
                 icat="",
                 message_level="normal") :
    """
    Recover the filename passed in to the target.
    
    @author: Roy Nielsen
    """
    if re.match("^\s*$", str(node)) or \
       re.match("^\s*$", str(filename)) or \
       re.match("^\s*$", str(flsfile)) or \
       re.match("^\s*$", str(filesystem)) or \
       re.match("^\s*$", str(source)) or \
       re.match("^\s*$", str(target)) or \
       re.match("^\s*$", str(rootdir)) or \
       re.match("^\s*$", str(icat)) :
        log_message("Cannot recover filename: \"" + str(filename) + \
                    "\" with any empty parameters:", \
                    "normal", message_level)
        log_message("node:\t\"" + str(node) + "\"", "normal", message_level)
        log_message("filename:\t\"" + str(filename) + "\"", "normal", message_level)
        log_message("flsfile:\t\"" + str(flsfile) + "\"", "normal", message_level)
        log_message("filesystem:\t\"" + str(filesystem) + "\"", "normal", message_level)
        log_message("source:\t\"" + str(source) + "\"", "normal", message_level)
        log_message("target:\t\"" + str(target) + "\"", "normal", message_level)
        log_message("rootdir:\t\"" + str(rootdir) + "\"", "normal", message_level)
        log_message("icat:\t\"" + str(icat) + "\"", "normal", message_level)
        log_message("Exiting...", "normal", message_level)
        sys.exit(252)
        
    else :
        if os.path.exists(str(icat)) and os.path.isfile(str(icat)) :
            
            #####
            # Create directories on the target if they don't exist...
            dirs = filename.split("/")[:-1]
            if dirs :
                dir = "/".join(dirs)
                log_message("Directory of file to restore is: \"" + str(dir) + \
                            "\"...", "verbose", message_level)

                create_directory(dir, target, message_level)
            
            #####
            # open a filehandle to the file that we want subprocess to write to...
            try :
                full_file_path = os.path.join(str(target), str(filename))
                fh = open(str(full_file_path), "wb")
            except Exception, err :
                log_message(" Cannot open file...", "normal", message_level)
                log_message("file: \"" + full_file_path + "\"", "normal", message_level)
                log_message("Associated exception: \"" + str(err) + "\"", \
                            "normal", message_level)
                if re.search("[N|n][O|o] [S|s]pace [L|l]eft", str(err)) :
                    log_message("It appears there is no space left on " + \
                                "target: \"" + str(target) + "\"", \
                                "normal", message_level)
                    log_message("Exiting...", "normal", message_level)
                    sys.exit(251)
            else :
                #####
                # Set up the icat recovery command 
                # THIS MAY BE DANGEROUS WITH VERY LARGE FILES....
                command = [icat, "-f", str(filesystem), source, node]
                log_message("command: \"" + " ".join(command) + "\"", "verbose", message_level)
                try :
                    reterr = Popen(command, stdout=fh, stderr=PIPE).communicate()[1]
                    if reterr :
                        log_message("icat spawned with subprocess returned " + \
                                    "this: \"" + str(reterr) + "\"", \
                                    "normal", message_level)
                except Exception, err :
                    log_message("Exception attemting to restore file: \"" + \
                                str(filename) + "\" with exception: \"" + \
                                str(err), "normal", message_level)
                else :
                    log_message("Completed recovery of file: \"" + \
                                str(filename) + "\"", "debug", message_level)
                fh.close()
                if os.stat(str(full_file_path)).st_size == 0 :
                    log_message("Unable to recover file: \"" + \
                                str(full_file_path) + "\"", \
                                "verbose", self.message_level)
        else :
            log_message("Invalid icat \"" + str(icat) + "\"...", "normal", message_level)
            log_message("Exiting...", "normal", message_level)
            sys.exit(250)


def do_icat(flsfile="", 
            filesystem="", 
            source="", 
            target="", 
            rootdir="", 
            icat ="", 
            message_level="normal") :
    """
    Perform icat operations on the bitstream image.

    @author: Roy Nielsen
    """
    if re.match("^\s*$", str(flsfile)) or \
       re.match("^\s*$", str(filesystem)) or \
       re.match("^\s*$", str(source)) or \
       re.match("^\s*$", str(target)) or \
       re.match("^\s*$", str(rootdir)) or \
       re.match("^\s*$", str(icat)) :
        log_message("Cannot process flsfile with any empty parameters:", \
                    "normal", message_level)
        log_message("flsfile:\t\"" + str() + "\"", "normal", message_level)
        log_message("filesystem:\t\"" + str() + "\"", "normal", message_level)
        log_message("source:\t\"" + str() + "\"", "normal", message_level)
        log_message("target:\t\"" + str() + "\"", "normal", message_level)
        log_message("rootdir:\t\"" + str() + "\"", "normal", message_level)
        log_message("icat:\t\"" + str() + "\"", "normal", message_level)
        log_message(": \"" + str() + "\"", "normal", message_level)
        log_message(": \"" + str() + "\"", "normal", message_level)
        log_message("Exiting...", "normal", message_level)
        sys.exit(253)
        
    if is_file_valid(str(flsfile), message_level) :
        #####
        # Set up regular expression
        if re.match("^fat$", str(filesystem)) :
            reline = re.compile("(\w)/(\w)\s+\S+\s+(\d+):(\s+)(\S.*)")
        elif re.match("^hfs$", str(filesystem)) :
            reline = re.compile("(\w)/(\w)\s+(\d+):(\s+)(\S.*)")

        #####
        # Processing FLS file...
        # Read the file line by line - with fileinput - reads one line, so
        # you can process it, then throws it away so you can read the next line,
        # and so on.  Use this so you don't have to load the whole file into
        # memory
        for line in fileinput.input([flsfile]) :
            file_info = reline.match(line)
            if file_info :
                col1 = file_info.group(1)
                col2 = file_info.group(2)
                node = file_info.group(3)
                spaces = file_info.group(4)
                filename = file_info.group(5)
    
                #log_message(str(col1) + "/" + str(col2) + " " + str(node) + ":" + \
                #            str(spaces) + str(filename), "debug", message_level)
    
                if is_root_dir_found(col1, col2, filename, rootdir, message_level) :
                    if re.match("^d$", col1) and re.match("^d$", col2) :
                        #####
                        # If the fls entry is a directory create it.
                        log_message("Creating directory: \"" + filename + "\"", "verbose", message_level)
                        create_directory(filename, target, message_level)
    
                    #####
                    # if re.match("^?????$", col1 and re.match("^???$", col2) :
                        #####
                        # If the fls entry is a link??? Hard vs Soft??
                    
                    if re.match("^r$", col1) and re.match("^r$", col2) :
                        #####
                        # If the fls entry is a file, recover it.  Call function to do so.
                        recover_file(node, filename, flsfile, filesystem, source, target, rootdir, icat, message_level)
            else :
                #log_message("Line does not match...", "verbose", message_level)
                #log_message("line: \"" + str(line) + "\"", "debug", message_level)
                pass       
        log_message("Done with recovery of files with rootdir of: " + str(rootdir), "normal", message_level)
    else :
        log_message("Cannot find the flsfile: \"" + str(flsfile) + "\"", "normal", message_level)

        
def main() :
    """
    Main program
    
    @author: Roy Nielsen
    """
    program_options = ProgramOptions()
    message_level = program_options.get_message_level()
    
    log_message("Successfully acquired program options.", "verbose", message_level)
    
    flsfile = do_fls(program_options.get_fs_type(), \
              program_options.get_source(), \
              program_options.get_fls(), \
              program_options.get_message_level())
    
    log_message("Completed fls command.", "verbose", message_level)
    
    do_icat(flsfile, \
            program_options.get_fs_type(), \
            program_options.get_source(), \
            program_options.get_target(), \
            program_options.get_root_dir(), \
            program_options.get_icat(), \
            program_options.get_message_level())
    
    log_message("Completed icat command.", "verbose", message_level)
    
    log_message(sys.argv[0] + " done...", "verbose", message_level)


if __name__ == "__main__" :
    """
    Call main function and exit
    
    @author: Roy Nielsen
    """
    sys.exit(main())
