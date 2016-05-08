"""
Title:          Validators.py
Author:         Michael Garod
Date Created:   3/7/16
Class:          CSCI 340-01, Tues & Fri 3:45PM - 5:00PM
Professor:      Eric Schweitzer
Purpose:        Project #1
Description:    Provides necessary validation functions for the OS class
Note:           validate_device_number() is also used to validate any
                input to be a positive integer. Raises many exceptions that
                will be caught in Main.py
-------------------------------------------------------------------------------
Update:         4/10/16
Purpose:        Project #2
Description:    Add validators for floats.
                Add validator for cylinder (pos_int_less_than)
-------------------------------------------------------------------------------
Update:         4/26/16
Purpose:        Project #3
Description:    Add:
                    - validator for power of 2
                    - validator for mulitple
                    - validator for hexadecimals
                    - validator for logical address (in hex)
                    - convert from decimal to hex
"""
import OperatingSystem as opsys


def validate_pos_int(message):
    """
    :param message: Message to show to the user

    Enforce that the user input a positive integer from the keyboard.
    :return num: The positive integer
    """
    good_number = False
    num = None

    while not good_number:
        try:
            num = int(raw_input(message))

            if num <= 0:
                raise ValueError("Please input only a positive integer")

            good_number = True
        except Exception as e:
            print e

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
    S. = snapshot of current device [r, p, d, c, j, m]
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
    except Exception:
        raise ValueError("Invalid Command")


def validate_snapshot(message):
    """
    Enforce that the user inputs one of the following:
        ['p', 'd', 'c', 'r', 'j', 'm']

    :param message: The string to be displayed to the user
    :return: One of the following ['p', 'd', 'c', 'r', 'j', 'm']
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
        except Exception as e:
            print e

    return num


def validate_pos_float(message):
    """
    Enforce that the user inputs a float

    :param message: The string to be displayed to the user
    :return: The positive float
    """
    good_number = False
    num = None

    while not good_number:
        try:
            num = float(raw_input(message))

            if num < 0:
                raise ValueError("Please input only a positive float")

            good_number = True
        except Exception as e:
            print e

    return num


def validate_pos_int_less_than(message, max):
    """
    Enforce that the user enters a positive integer less than max.

    :param message: The string to be displayed to the user
    :param max: The upper limit of what the user may enter
    :return: Float
    """
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
        except Exception as e:
            print e

    return num


def validate_power_2(message):
    """
    Enforce that the user input a power of 2 from the keyboard.

    :param message: Message to show to the user
    """
    good_number = False
    num = None

    while not good_number:
        try:
            num = int(raw_input(message))
            if (num < 1) or ((num & (num - 1)) != 0):
                raise ValueError("Please input only some 2^n where n>=0")

            good_number = True
        except Exception as e:
            print e

    return num


def validate_pos_int_multiple(message, factor):
    """
    :param message: Message to show to the user
    :param factor: User input must be a multple of factor

    Enforce that the user input a positive integer from the keyboard
    and enforce that the input is a multiple of factor
    """
    good_number = False
    num = None

    while not good_number:
        try:
            num = int(raw_input(message))

            if num <= 0:
                raise ValueError("Please input only a positive integer")
            elif num < factor:
                raise ValueError(
                    "Please input a number larger than {}".format(factor))
            elif num % factor != 0:
                raise ValueError(
                    "Input number must be a multiple of {}".format(factor))

            good_number = True
        except Exception as e:
            print e

    return num


def validate_hex(message, p):
    """
    :param message: Message to show to the user
    :param p: The PCB to which we are accepting a logical address in hex

    Enforce that the user input a non-negative hexadecimal number within the
    process' logical address space
    :return deciimal
    """
    good_number = False
    hexa = None
    num = None

    while not good_number:
        try:
            hexa = raw_input(message)
            num = int(hexa, 16)

            if num < 0:
                hexa = None
                raise ValueError("Please input only a positive hexadecimal "
                                 "number (e.g. F28A)")
            if num > p.mem_usage:
                hexa = None
                raise ValueError("This logical address is out of bounds.\n" +
                                 "Process size is {} (in decimal)".format(
                                     p.mem_usage))

            good_number = True
        except Exception as e:
            print e

    print "--- You have entered {} (hex), {} (dec)".format(hexa, num)
    return num


def convert_dec_to_hex(d):
    """
    Accept a decimal (base 10) number and return its simplified, uppercase hex
    representation (string).

    Example: 254 will return 'FE', instead of '0xfe'

    This is a private method used after validation, therefore no need to
    loop until correct, because the input will always be correct.

    :param d: A decimal number
    :return: String
    """
    try:
        d = int(d)
        return str(hex(d)[2:]).upper()
    except Exception:
        raise ValueError("Please only input a decimal number")
