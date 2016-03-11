"""
Title:          CentralProcessingUnit.py
Author:         Michael Garod
Date Created:   3/7/16
Class:          CSCI 340-01, Tues & Fri 3:45PM - 5:00PM
Professor:      Eric Schweitzer
Purpose:        Project #1
Description:    Defines a CPU--the head of the Ready Queue
Note:           Makes use of valid.validate_device_number() to validate
                that the user inputs a positive integer. Raises exceptions
                that will be caught in Main.py
"""
class CPU:
    def __init__(self):
        """Class which holds the item at the front of the Ready Queue"""
        self.process = None

    def load(self, pcb):
        """
        Set the process with the given PCB Object

        Args:
            pcb: A properly constructed PCB with unique PID
        """
        self.process = pcb

    def unload(self):
        """
        Command 't': Pop and return the current process of the CPU
        Also used during system calls to move the process to a device queue
        """
        if not self.empty():
            temp = self.process
            self.process = None
            return temp
        else:
            raise StandardError("CPU is empty, cannot terminate any process")

    def empty(self):
        """Return True if there is no current process in the CPU"""
        if self.process is None:
            return True
        else:
            return False
