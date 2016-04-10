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
-------------------------------------------------------------------------------
Update:         4/10/16
Purpose:        Project #2
Description:    Add history, based pre-emptive Ready Queue.
                Add FSCAN based disk queues.
                Add System Wide accounting information.
                Modify Snapshots accordingly.
"""
import collections as col
# use append() and popleft() in order to simulate a regular queue with deque
import ProcessControlBlock as pcb
import CentralProcessingUnit as cpu
import Validators as valid
import ReadyQueue as rq
import DiskDrive as disk


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
    # Static variables for the Operating System
    alpha = valid.validate_alpha("> Input alpha for this OS: ")
    tau = valid.validate_pos_float("> Input initial burst for this OS: ")

    def __init__(self):
        """
        System Generator for the OS Class.
        Will ask for number of Printers, Disks, and CD/RWs.
        Maintains a unique PID numbering system ( see get_next_id() )
        """
        self.ReadyQueue = rq.ReadyQueue()
        self.Printers = list()
        self.Disks = list()
        self.CDs = list()

        self.pidGenerator = 1
        self.CPU = cpu.CPU()

        self.num_printers = \
            valid.validate_pos_int("> Input number of printers: ")
        self.num_disks = \
            valid.validate_pos_int("> Input number of disk drives: ")
        self.num_cds = \
            valid.validate_pos_int("> Input number of CD/RW drives: ")

        for i in range(self.num_printers):
            self.Printers.append(col.deque())

        for i in range(self.num_disks):
            d = valid.validate_pos_int(">>> Input number of cylinders for "
                                       "disk drive " + str(i + 1) + ": ")
            self.Disks.append(disk.Disk(d))

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

        self.completed_processes = 0
        self.total_cpu_usage = 0

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
        new_p = pcb.PCB(self.get_next_id(), OS.tau, OS.alpha)
        if self.CPU.empty():
            self.CPU.load(new_p)
        else:
            self.ReadyQueue.append(new_p)
            p = self.CPU.unload()
            p.increment_burst()
            self.ReadyQueue.append(p)
            self.load_next_process()

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
        process = self.CPU.unload()
        self.load_next_process()
        process.terminal_accounting()
        self.total_cpu_usage += process.total_burst
        self.completed_processes += 1
        print ">>> Process terminated"

    def load_next_process(self):
        if self.ReadyQueue:  # equivalent to not deque.empty()
            self.CPU.load(self.ReadyQueue.popleft())

    def snapshot(self):
        """
        Command 'S': Show the state of queues of a chosen type
        Note: Only the first 16 characters of file name is displayed
        Will also display system wide accounting information.
        """

        choice = valid.validate_snapshot(">>> Select r, p, d, or c: ")
        self.print_devices(choice)

    def print_devices(self, char):
        """
        Precondition: This character has already been validated
        :param char: A single character in [r,p,d,c]

        Given some symbol, print that ready queue or device list
        """
        def row_print(input_width, string):
            print '{0:>{width}}'.format(str(string), width=input_width),

        def row_print_header():
            row_print(7, "PID")
            row_print(10, "Filename")
            row_print(10, "Mem Start")
            row_print(4, "R/W")
            row_print(10, "File Len")
            row_print(9, "Est.Burst")
            row_print(9, "Tot.Burst")
            row_print(9, "Avg.Burst")
            print

        def row_print_pcb(pcb, offset=0):
            row_print(3 + offset, pcb.id)
            row_print(10, pcb.filename[:20])
            row_print(10, pcb.memstart)
            row_print(4, pcb.rw)
            row_print(10, pcb.length)
            row_print(9, pcb.working_tau)
            row_print(9, pcb.total_burst)
            row_print(9, pcb.get_avg())
            print

        def row_print_disk_header():
            row_print(7, "PID")
            row_print(10, "Filename")
            row_print(9, "Mem.Start")
            row_print(4, "R/W")
            row_print(8, "File Len")
            row_print(9, "Cylinder")
            row_print(7, "E.Bur")
            row_print(7, "T.Bur")
            row_print(7, "A.Bur")
            print

        def row_print_disk_pcb(pcb):
            row_print(7, pcb.id)
            row_print(10, pcb.filename[:20])
            row_print(9, pcb.memstart)
            row_print(4, pcb.rw)
            row_print(8, pcb.length)
            row_print(9, pcb.cylinder)
            row_print(7, pcb.working_tau)
            row_print(7, pcb.total_burst)
            row_print(7, pcb.get_avg())
            print

        def print_os_accounting():
            print "System Accounting---"
            row_print(20, "  Systemwide Avg. Burst")
            if self.completed_processes == 0:
                row_print(25, "No completed processes")
            else:
                row_print(6, (self.total_cpu_usage / self.completed_processes))

        # Begin Printing
        print_os_accounting()
        print
        print
        if char == 'r':
            print "CPU---"
            row_print(6, "PID")
            row_print(12, "Est. Burst")
            row_print(12, "Total Burst")
            row_print(12, "Avg. Burst")
            print
            if not self.CPU.empty():
                row_print(6, self.CPU.process.id)
                row_print(12, self.CPU.process.working_tau)
                row_print(12, self.CPU.process.total_burst)
                row_print(12, self.CPU.process.get_avg())
                print
            else:
                row_print(6, "--\n")
                # print "    n/a\n"

            print "ReadyQueue---"
            row_print(6, "PID")
            row_print(12, "Est. Burst")
            row_print(12, "Total Burst")
            row_print(12, "Avg. Burst")
            print
            if self.ReadyQueue:  # equivalent to 'not deque.empty()'
                for process in self.ReadyQueue:
                    row_print(6, process.id)
                    row_print(12, process.working_tau)
                    row_print(12, process.total_burst)
                    row_print(12, process.get_avg())
                    print
            else:
                print "    --"
        elif char == 'd':
            i = 1
            print "Disks---"
            row_print_disk_header()
            print "-" * 78
            for d in self.devices[char]:
                print "{0}{1} ({2} cylinders) ".format(char, i, d.max_cylinders)
                # Print Busy Queue
                print "  Busy Queue:"
                if d.get_busy_queue():
                    for p in d.get_busy_queue_iter():
                        row_print_disk_pcb(p)
                else:
                    print "    --"

                # Print Waiting Queue
                print "  Waiting Queue:"
                if d.get_waiting_queue():
                    for p in d.get_waiting_queue_iter():
                        row_print_disk_header(p)
                else:
                    print "    --"

                i += 1
        else:  # Printers and CD/RW
            row_print_header()
            i = 1
            for device_queue in self.devices[char]:
                print "{0}{1}:".format(char, i),
                if device_queue:  # equivalent to 'not deque.empty()'
                    offset = False
                    for p in device_queue:
                        if offset is False:
                            row_print_pcb(p)
                            if p.cylinder:
                                print "CYLINDER {}".format(p.cylinder)
                            offset = True
                        else:
                            row_print_pcb(p, 4)
                            if p.cylinder:
                                print "CYLINDER {}".format(p.cylinder)
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
        process.end_burst()
        print "--- Setting Printer Information"
        process.set_printer_process()  # Set proper variables
        self.Printers[num - 1].append(process)  # Load into device
        self.load_next_process()  # Load next process into CPU

    def disk_system_call(self, num):
        """
        Remove CPU process, set information, and place into the
        n-th Disk queue

        :param num: Disk device number
        """
        process = self.CPU.unload()
        process.end_burst()
        print "--- Setting Disk Information"
        process.set_disk_process(self.Disks[num - 1].max_cylinders)
        self.Disks[num - 1].append(process)
        self.load_next_process()

    def cd_system_call(self, num):
        """
        Remove CPU process, set information, and place into the
        n-th CD/RW queue

        :param num: CD/RW device number
        """
        process = self.CPU.unload()
        process.end_burst()
        print "--- Setting CD/RW Information"
        process.set_full_process()
        self.CDs[num - 1].append(process)
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
        # Remove process from the CPU
        p = self.CPU.unload()
        self.ReadyQueue.append(p)
        self.load_next_process()
        # Pick Logical Next

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
        process = self.Printers[num - 1].popleft()
        self.interrupt_cleanup(process)

    def disk_interrupt(self, num):
        """
        Remove Disk[num] process, clear information, and place into the
        ReadyQueue (or CPU if the Ready Queue is empty)

        :param num: Disk device number
        """
        process = self.Disks[num - 1].popleft()
        self.interrupt_cleanup(process)

    def cd_interrupt(self, num):
        """
        Remove CDs[num] process, clear information, and place into the
        ReadyQueue (or CPU if the ReadyQueue is empty)

        :param num: CD/RW device number
        """
        process = self.CDs[num - 1].popleft()
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
        device = self.devices[char.lower()][num - 1]
        if char.lower() == 'd':
            size = len(device.get_busy_queue())
        else:
            size = len(device)

        if size > 0:  # true if queue contains items
            return True
        else:
            raise Exception("Selected device has no process in queue")