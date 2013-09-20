#!/usr/bin/env python
import os
import sys

def main(arguments=None):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fvgui.settings")

    from django.core.management import execute_from_command_line

    print sys.argv

    if not arguments == None:
        execute_from_command_line(arguments)
    else:
        execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()