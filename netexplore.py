class NetworkScanner:
    def __init__(self):
        global IPv4Network
        global Queue
        global Thread
        global subprocess
        from ipaddress import IPv4Network
        from queue import Queue
        from threading import Thread
        import subprocess
        from sys import exit

    @staticmethod
    def host_discovery(netmask, threads, verbose=True):
        try:
            if verbose:
                print("[+] Searching for hosts ...")
            def scan(ip):
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
            t = Thread(target=thread_handle)
            t.start()
            for i in range(threads - 1):
                t = Thread(target=thread_handle)
                t.start()
            t.join()
            print("[+] Discovered hosts:")
            for host in up:
                print("-%s"%host)
        except KeyboardInterrupt:
            print("[-] CTRL-C was punched, exiting...")
            exit()
        except:
            print("[-] Unknown Error")
            exit()
scan = NetworkScanner()

from time import time
start = time()
from sys import argv,exit
if len(argv) < 2:
    print("[+] You forgot to add an IP range")
    print("[+] Usage: python netexplore.py <iprange> <threads>")
    exit()
elif len(argv) < 3:
    print("[+] You forgot to add the amount of threads")
    print("[+] Usage: python netexplore.py <iprange> <threads>")
else:
    scan.host_discovery(argv[1], threads=int(argv[2]))
    stop = time()
    time_spent = str((stop - start)).split(".")[0]
    print("[+] Scan time: %s seconds" % time_spent)







