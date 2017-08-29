#!/usr/bin/python

import sys
import argparse
from RunCmdPy import RunCmd

cmd_runner = RunCmd()

# ---------------------------------------------------------------------
def parse_parms(cmd_parms):
    """

    :param cmd_parms: Command-line parameters
    :type cmd_parms:  array of strings
    :return: command parameters
    :rtype: list
    """
    cmd_parm_cnt = len(cmd_parms) - 1

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
    parser.add_argument('-m', '--mode', help="Mode to run", required=False, default="normal", dest="run_mode")

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

def save_file_dirs(dirlist):

    for dir in dirlist:
        print(">>> INFO: <dir={}>".format(dir))


# ---------------------------------------------------------------------
def main():
    print("\nRunning main() function")
    input_args = parse_parms(sys.argv)
    dirs = read_dirfile(input_args.dirfile)
    save_file_dirs(dirs)
    return 0


# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
if __name__ == "__main__":
    # execute only if run as a script
    main()
    exit(0)
