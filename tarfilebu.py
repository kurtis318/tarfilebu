#!/usr/bin/python

import sys
import os
import argparse
from RunCmdPy import RunCmd

cmd_runner = RunCmd()

NORMAL_MODE = "normal"
TEST_MODE = "test"
BLANKS16=' '*16
BLANKS20=' '*20
DOTS_TAR_FILE_NAME="__DOTDIRS__"

def parse_parms(cmd_parms):
    """

    :param cmd_parms: Command-line parameters
    :type cmd_parms:  array of strings
    :return: command parameters
    :rtype: list
    """
    #    cmd_parm_cnt = len(cmd_parms) - 1
    #    print(">>>parse_parms(.): Starting")
    #    print("   This is the name/path of the script:{0}".format(cmd_parms[0]))
    #    print("   Number of arguments:{0}".format(cmd_parm_cnt))
    #    print("   Argument List: {}".format(str(cmd_parms)))
    #    print(">>>parse_parms(.): Finished")

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help="Directory list file", required=True, dest="dirfile")
    parser.add_argument('-s', '--srcdir', help="Source directory", required=True, dest="srcdir")
    parser.add_argument('-t', '--todir', help="Target directory", required=True, dest="tardir")

    #    parser.add_argument('-h', '--help', help='Display help text', required=False)
    parser.add_argument('-a', '--all', help="Backup all directories", required=False, default=False, dest="backup_all")
    parser.add_argument('-k', '--kvm', help='Backup kvm direcotry', required=False, default=False, dest="backup_kvm")
    parser.add_argument('-m', '--mode', help="Mode to run", required=False, choices=[NORMAL_MODE,TEST_MODE],
                            default=NORMAL_MODE, dest="run_mode")
    parser.add_argument('-d', action='store_true', help='Unclude dot files', required=False, default=False, dest="dodots") 

    # Perform parsing and issue messages.
    args = parser.parse_args()

    print(">>> Parameters are correct.")
    print("<args={}>".format(args))
    return args

def read_dirfile(fname):
    """

    :return:    list of directories
    """
    print(">>> read_dirfile(): <fname={}>".format(fname))
    cmd_runner.run("awk '!/^ *#/ && NF' {}".format(fname))
    if cmd_runner.get_rc != 0:
        print(">>> ERROR: <rc={}>".format(cmd_runner.get_rc))
        return 1
    print(">>> INFO: stdout follows")
    cmd_runner.dump_stdout()
    return cmd_runner.get_stdout

def compute_dir_size_human_readable(fullpath):
    cmd_runner.run("du -sh " + fullpath + "|awk '{print $1;}'")
    if cmd_runner.rc == 0:
        hr_size = cmd_runner.get_stdout[0]
    else:
        hr_size = "error"
    return hr_size

def count_num_files_dirs(path):
    files = folders = 0

    for _, dirnames, filenames in os.walk(path):
        # ^ this idiom means "we won't be using this value"
        files += len(filenames)
        folders += len(dirnames)

    # print "{:,} files, {:,} folders".format(files, folders)

    return(files,folders)

def save_dirs(sdir, tdir, dirlist, mode):

    for __dir in dirlist:

        fullpath=sdir + "/" + __dir
        if os.path.exists(fullpath):
            print(">>> INFO: found <dir={}> <fullpath={}>".format(__dir,fullpath))
        else:
            print(">>> WARN: could not find <dir={}> <fullpath={}>. Skipping request.".format(__dir,fullpath))
            continue

        # Determine human readable size of directory
        human_readable_size = compute_dir_size_human_readable(fullpath)

        # Compute number of files and number of sub-directories
        (fcnt, dcnt) = count_num_files_dirs(fullpath)

        # Output stats
        print("{}<human_readable_size={}> <files={:,}> <dirs={:,}>".format(BLANKS16,human_readable_size,fcnt,dcnt))

        base_tar_opts = '-C {} -p '.format(sdir)

        tar_file_path = '{}/{}.tar'.format(tdir, __dir)

        # If tar file already exists, add update flag
        if os.path.isfile(tar_file_path):
            tar_opts = base_tar_opts + ' -uf'
        else:
            tar_opts = base_tar_opts + ' -cf'

        # Now we have all the pieces to build a tar command.
        cmd = 'tar {} {} {}'.format(tar_opts, tar_file_path, __dir)

        # Caller decides if this is a NORMAL (tar command run) or a test (just print tar command)
        print("{}<mode={}> <cmd={}>".format(BLANKS16, mode, cmd,))
        msecs = cmd_runner.elaspe_time_run(cmd, mode)
        print("{}<rc={}> Elapased time={}".format(BLANKS16,
                                                  cmd_runner.get_rc,
                                                  cmd_runner.ms_2_human_readable(msecs)))
        if cmd_runner.get_rc != 0:
            print(">>> ERROR: stderr follows:")
            cmd_runner.dump_stderr()
    return

def save_all_dot_dirs(sdir, tdir, dirlist, mode):
    
    # Generate list of dirs that start with a dot.  Must cd to base dir and then use find. Easier to grep.
    cmd='cd {}; find . -maxdepth 1 -type d|grep "^\./\."|xargs'.format(sdir)
    cmd_runner.run(cmd, mode)
    
    if cmd_runner.get_rc != 0:
        print "{} WARN: Cannot find dot files in directory {}".format(BLANKS16, sdir)
        print(">>> WARN: stderr follows:")
        cmd_runner.dump_stderr()   
        return
    
    # There should be ONLY 1 string returned which is blank delimited list of dirs beginning with dot.
    dirlist = cmd_runner.get_stdout[0]
    
    base_tar_opts = '-C {} -p '.format(sdir)

    # Need to output to "special" tar file name.
    tar_file_path = '{}/{}.tar'.format(tdir,DOTS_TAR_FILE_NAME)

    # If tar file already exists, add update flag
    if os.path.isfile(tar_file_path):
        tar_opts = base_tar_opts + ' -uf'
    else:
        tar_opts = base_tar_opts + ' -cf'

    # Now we have all the pieces to build a tar command.
    cmd = 'tar {} {} {}'.format(tar_opts, tar_file_path, dirlist)
    print ">>> INFO: Found <dirlist={}>\n{}".format(dirlist,BLANKS16)
    
    # Caller decides if this is a NORMAL (tar command run) or a test (just print tar command)        
    print("{}<mode={}> <cmd={}>".format(BLANKS16, mode, cmd))
    msecs = cmd_runner.elaspe_time_run(cmd, mode)
    print("{}<rc={}> Elapased time={}".format(BLANKS16,
                                              cmd_runner.get_rc,
                                              cmd_runner.ms_2_human_readable(msecs)))
    if cmd_runner.get_rc != 0:
        print(">>> ERROR: stderr follows:")
        cmd_runner.dump_stderr()   
    
    return

def verify_args(args):
    ecnt=0
    if not os.path.isfile(args.dirfile):
        ecnt+=1
        print(">>> ERROR: directory file not found <dirfile={}".format(args.dirfile))

    if not os.path.isdir(args.srcdir):
        ecnt+=1
        print(">>> ERROR: source directory not found <srcdir={}".format(args.srcdir))

    if not os.path.isdir(args.tardir):
        ecnt+=1
        print(">>> ERROR: target directory not found <tardir={}".format(args.srcdir))

    if ecnt:
        print(">>> ERROR: {} argument errors found.  Aborting script now.".format(ecnt))
        exit(100)
    else:
        print(">>> INFO: No argument errors found")


def main():
    print("\nRunning main() function")
    input_args = parse_parms(sys.argv)
    verify_args(input_args)
    dirs = read_dirfile(input_args.dirfile)
    save_dirs(input_args.srcdir, input_args.tardir, dirs, input_args.run_mode)
    if input_args.dodots:
        save_all_dot_dirs(input_args.srcdir, input_args.tardir, dirs, input_args.run_mode)
        
    return 0


if __name__ == "__main__":
    # execute only if run as a script
    main()
    exit(0)
