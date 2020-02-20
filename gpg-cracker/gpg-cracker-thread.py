import argparse
import time
import subprocess as sub
import string
import sys
import pprint
import threading


charsets = {
    "digits" : string.digits,
    "lower" : string.ascii_lowercase,
    "upper" : string.ascii_uppercase,
    "ascii" : string.ascii_letters,
    "full" : string.digits + string.ascii_letters
}

def decrypt_schedule(begin,end,charset,filename):

    for i in range (begin,end):
        nuevo = str_base(i,charset)
        result = sub.run("echo {} | gpg --batch --yes --passphrase-fd 0 {} >> /dev/null".format(nuevo,filename),stdout=sub.DEVNULL,shell=True)
        #result = sub.run("echo {} | gpg --batch --passphrase-fd 0 {}".format(nuevo,filename),stdout=sub.DEVNULL,shell=True)
        #result = sub.run("gpg --batch --passphrase '{}' -d {} &> null".format(nuevo,filename),stdout=sub.DEVNULL,shell=True)
        #rc = result.returncode
        print("{}".format(nuevo))
        if result.returncode is 0:
            print("Clave {} n {}".format(nuevo,i))
            sys.exit(0)

def decrypt(key_len, charset,filename,threads):

    max = maximun(key_len,charset)
    base = charsets[charset]
    rep = (int) (max/threads)

    for i in range(0,threads):
        begin = rep * i + 1
        end = (rep * (i+1))+1
        if i == threads-1:
            end = max
        
        ## Aqui se crean los hilos
        ##decrypt_schedule(begin,end,base,filename)
        t = threading.Thread(target=decrypt_schedule,args=(begin,end,base,filename,))
 
        t.start()


    return



def str_base(number, base):
   (d,m) = divmod(number,len(base))
   if d > 0:
      return str_base(d-1,base)+base[m]
   return base[m]

def maximun(key_len,charset):

    max = 0
    for i in range (1,key_len+1):
        max = max + len(charsets[charset])**i

    return max

def main():
    parser = argparse.ArgumentParser(description='gpg-cracker')
    parser.add_argument('--file',type=str,help="File route",required=True)
    parser.add_argument('--len', type=int, help='Maximum length of the symmetric key', required=True)
    parser.add_argument('--charset', type=str, help='Key character set', required=True)
    parser.add_argument('--threads', type=int, help='Number of threads. Default 1', default=1)
    args = parser.parse_args()  

    fileName = args.file
    key_len = args.len
    charset = args.charset
    threads  = args.threads

    try:
        file = open(fileName,'rb')
    except:
        print("File error")
        sys.exit(1)

    file.close()

    if charset not in charsets:
        print ("Not correct charset")
        pprint.pprint(charsets)
        sys.exit(1)

    decrypt(key_len,charset,fileName,threads)

if __name__ == "__main__":
    main()
