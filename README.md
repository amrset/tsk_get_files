tsk_get_files
=============

Recover deleted files based on a search string.  Wraps "fls" and "icat" from The Sleuth Kit: http://www.sleuthkit.org/sleuthkit/
 
tsk_get_files is a script that uses "The Sleuth Kit" commands "fls" and "icat" 
to rebuild a file structure from a disk image.  Although TSK is intended for 
use forensics purposes, this script can be used when a user's home directory is 
accidentally removed, either by an admin or a user.

The main purpose of this script is to wrap the "fls" and "icat" TSK utilities
to recover files based on a search string.

For instance if a user - "amrset" - lost his home directory - one could run:

   tsk_get_files.py -r amrset -s imageToRecoverFrom.img -t /tmp

and it will recover files from the image that have "amrset" in the path, found 
by "fls"

TSK is required to be available to tsk_get_files.py to function.  Specifically
the "fls" and "icat" commands.

WARNING: TSK and this script could be used on an attached disk, such as giving 
the source path as /dev/sdb, however that can be dangerous.  It's faster than 
creating a binary image first, but if not careful, the deleted data can be 
damaged.

The Sleuth Kit(TSK) can be found at: http://www.sleuthkit.org/sleuthkit/

------------------------------------------------------------------------------
<code>
Usage:   tsk_get_files.py [options]

Message levels are mutually exclusive.  The messages print to both the screen 
and to syslog.  

Default is to print "Normal" messages to the screen.

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -m LEVEL, --message-level=LEVEL
                        How verbose to be.  Default is "normal"
  -q, --quiet           Don't print status messages
  -v, --verbose         Print status messages
  -d, --debug           Print debug messages
  --fls=FLS             Location of the fls executable,  if not in the user's
                        path.  OPTIONAL parameter.
  --icat=ICAT           Location of the icat executable,  if not in the user's
                        path.  OPTIONAL parameter.
  -r ROOT, --root-dir=ROOT
                        Directory you want to recover.  REQUIRED parameter.
  -s SOURCE, --source-dir=SOURCE
                        Source - location of the bitstream image.  REQUIRED
                        parameter.
  -t TARGET, --target-dir=TARGET
                        Target or destination directory to copy data to.
                        REQUIRED parameter.
  -f FILESYSTEM, --filesystem-type=FILESYSTEM
                        Filesystem type to analyze.  Valid filesystems can
                        come from "The Sleuth Kit"'s "fls -f list" command.
                        REQUIRED parameter.
</code>
