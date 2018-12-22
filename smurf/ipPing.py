#!/usr/bin/python

'''
ping ICMP

 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|      Type     |      Code     |            Checksum           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|            Identifier         |           Sequence Number     |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                             Payload                           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
'''

'''
IP

 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|Version|  IHL  |Type of Service|          Total Length         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         Identification        |Flags|      Fragment Offset    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  Time to Live |    Protocol   |         Header Checksum       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       Source Address                          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Destination Address                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Options                    |    Padding    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

The result of summing the entire IP header, including checksum, should be zero

'''

import socket
import sys
import os
import time
import array
import random
import struct


CODE_REQUEST = 8

def cksum(s):
    if len(s) & 1:
        s = s + '\0'
    words = array.array('h', s)
    sum = 0
    for word in words:
        sum = sum + (word & 0xffff)
    hi = sum >> 16
    lo = sum & 0xffff
    sum = hi + lo
    sum = sum + (sum >> 16)
    return (~sum) & 0xffff

# IP Package definition
class IPPacket:
    def __init__(self, icmpPacket=None, src=None, dest=None):
        self.icmpPacket = icmpPacket

        self.version = 4
        self.ihl = 5
        self.tos = 0
        self.totalLength = len(icmpPacket.toString()) + (self.ihl * 4)
        self.id = int((100000* random.random()) % os.getpid())
        self.flags = 0
        self.offset = 0
        self.ttl = 128
        self.protocol = socket.IPPROTO_ICMP;
        self.source = socket.inet_aton(src)
        self.destination = socket.inet_aton(dest)
        self.headerChecksum = self.__calculateHeaderChecksum();

    def __getIpHeader(self):
        ver_ihl = (self.version << 4) + self.ihl
        # Found this library to create the binary :party: Let's try
        ip_hdr = struct.pack("!BBHHBBBBcc4s4s", ver_ihl, self.tos, self.totalLength, self.id, self.flags, self.offset,self.ttl, self.protocol, chr((self.headerChecksum & 0xff00) >> 8), chr(self.headerChecksum & 0xff), self.source, self.destination)
        return ip_hdr;

    def __calculateHeaderChecksum(self):
        ver_ihl = (self.version << 4) + self.ihl
        ip_hdr = struct.pack("!BBHHBBBBcc4s4s", ver_ihl, self.tos, self.totalLength, self.id, self.flags, self.offset,self.ttl, self.protocol, chr(0), chr(0), self.source, self.destination)
        s = cksum(ip_hdr)
        return s

    def toString(self):
        ipheader = self.__getIpHeader()
        return ipheader + self.icmpPacket.toString()


# ICMP Package definition
class ICMPPacket:
    '''
    ICMP Header (in red):

        - Type of ICMP message (8 bits)
        - Code (8 bits)
        - Checksum (16 bits), calculated with the ICMP part of the packet (the IP header is not used). It is the 16-bit one's complement of the one's complement sum of the ICMP message starting with the Type field[10]
        - Header Data (32 bits) field, which in this case (ICMP echo request and replies), will be composed of
            - identifier (16 bits)
            - sequence number (16 bits).

    ICMP Payload: payload for the different kind of answers; can be an arbitrary length, left to implementation detail. However, the packet including IP and ICMP headers must be less than the maximum transmission unit of the network or risk being fragmented.
    '''

    def __init__(self):
        self.data = '56 bytes of dummy data............56 bytes of dummy data'
        self.code = 0;
        self.seq = 0
        self.id = 0

    # Build string to be sent
    def toString(self):
        id_seq = self.__getIdSeq()
        checksum = self.__calculateCheckSum()
        checkSumAdapted = chr(checksum & 0xff) + chr((checksum & 0xff00) >> 8)  # represent 16bit number checksum in 2 byte representation
        return chr(self.type) + chr(self.code) + checkSumAdapted + id_seq + self.data

    def __getIdSeq(self):
        return chr((self.id & 0xff00) >> 8) + chr(self.id & 0x00ff) + chr((self.seq & 0xff00) >> 8) + chr(self.seq & 0x00ff)

    def __calculateCheckSum(self):
        package = chr(self.type) + chr(self.code) + '\000\000' + self.__getIdSeq() + self.data
        return cksum(package)


# Placeholder for statistics values
class PingData:
    def __init__(self):
        self.pktsTrans = 0


def printStats(dest, pingData, initTime):
    print "\n--- " + dest + " ping statistics ---"
    print "%d packets transmitted during %dms" % (pingData.pktsTrans, ((time.time() - initTime) * 1000))


def sendPacket(sock, pingData, destHost, srcHost):
    pkt = ICMPPacket()
    pkt.seq = pingData.pktsTrans
    pkt.id = os.getpid()
    pkt.type = CODE_REQUEST
    ipPacket = IPPacket(icmpPacket = pkt, dest=destHost, src=srcHost)
    packet = ipPacket.toString()
    sock.sendto(packet, (destHost, 0))
    print "REQUEST SENT: %d bytes to %s from %s " % (len(packet) - 20, " (" + destHost + ")", " (" + srcHost + ")")


def executePing(dest, source):
    initTime = time.time()
    pingData = PingData()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Reuse port if in use (broke previous run)
        sock.setsockopt(socket.SOL_IP, socket.IP_HDRINCL, 1) # Include IP header
        sock.setblocking(0)
        sock.settimeout(1000)

        destHost = getDir(dest)
        sourceHost = getDir(source)
        while True:
            pingData.pktsTrans = pingData.pktsTrans + 1
            sendPacket(sock, pingData, destHost, sourceHost)
            time.sleep(1)
    except KeyboardInterrupt:
        printStats(dest, pingData, initTime)
    finally:
        sock.close()


def getDir(dir):
    try:
        hostname, alias, ip = socket.gethostbyaddr(dir)
    except socket.herror:
        ip = [dir]
    return ip[0]

def ping(dest, source):
    try:
        print "PING " + dest + " (" + socket.gethostbyname(dest) + ") FROM " + source + " (" + socket.gethostbyname(source) + ") 56(84) bytes of data."
        executePing(dest, source)
    except socket.gaierror:
        print sys.argv[0] + ": unknown host " + dest + " or " + source


if __name__ == "__main__":
    try:
        destination = sys.argv[1]
        source = sys.argv[2]
    except IndexError:
        print "USE: sudo " + sys.argv[0] + " <destination-host> <source-host>"
        sys.exit(0)
    ping(destination, source)
    sys.exit(0)
