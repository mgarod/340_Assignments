"""
Title:          ProcessControlBlock.py
Author:         Michael Garod
Date Created:   3/7/16
Class:          CSCI 340-01, Tues & Fri 3:45PM - 5:00PM
Professor:      Eric Schweitzer
Purpose:        Project #1
Description:    Defines a PCB--the content of all queues in the OS class
Note:           Makes use of valid.validate_device_number() to validate
                that the user inputs a positive integer
"""
import Validators as valid


class PCB:
    def __init__(self, pid):
        self.id = pid
        self.filename = None
        self.memstart = None
        self.rw = None
        self.length = None

    def clear(self):
        self.filename = None
        self.memstart = None
        self.rw = None
        self.length = None

    def set_full_process(self):
        self.filename = raw_input(">>> Name of file: ")
        self.memstart = valid.validate_device_number(">>> Starting Memory: ")
        self.rw = valid.validate_r_w(">>> Read(r) or Write(w): ")
        if self.rw == "w":
            self.length = valid.validate_device_number(">>> Length of file: ")
        else:
            self.length = "n/a"

    def set_printer_process(self):
        self.filename = raw_input(">>> Name of file: ")
        self.memstart = valid.validate_device_number(">>> Starting Memory: ")
        self.rw = 'w'
        self.length = valid.validate_device_number(">>> Length of file: ")
