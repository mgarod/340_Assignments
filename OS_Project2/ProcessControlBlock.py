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
-------------------------------------------------------------------------------
Update:         4/10/16
Purpose:        Project #2
Description:    Add accounting information and methods to PCB for ReadyQueue.
                Add cylinder data to PCB for Disk.
                Add reporting when terminated.
"""
import Validators as valid


class PCB:
    def __init__(self, pid, tau_init, alpha):
        self.id = pid
        self.filename = None
        self.memstart = None
        self.rw = None
        self.length = None
        self.cylinder = None

        # Accounting stuff
        self.tau_current = tau_init  # The value that will be kept for recursion
        self.working_tau = tau_init  # The value to be considered in preempting
        self.alpha = alpha
        self.current_burst = 0
        self.total_burst = 0
        self.cpu_uses = 0

    def clear(self):
        self.filename = None
        self.memstart = None
        self.rw = None
        self.length = None
        self.cylinder = None

    def set_full_process(self):
        self.filename = raw_input(">>> Name of file: ")
        self.memstart = valid.validate_pos_int(">>> Starting Memory: ")
        self.rw = valid.validate_r_w(">>> Read(r) or Write(w): ")
        if self.rw == "w":
            self.length = valid.validate_pos_int(">>> Length of file: ")
        else:
            self.length = "n/a"

    def set_printer_process(self):
        self.filename = raw_input(">>> Name of file: ")
        self.memstart = valid.validate_pos_int(">>> Starting Memory: ")
        self.rw = 'w'
        self.length = valid.validate_pos_int(">>> Length of file: ")

    def set_disk_process(self, c):
        """
        :param c: The maximum cylinder of the selected disk
        :return:
        """
        self.filename = raw_input(">>> Name of file: ")
        self.memstart = valid.validate_pos_int(">>> Starting Memory: ")
        self.rw = valid.validate_r_w(">>> Read(r) or Write(w): ")
        if self.rw == "w":
            self.length = valid.validate_pos_int(">>> Length of file: ")
        else:
            self.length = "n/a"
        self.cylinder = \
            valid.validate_pos_int_less_than(">>> Cylinder location: ", c)

    # NEW ADDITIONS IN PROJECT 2

    def increment_burst(self):
        """
        Used for both system calls and interrupts.
        Ask how much CPU time was given to the process.

        :return: none
        """
        burst = valid.validate_pos_float(">>> How long was pid {} "
                                              "in the CPU?: ".format(self.id))
        self.working_tau -= burst
        self.current_burst += burst
        self.total_burst += burst

    def end_burst(self):
        """
        Burst Ends with a system call:
        1) Ask for last burst, then add that to the current burst
        2) Increase the total burst this process has used
        3) CPU Uses increases by 1 (used for averaging)
        4) Recalculate Tau
        5) The next estimated burst is that recalculated Tau
        6) Reset the current burst

        :return: none
        """
        self.increment_burst()
        self.cpu_uses += 1
        self.tau_current = ((1 - self.alpha) * self.tau_current) + \
                           (self.alpha * self.current_burst)
        self.working_tau = self.tau_current
        self.current_burst = 0

    def get_avg(self):
        if self.cpu_uses == 0:
            return self.total_burst
        else:
            return self.total_burst / self.cpu_uses

    def terminal_accounting(self):
        self.increment_burst()
        self.cpu_uses += 1
        print "{:>15} | {:>10}".format("PID", self.id)
        print "{:>15} | {:>10}".format("Total CPU Burst", self.total_burst)
        print "{:>15} | {:>10}".format("Avg. CPU Burst", self.get_avg())
