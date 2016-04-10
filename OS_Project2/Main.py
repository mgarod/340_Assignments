"""
Title:          Main.py
Author:         Michael Garod
Date Created:   3/7/16
Class:          CSCI 340-01, Tues & Fri 3:45PM - 5:00PM
Professor:      Eric Schweitzer
Purpose:        Project #1
Description:    Builds an OS object and perpetually waits for user input
Note:           Will not terminate. Use ctrl+c to exit.
"""
import OperatingSystem as opsys


def go():
    os = opsys.OS()

    while True:
        try:
            os.wait_for_input()
        except KeyboardInterrupt:
            print "\n\nThank you! Have a nice day"
            exit()
        except Exception as e:
            print e

go()
