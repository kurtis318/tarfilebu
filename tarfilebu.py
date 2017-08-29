#!/usr/bin/python

import sys
from RunCmdPy import RunCmd

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

def main():
    #    test1()
    #    test2()
    print("\nRunning main() function")
    parse_parms(sys.argv)

    return 0


if __name__ == "__main__":
    # execute only if run as a script
    main()
    exit(0)