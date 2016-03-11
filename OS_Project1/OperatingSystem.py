"""
Title:          OperatingSystem.py
Author:         Michael Garod
Date Created:   3/7/16
Class:          CSCI 340-01, Tues & Fri 3:45PM - 5:00PM
Professor:      Eric Schweitzer
Purpose:        Project #1
Description:    Contains the OS class which simulates a single processor
                operating system with printers, disks and CD/RW drives.
Note:           Snapshot r will also show the contents of the CPU.
                Raises many exceptions that will be caught in Main.py
"""
import collections as col
# use append() and popleft() in order to simulate a regular queue with deque
import ProcessControlBlock as pcb
import CentralProcessingUnit as cpu
import Validators as valid


""" Valid characters to be received as input """
single_commands = ['A', 't', 'S']
device_commands = ['p', 'd', 'c', 'P', 'D', 'C']
valid_c1 = ['p', 'd', 'c', 'P', 'D', 'C', 'A', 't', 'S']
valid_snapshot_char = ['p', 'd', 'c', 'r']  # And any number


class OS:
    """
    Available Commands for this OS class

    SYSTEM CALLS
    p# = place current process on printer# queue
    d# = place current process on disk# queue
    c# = place current process on CD/RW# queue

    INTERRUPTS
    A = new process arrival
    t = terminate current process
    S. = snapshot of current device [r, p, d, c] (r also prints CPU process)
    P# = remove job from printer# queue, place in ready queue
    D# = remove job from disk# queue, place in ready queue
    C# = remove job from CD/RW# queue, place in ready queue
    """

    def __init__(self):
        """
        System Generator for the OS Class.
        Will ask for number of Printers, Disks, and CD/RWs.
        Maintains a unique PID numbering system ( see get_next_id() )
        """
        self.ReadyQueue = col.deque()
        self.Printers = list()
        self.Disks = list()
        self.CDs = list()

        self.pidGenerator = 1
        self.CPU = cpu.CPU()

        self.num_printers = \
            valid.validate_device_number("> Input number of printers: ")
        self.num_disks = \
            valid.validate_device_number("> Input number of disk drives: ")
        self.num_cds = \
            valid.validate_device_number("> Input number of CD/RW drives: ")

        for i in range(self.num_printers):
            self.Printers.append(col.deque())

        for i in range(self.num_disks):
            self.Disks.append(col.deque())

        for i in range(self.num_cds):
            self.CDs.append(col.deque())

        self.devices = {
            'p': self.Printers,
            'd': self.Disks,
            'c': self.CDs
        }

        self.device_sizes = {
            'p': self.num_printers,
            'd': self.num_disks,
            'c': self.num_cds
        }

        self.action_dict = {
            'A': self.arrival_pcb,
            't': self.terminate_pcb,
            'S': self.snapshot,
            'p': self.system_call,
            'd': self.system_call,
            'c': self.system_call,
            'P': self.interrupt,
            'D': self.interrupt,
            'C': self.interrupt
        }

        self.device_calls = {
            'p': self.printer_system_call,
            'd': self.disk_system_call,
            'c': self.cd_system_call,
        }

        self.device_interrupts = {
            'P': self.printer_interrupt,
            'D': self.disk_interrupt,
            'C': self.cd_interrupt,
        }

    def get_next_id(self):
        """
        Return current ID. Also increment by 1 for the next ID
        :rtype: integer
        """
        old_id = self.pidGenerator
        self.pidGenerator += 1
        return old_id

    """ USER INTERACTION """
    def wait_for_input(self):
        """
        Receive input from the Keyboard. See documentation for OS class
        for information about available commands
        """
        command = raw_input("> Input a valid command: ")
        if valid.validate_command(command):
            self.action(command)

    def action(self, command):
        """
        :param command: A valid command recognized by the system

        Jump to the proper function based on the command
        """
        if command in single_commands:
            return self.action_dict[command]()
        elif command[0] in device_commands and len(command) > 1:
            return self.action_dict[command[0]](command[0], int(command[1:]))
        else:
            raise Exception("Invalid command")

    """ SINGLE COMMANDS """
    def arrival_pcb(self):
        """
        Command 'A': Enqueue a new PCB with the next PID into the Ready Queue
        """
        if self.CPU.empty():
            self.CPU.load(pcb.PCB(self.get_next_id()))
        else:
            self.ReadyQueue.append(pcb.PCB(self.get_next_id()))

        print ">>> New process has arrived"

    def load_ready_queue(self, process):
        """
        Take the given process from some device and place into the

        :param process: Some process a device has issued the interrupt for
        :return:
        """
        if self.CPU.empty():
            self.CPU.load(process)
        else:
            self.ReadyQueue.append(process)

    def terminate_pcb(self):
        """
        Command 't': Unload the CPU. If the Ready Queue is not empty, load the
        head of the Ready Queue into the CPU.
        """
        self.CPU.unload()
        self.load_next_process()
        print ">>> Process terminated"

    def load_next_process(self):
        if self.ReadyQueue:  # equivalent to not deque.empty()
            self.CPU.load(self.ReadyQueue.popleft())

    def snapshot(self):
        """
        Command 'S': Show the state of queues of a chosen type
        Note: Only the first 16 characters of file name is displayed
        """
        choice = valid.validate_snapshot("> Select r, p, d, or c: ")
        self.print_devices(choice)

    def print_devices(self, char):
        """
        Precondition: This character has already been validated
        :param char: A single character in [r,p,d,c]

        Given some symbol, print that ready queue or device list
        """
        def row_print(input_width, string):
            print '{0:>{width}}'.format(string, width=input_width),

        def row_print_header():
            row_print(10, "PID")
            row_print(20, "Filename")
            row_print(16, "Mem Start")
            row_print(6, "R/W")
            row_print(16, "File Length")
            print

        def row_print_pcb(pcb, offset=0):
            row_print(6+offset, pcb.id)
            row_print(20, pcb.filename[:20])
            row_print(16, pcb.memstart)
            row_print(6, pcb.rw)
            row_print(16, pcb.length)
            print

        if char == 'r':
            print "CPU---"
            row_print(6, "PID\n")
            if not self.CPU.empty():
                row_print(6, self.CPU.process.id)
                print " (Current CPU Process)"
            else:
                print "    n/a (Current CPU Process)\n"

            print "ReadyQueue---"
            row_print(6, "PID\n")
            if self.ReadyQueue:  # equivalent to 'not deque.empty()'
                for process in self.ReadyQueue:
                    row_print(6, process.id)
                    print
            else:
                print "    --"
        else:
            row_print_header()
            i = 1
            for device_queue in self.devices[char]:
                print "{0}{1}:".format(char, i),
                if device_queue:  # equivalent to 'not deque.empty()'
                    offset = False
                    # don't offset the first line because
                    # the first line also contains device ID
                    for p in device_queue:
                        if offset is False:
                            row_print_pcb(p)
                            offset = True
                        else:
                            row_print_pcb(p, 4)
                else:
                    print "    --"
                i += 1

    """ DEVICE SYSTEM CALL COMMANDS """
    def system_call(self, char, num):
        """
        Switch function for all system calls

        :param char: Device Key [p,d,c]
        :param num: Device Number
        :return: None
        """
        if self.CPU.empty():
            raise Exception("CPU is empty. Cannot issue System Call.")
        elif self.device_exists(char, num):
            self.device_calls[char](num)
        print ">>> System call issued"

    def printer_system_call(self, num):
        """
        Remove CPU process, set information, and place into the
        n-th Printer queue

        :param num: Printer device number
        """
        process = self.CPU.unload()  # Get current process
        process.set_printer_process()  # Set proper variables
        self.Printers[num-1].append(process)  # Load into device
        self.load_next_process()  # Load next process into CPU

    def disk_system_call(self, num):
        """
        Remove CPU process, set information, and place into the
        n-th Disk queue

        :param num: Disk device number
        """
        process = self.CPU.unload()
        process.set_full_process()
        self.Disks[num-1].append(process)
        self.load_next_process()

    def cd_system_call(self, num):
        """
        Remove CPU process, set information, and place into the
        n-th CD/RW queue

        :param num: CD/RW device number
        """
        process = self.CPU.unload()
        process.set_full_process()
        self.CDs[num-1].append(process)
        self.load_next_process()

    """ INTERRUPT COMMANDS """
    def interrupt(self, char, num):
        """
        Switch function for all interrupts

        :param char: Device Key [p,d,c]
        :param num: Device Number
        :return: None
        """
        if self.device_exists(char, num):
            if self.device_contains_something(char, num):
                self.device_interrupts[char](num)
        print ">>> Device issued an interrupt"

    def interrupt_cleanup(self, process):
        """
        Common ending to all interrupts. Clear the device specific info,
        and place the process back into the Ready Queue or CPU.

        :param process:
        :return:
        """
        process.clear()
        self.load_ready_queue(process)

    def printer_interrupt(self, num):
        """
        Remove Printer[num] process, clear information, and place into the
        ReadyQueue (or CPU if the Ready Queue is empty)

        :param num: Printer device number
        """
        process = self.Printers[num-1].popleft()
        self.interrupt_cleanup(process)

    def disk_interrupt(self, num):
        """
        Remove Disk[num] process, clear information, and place into the
        ReadyQueue (or CPU if the Ready Queue is empty)

        :param num: Disk device number
        """
        process = self.Disks[num-1].popleft()
        self.interrupt_cleanup(process)

    def cd_interrupt(self, num):
        """
        Remove CDs[num] process, clear information, and place into the
        ReadyQueue (or CPU if the ReadyQueue is empty)

        :param num: CD/RW device number
        """
        process = self.CDs[num-1].popleft()
        self.interrupt_cleanup(process)

    """ (CLASS SPECIFIC) DEVICE VALIDATORS """
    def device_exists(self, char, num):
        """
        Check if this combination is valid. Raise exception if not.

        :param char: Device keyword
        :param num: Device number
        :return:
        """
        if num > self.device_sizes[char.lower()]:
            raise IndexError("Invalid device choice")
        elif num <= 0:
            raise IndexError("There is no zero-th or negative number devices")
        else:
            return True

    def device_contains_something(self, char, num):
        """
        Check if this device combination contains at least 1 item.
        Raise an exception if not.

        :param char: Device keyword
        :param num: Device number
        :return:
        """
        contains_something = self.devices[char.lower()][num-1]
        if contains_something: # true if queue contains items
            return True
        else:
            raise Exception("Selected device has no process in queue")