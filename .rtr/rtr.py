#!/usr/bin/python3

# Copyright (C) 2023-2024, RV Bionics Group SpA.
# Created by RV Bionics Group SpA. <info@rvbionics.com>.
# This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

import argparse
import logging
import sys
import os

from rtrtests import (cppcheck, clangformat, build, unittests, docs)

TESTS = {
    "cppcheck": cppcheck,
    "format": clangformat,
    "build": build,
    "ut": unittests,
    "docs": docs
}


def init_argparse():
    """Setup argparse for handle command line parameters.

    Returns:
        object: argparse parser object
    """
    parser = argparse.ArgumentParser(
        description="Tool to execute code quality validations."
    )
    parser.add_argument(
        "-V", help='Version and license message',
        action="store_true",
        dest='version'
    )
    parser.add_argument(
        "-t", "--test", help='Test to execute. If omitted, all tests will be executed',
        action="append",
        dest='tests',
        choices=list(TESTS.keys())
    )
    parser.add_argument(
        "-i", "--ignore", help='Ignore directories',
        action="append",
        dest='ignore',
    )
    parser.add_argument(
        "-q", help='Quiet execution',
        dest='quiet',
        action="store_true"
    )
    parser.add_argument(
        '-v', help='Verbose',
        dest='verbose',
        action='store_true'
    )
    parser.add_argument(
        '-o', help='Output directory',
        dest='output',
        required=True
    )
    parser.add_argument(
        '-s', help='Source directory',
        dest='source',
        required=True
    )
    parser.add_argument(
        '-u', help='Output owner user id',
        dest='uid',
        required=True
    )
    parser.add_argument(
        '-g', help='Output owner group id',
        dest='gid',
        required=True
    )

    return parser


def backup_permissions(dirlist):
    for directory in dirlist:
        os.system(f'getfacl -p -R {directory} > {directory}.acl')


def restore_permissions(dirlist):
    for directory in dirlist:
        os.system(f'setfacl --restore={directory}.acl')
        os.unlink(f'{directory}.acl')


def set_output_permissions(dirlist, uid, gid):
    for directory in dirlist:
        os.system(f'chown -R {uid}:{gid} {directory}')


def main():
    """RTR tool main function
    """
    # Parse cmdline args
    results = True
    parser = init_argparse()
    args = parser.parse_args()
    init_logger(args)

    backup_permissions([args.source])
    if args.tests is None:
        args.tests = TESTS.keys()

    for test in args.tests:
        results = TESTS[test](args) and results
    restore_permissions([args.source])
    set_output_permissions([args.output], args.uid, args.gid)
    sys.exit(not int(results))


def init_logger(args):
    """[summary]

    Args:
        args ([type]): [description]
    """
    # Default logger configs
    logger_level = 'INFO'
    logger_fmt = '%(message)s'

    # Debug level if requested
    if args.verbose:
        logger_level = 'DEBUG'
        logger_fmt = '%(asctime)-15s %(module)s[%(levelname)s] %(message)s'

    # Handle quiet request
    if args.quiet:
        logger_level = 'ERROR'
        logger_fmt = ''

    # Set logging configs
    logging.basicConfig(format=logger_fmt, level=logger_level)


if __name__ == "__main__":
    main()
