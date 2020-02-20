import socket,sys,struct,os
from netaddr import IPNetwork,IPAddress
from ctypes import *


srcip   = '192.168.100.138'
destip  = '209.85.195.104'
srcport = 80
dstport = 80

def checksum(msg):
    s = 0
     
    for i in range(0, len(msg)-1, 2):
        w = ord(msg[i]) + (ord(msg[i+1]) << 8 )
        s = s + w
     
    s = (s>>16) + (s & 0xffff)
    s = s + (s >> 16)

    s = ~s & 0xffff
     
    return s

def construct_ip_header(source_ip,dest_ip,ihl=5,ver=4,pid=0,offs=0,ttl=255,proto=socket.IPPROTO_TCP):
    ip_ihl = ihl
    ip_ver = ver
    ip_tos = 0
    ip_tot_len = 0 
    ip_id = pid   
    ip_frag_off = offs
    ip_ttl = ttl
    ip_proto = proto
    ip_check = 0   
    ip_saddr = socket.inet_aton ( source_ip )
    ip_daddr = socket.inet_aton ( dest_ip )
    
    ip_ihl_ver = (ip_ver << 4) + ip_ihl
    
    ip_header = struct.pack('!BBHHHBBH4s4s' , ip_ihl_ver, ip_tos, ip_tot_len, ip_id, ip_frag_off, ip_ttl, ip_proto, ip_check, ip_saddr, ip_daddr)
    return ip_header

def construct_tcp_header(source_ip,dest_ip,srcp,dstp,seq,ackno,flags,user_data="",doff=5,wsize=5840,urgptr=0):
    tcp_source = srcp  
    tcp_dest = dstp   
    tcp_seq = seq
    tcp_ack_seq = ackno
    tcp_doff = doff
    tcp_fin = flags[8]
    tcp_syn = flags[7]
    tcp_rst = flags[6]
    tcp_psh = flags[5]
    tcp_ack = flags[4]
    tcp_urg = flags[3]
    tcp_window = socket.htons(5840)  
    tcp_check = 0
    tcp_urg_ptr = urgptr
    
    tcp_offset_res = (tcp_doff << 4) + 0
    tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh <<3) + (tcp_ack << 4) + (tcp_urg << 5)
    
    tcp_header = struct.pack('!HHLLBBHHH' , tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window, tcp_check, tcp_urg_ptr)
    
    source_address = socket.inet_aton( source_ip )
    dest_address = socket.inet_aton(dest_ip)
    placeholder = 0
    protocol = socket.IPPROTO_TCP
    tcp_length = len(tcp_header) + len(user_data)
    
    psh = struct.pack('!4s4sBBH' , source_address , dest_address , placeholder , protocol , tcp_length)
    psh = psh + tcp_header + user_data
    
    tcp_check = checksum(psh)
    
    tcp_header = struct.pack('!HHLLBBH' , tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window) + struct.pack('H' , tcp_check) + struct.pack('!H' , tcp_urg_ptr)
    return tcp_header

def construct_tcp_packet(ip_header,tcp_header,user_data=""):
    packet=''
    packet = ip_header + tcp_header + user_data
    return packet

class IP(Structure):
    
    _fields_ = [
        ("ihl",           c_ubyte,4),
        ("version",       c_ubyte,4),
        ("tos",           c_ubyte),
        ("len",           c_ushort),
        ("id",            c_ushort),
        ("offset",        c_ushort),
        ("ttl",           c_ubyte),
        ("protocol_num",  c_ubyte),
        ("sum",           c_ushort),
        ("src",           c_uint),
        ("dst",           c_uint)
    ]

    def __new__(self, socket_buffer=None):
            return self.from_buffer_copy(socket_buffer)    
        
    def __init__(self, socket_buffer=None):

        self.protocol_map = {1:"ICMP", 6:"TCP", 17:"UDP"}
        
        self.src_address = socket.inet_ntoa(struct.pack(">1"))&1
        self.rst = (flagsi>>2)&1
        self.psh = (flagsi>>3)&1
        self.ack = (flagsi>>4)&1
        self.urg = (flagsi>>5)&1
        self.ece = (flagsi>>6)&1
        self.cwr = (flagsi>>7)&1
        self.hs  = (flagsi>>8)&1

        self.seq_no = socket.htonl(self.seqno)
        self.ack_no = socket.htonl(self.ackno)
        self.win_size = socket.htons(self.wsize)


def create_socket():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        s.bind((srcip,srcport))
    except Exception as e:
        print('Error: ' + e.message)
        return (False,'Error: ' + e.message)
    
    return (s)

def three_way_handshake(s,destip):
    try:
        global latest_raw_buffer
        global latest_tcp_header
        #envio el syn
        iphead=construct_ip_header(srcip,destip)
        tcphead=construct_tcp_header(srcip,destip,srcport,dstport,1,0,[0,0,0,0,0,0,0,1,0])
        tcppacket = construct_tcp_packet(iphead,tcphead)
        ret = s.sendto(tcppacket,(destip, dstport))
        #recibo el ack/syn
        raw_buffer = s.recv(4096)
        latest_raw_buffer = raw_buffer
        tcp_header = raw_buffer[20:40]
        latest_tcp_header = tcp_header

        #envio el paquete ack
        iphead=construct_ip_header(srcip,destip)
        tcphead=construct_tcp_header(srcip,destip,srcport,dstport,2,tcp_header.seq_no + 1,[0,0,0,0,1,0,0,0,0])
        tcppacket = construct_tcp_packet(iphead,tcphead)
        ret = s.sendto(tcppacket,(destip, dstport))


    except Exception as e:
        print('Fallo: '  + e.message)
        return (False,'Fallo: '  + e.message)
    
    return (s)


s=create_socket()
three_way_handshake(s,destip)