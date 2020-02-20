#!/usr/bin/env python
import socket
import subprocess
import sys
from queue import Queue
import threading
import time

subprocess.call('clear', shell=True)

HOST    = raw_input("Introduce la direccion del host: ")
HOSTIP  = socket.gethostbyname(HOST)

THREADS    =  int(raw_input("Introduce el numero de  hilos con el que quieres buscar los puertos: "))
RANGEINF    = int(raw_input("Introduce el rango de puertos inferior: "))
RANGESUP    = int(raw_input("Introduce el rango de puertos superior: "))

print_lock = threading.Lock()

print "-" * 80
print "Escaneando al host: {}".format(HOSTIP)
print "-" * 80

def scan(puerto):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try: 
        result = sock.connect_ex((HOSTIP, puerto))
        if result == 0:
            with print_lock:
                print "Puerto TCP {}: 	 Abierto".format(puerto)
        sock.close()

    except socket.gaierror:
        print 'El nombre del host no se resolvio.'
        sys.exit()

    except socket.error:
        print "No  se pudo conectar al host"
        sys.exit()

def threader():
    while True:
        worker = q.get()
        scan(worker)
        q.task_done()

q = Queue()

for x in range(THREADS):
    t = threading.Thread(target=threader)
    t.daemon = True
    t.start()

start = time.time()
for worker in range(RANGEINF,RANGESUP):
    q.put(worker)

q.join()
end = time.time()

print(end-start)

print 'Escaneado completado con exito'