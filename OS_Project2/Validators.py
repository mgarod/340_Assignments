"""
Title:          Validators.py
Author:         Michael Garod
Date Created:   3/7/16
Class:          CSCI 340-01, Tues & Fri 3:45PM - 5:00PM
Professor:      Eric Schweitzer
Purpose:        Project #1
Description:    Provides necessary validation functions for the OS class
Note:           validate_device_number() is also used to validate any
                input to be a positive integer. Raises many exceptions that will
                be caught in Main.py
-------------------------------------------------------------------------------
Update:         4/10/16
Purpose:        Project #2
Description:    Add validators for floats.
                Add validator for cylinder (pos_int_less_than)
"""
import OperatingSystem as opsys


def validate_pos_int(message):
    """
    :param message: Message to show to the user

    Retreive a valid positive integer from the the user keyboard.
    Also used in ProcessControlBlock to simply validate a positive integer
    """
    good_number = False
    num = None

    while not good_number:
        try:
            num = int(raw_input(message))

            if num <= 0:
                raise ValueError("Please input only a positive integer")

            good_number = True
        except ValueError:
            print "Please input only a positive integer"

    return num


def validate_command(message):
    """
    :param message: input from the user keyboard

    Running portion of the OS Class

    SYSTEM CALLS
    p# = place current process on printer# queue
    d# = place current process on disk# queue
    c# = place current process on CD/RW# queue

    INTERRUPTS
    A = new process arrival
    t = terminate current process
    S. = snapshot of current device [r, p, d, c]
    P# = remove job from printer# queue, place in ready queue
    D# = remove job from disk# queue, place in ready queue
    C# = remove job from CD/RW# queue, place in ready queue
    """
    if not message:  # check if the string is the empty string
        raise ValueError("Invalid command")

    c1 = message[0] in opsys.valid_c1

    if not c1:
        raise ValueError("Invalid command")
    elif len(message) == 1:
        return c1
    else:
        return c1 and validate_c2(message[1:])


def validate_c2(m_slice):
    """
    :param m_slice: all but the first the character of user input

    Assert that this character is a valid command2
    """
    try:
        int(m_slice)
        return True
    except Exception as e:
        raise ValueError("Invalid Command")


def validate_snapshot(message):
    """
    Enforce that the user inputs one of the following: ['p', 'd', 'c', 'r']

    :param message: The string to be displayed to the user
    :return: One of the following ['p', 'd', 'c', 'r']
    """
    good_char = False
    char = None
    while not good_char:
        try:
            char = raw_input(message)

            if (len(char) != 1) or (char not in opsys.valid_snapshot_char):
                raise ValueError("Invalid Entry")
            else:
                good_char = True
        except Exception as e:
            print e

    return char


def validate_r_w(message):
    good_char = False
    char = None
    while not good_char:
        char = raw_input(message)

        if char in ['r', 'w']:
            good_char = True
        else:
            print "Please input \'r\' or \'w\'"

    return char


def validate_alpha(message):
    """
    Enforce that the user inputs a float in the range [0,1]

    :param message: The string to be displayed to the user
    :return: A float in the range [0,1]
    """
    good_number = False
    num = None

    while not good_number:
        try:
            num = float(raw_input(message))

            if not (0 <= num <= 1):
                raise ValueError("Please input only a float in range [0-1]")

            good_number = True
        except ValueError:
            print "Please input only a float in range [0-1]"

    return num


def validate_pos_float(message):
    """
    Enforce that the user inputs a float

    :param message: The string to be displayed to the user
    :return: Float
    """
    good_number = False
    num = None

    while not good_number:
        try:
            num = float(raw_input(message))

            if num < 0:
                raise ValueError("Please input only a positive float")

            good_number = True
        except ValueError:
            print "Please input only a positive float"

    return num


def validate_pos_int_less_than(message, max):
    good_number = False
    num = None

    while not good_number:
        try:
            num = int(raw_input(message))

            if num <= 0:
                raise ValueError("Please input only a positive integer")
            elif num > max:
                raise ValueError("Please enter a positive integer less "
                                 "than or equal to {}".format(max))

            good_number = True
        except ValueError as e:
            print e

    return num