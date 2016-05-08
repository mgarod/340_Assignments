"""
Title:          Snapshot.py
Author:         Michael Garod
Date Created:   4/26/16
Class:          CSCI 340-01, Tues & Fri 3:45PM - 5:00PM
Professor:      Eric Schweitzer
Purpose:        Project #3
Description:    Implementation of the Snapshot function
"""


def print_devices(self, char):
        """
        Precondition: This character has already been validated

        :param self: The Operating system we wish to display
        :param char: A single character in [r,p,d,c]

        Given some symbol, print that ready queue or device list
        """
        def row_print(input_width, string):
            print '{0:>{width}}'.format(str(string), width=input_width),

        def row_print_header():
            row_print(7, "PID")
            row_print(10, "Filename")
            row_print(10, "Mem.Start")
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

        def row_print_jp_header():
            row_print(7, "PID")
            row_print(7, "E.Bur")
            row_print(7, "T.Bur")
            row_print(7, "A.Bur")
            row_print(12, "Mem. Usage")

        def row_print_jp_pcb(pcb):
            row_print(7, pcb.id)
            row_print(7, pcb.working_tau)
            row_print(7, pcb.total_burst)
            row_print(7, pcb.get_avg())
            row_print(12, pcb.mem_usage)
            pass

        def print_os_accounting():
            print "System Accounting---"
            row_print(20, "  Systemwide Avg. Burst:")
            if self.completed_processes == 0:
                row_print(25, "No completed processes")
            else:
                row_print(6, (self.total_cpu_usage / self.completed_processes))

        # Begin Printing
        print
        print_os_accounting()
        print
        print
        if char == 'r':
            print "CPU---"
            row_print(6, "PID")
            row_print(12, "Est. Burst")
            row_print(12, "Total Burst")
            row_print(12, "Avg. Burst")
            row_print(12, "Mem. Usage")
            print
            if not self.CPU.empty():
                row_print(6, self.CPU.process.id)
                row_print(12, self.CPU.process.working_tau)
                row_print(12, self.CPU.process.total_burst)
                row_print(12, self.CPU.process.get_avg())
                row_print(12, self.CPU.process.mem_usage)
                print
                print "      Frames Used: {}".format(
                    self.CPU.process.used_frames)
            else:
                row_print(6, "--\n")
                # print "    n/a\n"

            print "ReadyQueue---"
            row_print(6, "PID")
            row_print(12, "Est. Burst")
            row_print(12, "Total Burst")
            row_print(12, "Avg. Burst")
            row_print(12, "Mem. Usage")
            print
            if self.ReadyQueue:  # equivalent to 'not deque.empty()'
                for process in self.ReadyQueue:
                    row_print(6, process.id)
                    row_print(12, process.working_tau)
                    row_print(12, process.total_burst)
                    row_print(12, process.get_avg())
                    row_print(12, process.mem_usage)
                    print
                    print "      Frames Used: {}".format(process.used_frames)
            else:
                print "    --"
        elif char == 'd':
            i = 1
            print "Disks---"
            row_print_disk_header()
            print "-" * 78
            for d in self.devices[char]:
                asc_desc = d.get_arm_direction()
                curr_pos = d.current_position
                max_cyl = d.max_cylinders
                print "{0}{1}: {2} Arm at cylinder {3} (of {4}) "\
                    .format(char, i, asc_desc, curr_pos, max_cyl)
                # Print Busy Queue
                print "  Busy Queue:"
                if d.get_busy_queue():
                    for p in d.get_busy_queue_iter():
                        row_print_disk_pcb(p)
                        print "        Frames Used: {}".format(p.used_frames)
                else:
                    print "    --"

                # Print Waiting Queue
                print "  Waiting Queue:"
                if d.get_waiting_queue():
                    for p in d.get_waiting_queue_iter():
                        row_print_disk_pcb(p)
                        print "        Frames Used: {}".format(p.used_frames)
                else:
                    print "    --"

                i += 1
        elif char == 'j':
            print
            print "Job Pool---"
            print "-" * 78
            row_print_jp_header()
            print
            for p in self.JobPool:
                row_print_jp_pcb(p)
            print
        elif char == 'm':
            print
            print "Memory Usage---"
            row_print(10, "Page Size")
            row_print(20, "Max Process Size")
            row_print(16, "Total Memory")
            print
            row_print(10, self.page_size)
            row_print(20, self.max_process_size)
            row_print(16, self.max_mem)
            print
            print "-" * 78
            print "Free Frame List--- (10 frames per line, FIFO order)"
            for i, v in enumerate(self.Available_Frames):
                if i == 0:
                    print "[",
                if i != len(self.Available_Frames) - 1:
                    print str(v) + ", ",
                else:
                    print str(v) + " ]"
                if i % 10 == 9:
                    print
            if len(self.Available_Frames) == 0:
                print "    No Frames Available"
            print
            print "Frame Table"
            print "-" * 78
            row_print(6, "Frame#")
            row_print(6, "PID")
            row_print(6, "Page#")
            print
            for frame, item in self.Frame_Table.items():
                row_print(6, frame)
                if item == 0:
                    row_print(6, "--")
                    row_print(6, "--")
                else:
                    row_print(6, item[0])
                    row_print(6, item[1])
                print

        else:  # Printers and CD/RW
            if char == 'c':
                print "CD/RWs---"
            elif char == 'p':
                print "Printers---"
            row_print_header()
            print "-" * 78
            i = 1
            for device_queue in self.devices[char]:
                print "{0}{1}:".format(char, i),
                if device_queue:  # equivalent to 'not deque.empty()'
                    for p in device_queue:
                        row_print_pcb(p)
                        print "        Frames Used: {}".format(p.used_frames)
                else:
                    print "    --"
                i += 1

        print
