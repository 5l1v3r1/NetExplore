from ipaddress import IPv4Network
from queue import Queue
from threading import Thread
import subprocess
from sys import exit, argv
from time import sleep, time


class NetworkScanner:
    def __init__(self):
        pass

    @staticmethod
    def host_discovery(netmask, threads, verbose=True):
        try:
            if verbose:
                print("[+] Searching for hosts ...")

            def scan(ip):
                global PB
                PB.inc_value()
                output = subprocess.Popen(['ping', '-n', '1', '-w', '500', ip], stdout=subprocess.PIPE, startupinfo=info).communicate()[0]
                if not b"berschreitung" in output and not b"unreachable" in output and not b"exceed" in output and not b"timed out" in output and not b"Exception" in output:
                    up.append(ip)

            def thread_handle():
                while not queue.empty():
                    host_ = queue.get()
                    scan(host_)

            info = subprocess.STARTUPINFO()
            up = []
            hosts = IPv4Network(netmask).hosts()
            queue = Queue()

            for host in hosts:
                queue.put(str(host))

            PB.bar.max = queue.qsize()
            t = Thread(target=thread_handle)
            t.start()

            for i in range(threads - 1):
                t = Thread(target=thread_handle)
                t.start()

            t.join()
            print("\n\n[+] Discovered hosts:\n")
            for host in up:
                print("[-] {}".format(host))
        except KeyboardInterrupt:
            print("[-] CTRL-C was punched, exiting...")
            exit()
        except:
            print("[-] Unknown Error")
            exit()


class ProgrssBar:
    class Bar:
        def __init__(self, max_value, title, char, length, unit):
            self.__title = title
            self.__char = char
            self.__len = length
            self.speed = 0
            self.__fill = 0
            self.max = max_value
            self.value = 0.0
            self.percent = 0
            self.unit = unit

        def string(self):
            self.percent = round(self.value / self.max * 100)
            if self.percent > 100:
                self.percent = 100
            self.__fill = round(self.percent * self.__len / 100)

            return "{} |{}{}| {}/{} ({}%) {} {}/s".format(self.__title,
                                                          self.__fill * self.__char,
                                                          (self.__len - self.__fill) * " ",
                                                          self.value, self.max, self.percent,
                                                          self.speed, self.unit)

    def __init__(self, max_value, title="Loading", char="█", length=70, unit="", multiplyer=1):
        self.bar = self.Bar(max_value, title, char, length, unit)
        self.multiplyer = multiplyer

    def set_value(self, value):
        self.bar.value = value

    def inc_value(self, increment=1):
        self.bar.value += increment

    def show_progress(self):

        def monitor_speed():
            value_start = self.bar.value
            start = time()
            sleep(1)
            self.bar.speed = round((self.bar.value - value_start) / (time() - start) * self.multiplyer, 2)

        t = Thread(target=monitor_speed, daemon=True)
        t.start()

        print()
        while self.bar.percent < 100:
            try:
                print(self.bar.string(), end="\r")
                sleep(0.1)
            except KeyboardInterrupt:
                print("\n\nProcess aborted by user")
                break
        print()


scan = NetworkScanner()
PB = ProgrssBar(1, unit="hosts")


def perform_scan():
    global start
    start = time()
    scan.host_discovery(argv[1], threads=int(argv[2]))


if __name__ == '__main__':
    if len(argv) < 2:
        print("[+] You forgot to add an IP range")
        print("[+] Usage: python netexplore.py <iprange> <threads>")
        exit()
    elif len(argv) < 3:
        print("[+] You forgot to add the amount of threads")
        print("[+] Usage: python netexplore.py <iprange> <threads>")
    else:
        t = Thread(daemon=True, target=perform_scan)
        t.start()
        sleep(0.1)
        PB.show_progress()
        sleep(0.1)
        t.join()
        stop = time()
        time_spent = str((stop - start)).split(".")[0]
        print("\n[+] Scan time: %s seconds" % time_spent)
