#!/usr/bin/python

import sys
import argparse
from RunCmdPy import RunCmd
# ---------------------------------------------------------------------
def parse_parms(cmd_parms):
    """

    :param cmd_parms: Command-line parameters
    :type cmd_parms:  array of strings
    :return: nothing
    :rtype: none
    """
    cmd_parm_cnt = len(cmd_parms)-1

    print(">>>parse_parms(.): Starting")
    print("   This is the name/path of the script:{0}".format(cmd_parms[0]))
    print("   Number of arguments:{0}".format(cmd_parm_cnt))
    print("   Argument List: {}".format(str(cmd_parms)))
    print(">>>parse_parms(.): Finished")

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help="Directory list file", required=True)
    parser.add_argument('-s', '--srcdir', help="Source directory", required=True)
    parser.add_argument('-t', '--todir', help="Target directory", required=True)

#    parser.add_argument('-h', '--help', help='Display help text', required=False)
    parser.add_argument('-a', '--all', help="Backup all directories", required=False, default=False)
    parser.add_argument('-k', '--kvm', help='Backup kvm direcotry', required=False, default=False)
    parser.add_argument('-m', '--mode', help="Mode to run", required=False, default="")
    args = parser.parse_args()
# ---------------------------------------------------------------------
def main():
    #    test1()
    #    test2()
    print("\nRunning main() function")
    parse_parms(sys.argv)

    return 0
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
if __name__ == "__main__":
    # execute only if run as a script
    main()
    exit(0)