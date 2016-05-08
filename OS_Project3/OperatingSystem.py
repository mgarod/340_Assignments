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
-------------------------------------------------------------------------------
Update:         5/8/16
Purpose:        Project #3
Description:    Add memory management and paging
                Add Kill command
                Move Snapshot function to Snapshot.py
"""
import collections as col
# use append() and popleft() in order to simulate a regular queue with deque
import ProcessControlBlock as pcb
import CentralProcessingUnit as cpu
import Validators as valid
import ReadyQueue as rq
import DiskDrive as disk
import Snapshot
import JobPool as jp
import math


""" Valid characters to be received as input """
single_commands = ['A', 't', 'S', 'K']
device_commands = ['p', 'd', 'c', 'P', 'D', 'C']
valid_c1 = ['p', 'd', 'c', 'P', 'D', 'C', 'A', 't', 'S', 'K']
valid_snapshot_char = ['p', 'd', 'c', 'r', 'j', 'm']  # And any number


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
    K = remove job from the system (wherever it may lie) and deallocate memory
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
        self.JobPool = jp.JobPool()
        self.Available_Frames = col.deque()

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
            'C': self.interrupt,
            'K': self.kill
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

        # Memory Management
        self.page_size = valid.validate_power_2("> Input page size: ")
        self.max_process_size = valid.validate_pos_int(
            "> Input max size of a process: ")
        self.max_mem = valid.validate_pos_int_multiple(
            "> Input total size of memory: ", self.page_size)

        num_pages = self.max_mem / self.page_size
        self.Available_Frames.extend(range(0, num_pages))
        self.Frame_Table = {k: 0 for k in range(0, num_pages)}

        print "-" * 80

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
        # Memory Management Check
        process_size = valid.validate_pos_int(
            ">>> Please input this process's size: ")

        if process_size > self.max_mem:
            raise ValueError(
                """This system cannot service a process of size {},
                because the system's total memory is only {}
                """.format(process_size, self.max_mem))
        elif process_size > self.max_process_size:
            raise ValueError(
                """This process exceeds the maximum process size ({})"""
                .format(self.max_process_size))

        # Calculate if there are enough frames to service the process
        new_p = pcb.PCB(self.get_next_id(), OS.tau, OS.alpha, process_size,
                        self.page_size)
        num_frames_needed = self.calculate_frames_needed(process_size)
        if len(self.Available_Frames) < num_frames_needed:
            # Not enough frames->JP
            self.JobPool.append(new_p)
            p = self.CPU.unload()
            p.increment_burst()
            self.ReadyQueue.append(p)
            self.load_next_process()
        else:  # There are enough frames, so place in CPU or ReadyQueue
            self.give_n_frames_to_p(num_frames_needed, new_p)
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

        # Release used frames, and extend onto available frames list
        # Find largest in job pool to place on ready queue
        self.reclaim_frames_to_avail(process)

        print ">>> Process terminated"

    def load_next_process(self):  # into the CPU
        if self.ReadyQueue:  # equivalent to not deque.empty()
            self.CPU.load(self.ReadyQueue.popleft())

    def snapshot(self):
        """
        Command 'S': Show the state of queues of a chosen type
        Note: Only the first 16 characters of file name is displayed
        Will also display system wide accounting information.
        """

        choice = valid.validate_snapshot(">>> Select r, p, d, c, j, or m: ")
        Snapshot.print_devices(self, choice)

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

    def interrupt_cleanup(self, process):
        """
        Common ending to all interrupts. Clear the device specific info,
        and place the process back into the Ready Queue or CPU.

        :param process:
        :return:
        """
        process.clear()
        if not self.CPU.empty():
            cpu_p = self.CPU.unload()
            cpu_p.increment_burst()
            self.ReadyQueue.append(cpu_p)
        self.ReadyQueue.append(process)
        self.load_next_process()

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

    """ MEMORY MANAGEMENT METHODS """
    def give_n_frames_to_p(self, n, p):
        needed_frames = self.release_frames_from_avail(n)
        update_dict = {k: (p.id, i) for i, k in enumerate(needed_frames)}
        self.Frame_Table.update(update_dict)
        p.assign_frames_to_process(needed_frames)

    def release_frames_from_avail(self, n):
        l = list()
        for i in range(n):
            l.append(self.Available_Frames.popleft())
        return l

    def reclaim_frames_to_avail(self, p):
        released_frames = p.release_frames_from_process()
        update_dict = {k: 0 for k in released_frames}
        self.Frame_Table.update(update_dict)
        self.Available_Frames.extend(released_frames)
        self.load_next_jp_process()

    def calculate_frames_needed(self, mem_use):
        return int(math.ceil(float(mem_use) / float(self.page_size)))

    def load_next_jp_process(self):
        # Find the largest job in JobPool which could fit in memory
        next_job = self.JobPool.get_largest_fit(
            len(self.Available_Frames) * self.page_size)

        if next_job == 0 or next_job == 1:
            return  # There is no job available to place in the ReadyQueue
        else:  # If next job is not None
            # Assign n frames to the job, and put that job in the ReadyQueue
            n_frames_needed = self.calculate_frames_needed(next_job.mem_usage)
            self.give_n_frames_to_p(n_frames_needed, next_job)
            self.ReadyQueue.append(next_job)

    def kill(self):
        """
        Command 'K' to kill a process wherever it may lie.
        :return: None
        """
        class Accumulator:
            def __init__(self):
                self.killed = False

        k = Accumulator()
        target_id = valid.validate_pos_int(">>> Which PID would you like to "
                                           "kill? ")

        if not self.CPU.empty() and self.CPU.process.id == target_id:
            process = self.CPU.unload()
            self.load_next_process()
            self.reclaim_frames_to_avail(process)
            print ">>> PID {} killed".format(target_id)
            return

        self.kill_process_in_iter(target_id, self.ReadyQueue, k)
        self.kill_process_in_iter(target_id, self.JobPool, k)

        for printer in self.devices['p']:
            self.kill_process_in_iter(target_id, printer, k)

        for cd in self.devices['c']:
            self.kill_process_in_iter(target_id, cd, k)

        for d in self.devices['d']:
            self.kill_process_in_iter(target_id, d.get_busy_queue(), k)
            self.kill_process_in_iter(target_id, d.get_waiting_queue(), k)

        self.kill_cleanup()
        if k.killed:
            print ">>> PID {} killed".format(target_id)
        else:
            print ">>> PID {} not found. No kill occurred.".format(target_id)

    def kill_cleanup(self):
        """
        Final accounting to the kill command
        :return: None
        """
        if not self.CPU.empty():
            cpu_p = self.CPU.unload()
            cpu_p.increment_burst()
            self.ReadyQueue.append(cpu_p)
            self.load_next_process()

    def kill_process_in_iter(self, tar_id, d, acc):
            """
            Look for a PID in ReadyQueue, Job Pool(list), CD/RW or Printer(deque).
            If found, the job will be killed

            Note: This will not work on Disks. They must be handled uniquely.

            :param tar_id: The PID we are trying to find and kill
            :param d: The device deque we are looking through
            :param acc: Accumulator which keeps track of if the job was killed
            :return: None
            """
            if acc.killed:
                return

            index = None
            for i, p in enumerate(d):
                if p.id == tar_id:
                    index = i
                    break

            if index is not None:
                self.reclaim_frames_to_avail(d[index])
                del d[index]
                acc.killed = True
