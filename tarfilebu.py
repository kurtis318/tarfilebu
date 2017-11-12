#!/usr/bin/python

import sys
import os
import argparse
from RunCmdPy import RunCmd
from UniqueDir import UniqueDir

cmd_runner = RunCmd()
u_dir = UniqueDir()

NORMAL_MODE = "normal"
TEST_MODE = "test"
BLANKS16=' '*16
BLANKS20=' '*20
DOTS_TAR_DIR_FILE="__DOTDIRS__"
DOTS_TAR_FILE_FILE="__DOTFILES__"
KVM_IMAGE_DIR="/var/lib/libvirt/images"
# KVM_IMAGE_DIR="/ssd2/var.lib.libvirt.images"
KVM_SAVE_DIR="__KVM_IMAGES__"

def parse_parms(cmd_parms):
    """
    Parse the command line parameters only.  No verification is done.
    
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

    # Here are options with values after the option
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', 
                        help="Directory list file", 
                        required=True, 
                        dest="dirfile")
    
    parser.add_argument('-s', '--srcdir', 
                        help="Source directory", 
                        required=True, 
                        dest="srcdir")
    
    parser.add_argument('-p', '--pattern',
                        help='Sub-directory pattern',
                        required=True,
                        dest='pattern')
    
    parser.add_argument('-t', '--todir', 
                        help="Target directory", 
                        required=True, 
                        dest="tardir")
 
    # Here are optional parameters   
    parser.add_argument('-m', '--mode', 
                        help="Mode to run", 
                        required=False, 
                        choices=[NORMAL_MODE,TEST_MODE],
                        default=NORMAL_MODE, 
                        dest="run_mode")

    parser.add_argument('-z', '--pdsize', 
                        help='Max number of output dirs',
                        required=False,
                        default=5, 
                        dest="max_dir_count")

    # Here are options that have boolean values.  Notice  action=
    parser.add_argument('-a', '--all', 
                        action='store_true',
                        help="Backup all directories", 
                        required=False, 
                        default=False, 
                        dest="backup_all")
    parser.add_argument('-k', '--kvm', 
                        action='store_true',
                        help='Backup kvm direcotry', 
                        required=False, 
                        default=False, 
                        dest="backup_kvm")

    parser.add_argument('-d', 
                        action='store_true', 
                        help='include dot files', 
                        required=False, 
                        default=False, 
                        dest="dodots") 

    # Perform parsing and issue messages.
    args = parser.parse_args()

    print(">>> Parameters are correct.")
    print("<args={}>".format(args))
    return args     # parse_parms()

def read_dirfile(fname):
    """
    Private utility function to read the file that contains list of directories to backup.
    
    :param fname: Full directory file path
    :return: connents of directory file
    :rtype: list
    """
    
    print(">>> read_dirfile(): <fname={}>".format(fname))
    cmd_runner.run("awk '!/^ *#/ && NF' {}".format(fname))
    if cmd_runner.get_rc != 0:
        print(">>> ERROR: <rc={}>".format(cmd_runner.get_rc))
        return 1
    print(">>> INFO: stdout follows")
    cmd_runner.dump_stdout()
    return cmd_runner.get_stdout        # read_dirfile()

def compute_dir_size_human_readable(fullpath):
    """
    Private utility function to read the file that contains list of directories to backup.
    
    :param fullpath: Full path to a directory
    :return: human-readable size of directory
    :rtype: string
    """
    
    cmd_runner.run("du -sh " + fullpath + "|awk '{print $1;}'")
    if cmd_runner.rc == 0:
        hr_size = cmd_runner.get_stdout[0]
    else:
        hr_size = "error"
    return hr_size      # compute_dir_size_human_readable()

def count_num_files_dirs(path):
    """
    Private utility function that counts files and directories in a given directory.
    
    :param path: Full path to a directory to have counted
    :return: (number of files, number of directories)
    :rtype: (int, int)
    """

    files = folders = 0

    for _, dirnames, filenames in os.walk(path):
        # ^ this idiom means "we won't be using this value"
        files += len(filenames)
        folders += len(dirnames)

    # print "{:,} files, {:,} folders".format(files, folders)

    return(files,folders)       # count_num_files_dirs()

# REF: https://www.tecmint.com/monitor-copy-backup-tar-progress-in-linux-using-pv-command/
# create tar file using pv command:
#        tar -czf - ./Downloads/ | (pv -p --timer --rate --bytes > backup.tgz)
# Simple file copy:
#         pv opensuse.vdi > /tmp/opensuse.vdi
#
def save_dirs(sdir, tdir, dirlist, mode):
    """
    Private utility function that saves a list of directories to new directory.
    
    :param sdir: Full path to source directory to backup
    :param tdir: Full path to target directory
    :param dirlist: List of directories in source directory to backup
    :param mode: normal (run tar command) or test (just simulate running)
    :return: nothing
    :rtype: nothing
    """

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
    return      # save_dirs()

def save_all_dot_dirs(sdir, tdir, mode):
    """
    Private utility function that saves all directories in source directory that begin with a dot.
    
    :param sdir: Full path to source directory to backup
    :param tdir: Full path to target directory
    :param mode: normal (run tar command) or test (just simulate running)
    :return: nothing
    :rtype: nothing
    """
    
    # Generate list of dirs that start with a dot.  Must cd to base dir and then use find. Easier to grep.
    awk_pgm = "awk '{print substr($1,3);}'"
    cmd='cd {}; find . -maxdepth 1 -type d|grep "^\./\."|{}|xargs'.format(sdir, awk_pgm)
    cmd_runner.run(cmd)
    
    if cmd_runner.get_rc != 0:
        print "{} WARN: Cannot find dot directories in directory {}".format(BLANKS16, sdir)
        print(">>> WARN: stderr follows:")
        cmd_runner.dump_stderr()   
        return
    
    # There should be ONLY 1 string returned which is blank delimited list of dirs beginning with dot.
    dirlist = cmd_runner.get_stdout[0]
    
    base_tar_opts = '-C {} -p '.format(sdir)

    # Need to output to "special" tar file name.
    tar_file_path = '{}/{}.tar'.format(tdir,DOTS_TAR_DIR_FILE)

    # If tar file already exists, add update flag
    if os.path.isfile(tar_file_path):
        tar_opts = base_tar_opts + ' -uf'
    else:
        tar_opts = base_tar_opts + ' -cf'

    # Now we have all the pieces to build a tar command.
    cmd = 'tar {} {} {}'.format(tar_opts, tar_file_path, dirlist)
    print ">>> INFO: Found <dirlist={}>".format(dirlist)
    
    # Caller decides if this is a NORMAL (tar command run) or a test (just print tar command)        
    print("{}<mode={}> <cmd={}>".format(BLANKS16, mode, cmd))
    msecs = cmd_runner.elaspe_time_run(cmd, mode)
    print("{}<rc={}> Elapased time={}".format(BLANKS16,
                                              cmd_runner.get_rc,
                                              cmd_runner.ms_2_human_readable(msecs)))
    if cmd_runner.get_rc != 0:
        print(">>> ERROR: stderr follows:")
        cmd_runner.dump_stderr()   
    
    return      # save_all_dot_dirs()

def save_all_dot_files(sdir, tdir, mode):
    """
    Private utility function that saves files starting with a dot in source directory.
    
    :param sdir: Full path to source directory to backup
    :param tdir: Full path to target directory
    :param mode: normal (run tar command) or test (just simulate running)
    :return: nothing
    :rtype: nothing
    """

    # Generate list of files that start with a dot.  
    awk_pgm = "awk '{print substr($1,3);}'"
    cmd='cd {}; find . -maxdepth 1 -type f|{}|xargs'.format(sdir, awk_pgm)
    cmd_runner.run(cmd)
        
    if cmd_runner.get_rc != 0:
        print "{} WARN: Cannot find dot files in directory {}".format(BLANKS16, sdir)
        print(">>> WARN: stderr follows:")
        cmd_runner.dump_stderr()   
        return
    
    # There should be ONLY 1 string returned which is blank delimited list of dirs beginning with dot.
    file_list = cmd_runner.get_stdout[0]
    
    base_tar_opts = '-C {} -p --ignore-failed-read'.format(sdir)

    # Need to output to "special" tar file name.
    tar_file_path = '{}/{}.tar'.format(tdir, DOTS_TAR_FILE_FILE)

    # If tar file already exists, add update flag
    if os.path.isfile(tar_file_path):
        tar_opts = base_tar_opts + ' -uf'
    else:
        tar_opts = base_tar_opts + ' -cf'

    # Now we have all the pieces to build a tar command.
    cmd = 'tar {} {} {}'.format(tar_opts, tar_file_path, file_list)
    print ">>> INFO: Found <file_list={}>".format(file_list)
    
    # Caller decides if this is a NORMAL (tar command run) or a test (just print tar command)        
    print("{}<mode={}> <cmd={}>".format(BLANKS16, mode, cmd))
    msecs = cmd_runner.elaspe_time_run(cmd, mode)
    print("{}<rc={}> Elapased time={}".format(BLANKS16,
                                              cmd_runner.get_rc,
                                              cmd_runner.ms_2_human_readable(msecs)))
    if cmd_runner.get_rc != 0:
        print(">>> ERROR: stderr follows:")
        cmd_runner.dump_stderr()   
        
    return      # save_all_dot_files()

def save_kvm_files(tdir, mode):
    """
    Private utility function that saves kvm files in /var/lib/libvirt/images.
    
    :param tdir: Full path to target directory
    :param mode: normal (run tar command) or test (just simulate running)
    :return: nothing
    :rtype: nothing
    """
    
    if not os.path.isdir(KVM_IMAGE_DIR):
        print(">>> WARNING: Did not find <KVM_IMAGE_DIR=<{}>. Skipping saving KVM image files.".format(KVM_IMAGE_DIR))
        return
    
    # There is a directory of KVM images.  Make target directory for backup of KVM images.
    cmd_runner.run('mkdir {}/{}'.format(tdir, KVM_SAVE_DIR), mode)
    if cmd_runner.get_rc != 0:
            print(">>> ERROR: Cannot create directory {}/{} for KVM images. Skipping KVM image save.".format(tdir, KVM_SAVE_DIR))
            return
    
    # Build cp or rsync command.
    cmd_runner.run("rsync")
          
    if cmd_runner.get_rc != 1:
        cmd = "cp -p {}/* {}/{}/.".format(KVM_IMAGE_DIR, tdir, KVM_SAVE_DIR)
    else:
        cmd = "rsync -pog {}/* {}/{}/".format(KVM_IMAGE_DIR, tdir, KVM_SAVE_DIR)
    
    # Got this far, its time to backup the KVM images. 
    print(">>> INFO: Backing KVM images in {}.".format(KVM_IMAGE_DIR))
    print("{}<mode={}> <cmd={}>".format(BLANKS16, mode, cmd))
    msecs = cmd_runner.elaspe_time_run(cmd, mode)
    print("{}<rc={}> Elapased time={}".format(BLANKS16,
                                              cmd_runner.get_rc,
                                              cmd_runner.ms_2_human_readable(msecs)))
    if cmd_runner.get_rc != 0:
        print(">>> ERROR: Return code from KVM image backup was not 0.  RC={}".format(cmd_runner.get_rc))
    
    return      # save_kvm_files()

def verify_args(args):
    """
    Private utility function that verifies command-line parameters.  This function can exit script.
    
    :param args: Dictionary?? of arguments 
    :return: nothing
    :rtype: nothing
    """

    ecnt=0
    if not os.path.isfile(args.dirfile):
        ecnt+=1
        print(">>> ERROR: directory file not found <dirfile={}>".format(args.dirfile))

    if not os.path.isdir(args.srcdir):
        ecnt+=1
        print(">>> ERROR: source directory not found <srcdir={}>".format(args.srcdir))

    if not os.path.isdir(args.tardir):
        ecnt+=1
        print(">>> ERROR: target directory not found <tardir={}>".format(args.srcdir))
    else:
        
        # Let UniquDir object determine if input path is writable
        rc, args.tardir = u_dir.mkdir(args.tardir, args.pattern, args.max_dir_count)
        if rc != 0:
            print('>>> ERROR: Error creating new subdirectory in <tardir={}>'.format(args.tardir))
            exit(50)

    if ecnt:
        ecnt+=1
        print(">>> ERROR: {} argument errors found.  Aborting script now.".format(ecnt))
        exit(100)

    print(">>> INFO: No argument errors found")
    
    # Adjust the value of run mode to mathc RunCmd object
    if args.run_mode == NORMAL_MODE:
        args.run_mode = RunCmd.NORMAL_MODE
    else:
        args.run_mode = RunCmd.DEBUG_MODE
        
    return      # verify_args()


def main():
    """
    Private utility function that controls script execuction.
    
    :param none
    :return: nothing
    :rtype: nothing
    """
    print("\nRunning main() function")
    input_args = parse_parms(sys.argv)
    verify_args(input_args)
    dirs = read_dirfile(input_args.dirfile)
    save_dirs(input_args.srcdir, input_args.tardir, dirs, input_args.run_mode)
    if input_args.dodots:
        save_all_dot_dirs(input_args.srcdir, input_args.tardir, input_args.run_mode)
        save_all_dot_files(input_args.srcdir, input_args.tardir, input_args.run_mode)
        
    if input_args.backup_kvm:
        save_kvm_files(input_args.tardir, input_args.run_mode)
        
    return      # main()


if __name__ == "__main__":
    # execute only if run as a script
    main()
    exit(0)
