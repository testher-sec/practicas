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

import socket
import sys
import os
import time
import array

CODE_REQUEST = 8
CODE_RESPONSE = 0

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

ERRORS = {
    3: "From %s icmp_seq:%d Destination Host Unreachable",
    4: "From %s icmp_seq:%d Source quench",
    5: "From %s icmp_seq:%d Redirection",
    11: "From %s icmp_seq:%d Time to live exceeded",
    12: "From %s icmp_seq:%d Parameter problem"
}


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

    def __init__(self, icmpPacket=None):
        if icmpPacket:
            self.type = ord(icmpPacket[0])
            self.code = ord(icmpPacket[1])
            self.ckecksum = (ord(icmpPacket[3]) << 8) + ord(icmpPacket[2])  # 3rd & 4th byte as a number
            self.id = (ord(icmpPacket[4]) << 8) + ord(icmpPacket[5])
            self.seq = (ord(icmpPacket[6]) << 8) + ord(icmpPacket[7])
            self.data = icmpPacket[8:]
            self.__validateCheckSum();
        else:
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

    def __validateCheckSum(self):
        # checksum calculation and comparison with incoming
        if self.__calculateCheckSum() != self.ckecksum:
            print "CheckSum error"
            return False
        return True

# Placeholder for statistics values
class PingData:
    def __init__(self):
        self.times = list()
        self.pktsTrans = 0
        self.pktsRcvd = 0
        self.errors = 0


def printStats(dest, pingData, initTime):
    print "\n--- " + dest + " ping statistics ---"
    # Show errors if any
    print "%d packets transmitted, %d received, +%d errors, %d%% packet loss, time %dms" % (pingData.pktsTrans, \
                                                                                            pingData.pktsRcvd, \
                                                                                            pingData.errors, \
                                                                                            100 - 100 * pingData.pktsRcvd / pingData.pktsTrans, \
                                                                                            (
                                                                                                    time.time() - initTime) * 1000)

    # Show statistics if any successful
    if pingData.pktsRcvd:
        max = pingData.times[0]
        min = pingData.times[0]
        sum = 0
        # Compute Max, Min and Average
        for i in xrange(len(pingData.times)):
            if pingData.times[i] > max:
                max = pingData.times[i]
            if pingData.times[i] < min:
                min = pingData.times[i]
            sum += pingData.times[i]
        avg = sum / len(pingData.times)
        print "rtt min/avg/max = %.3f/%.3f/%.3f ms\n" % (min, avg, max)
    else:
        print ""


def sendPacket(sock, pingData, host, name):
    pkt = ICMPPacket()
    pkt.seq = pingData.pktsTrans
    pkt.id = os.getpid()
    pkt.type = CODE_REQUEST
    packet = pkt.toString()
    sock.sendto(packet, (host, 0))
    timeSent = time.time()
    return recvPacket(sock, pingData, timeSent, name)


def recvPacket(sock, pingData, timeSent, name):
    while True:
        try:
            pktRcv, pktFrom = sock.recvfrom(4096)
            timeRecv = (time.time() - timeSent) * 1000.0

            ipHeaderSize = int(bin(ord(pktRcv[0]))[5:],2) * 4;  # 4 right bits from first byte. (IHL which is the number of 32-bit words.)

            # Ignore ping requests
            if ord(pktRcv[ipHeaderSize]) == 8:
                continue

            pktICMPrcv = ICMPPacket(pktRcv[ipHeaderSize:])  # remove first 'ipHeaderSize' bytes from IP header

            # We need only the first 20 bytes for ICMP
            if ord(pktRcv[ipHeaderSize]) == 0:
                # Echo reply
                pingData.times.append(timeRecv)
                print "%d bytes from %s: ttl=%d time=%.3f ms" % (len(pktRcv) - 20, name + " (" + pktFrom[0] + ")", ord(pktRcv[8]), timeRecv)
                return 1

            errorCode = ord(pktRcv[ipHeaderSize])
            if ERRORS.__contains__(errorCode):
                pingData.errors += 1
                print ERRORS.get(errorCode) % (pktFrom[0], pktICMPrcv.seq)

            break;

        except socket.error:
            continue


def executePing(dest):
    initTime = time.time()
    pingData = PingData()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        try:
            hostname, alias, ip = socket.gethostbyaddr(dest)
        except socket.herror:
            hostname = dest
            alias = None
            ip = [hostname]
        sock.setblocking(0)
        sock.settimeout(1000)
        if alias:
            name = alias[0]
        else:
            name = hostname
        while True:
            pingData.pktsTrans = pingData.pktsTrans + 1
            isSent = sendPacket(sock, pingData, ip[0], name)
            if isSent == 1:
                # Sent
                pingData.pktsRcvd = pingData.pktsRcvd + isSent
            time.sleep(1)
    except KeyboardInterrupt:
        printStats(dest, pingData, initTime)
    finally:
        sock.close()


def ping(dest):
    try:
        print "PING " + dest + " (" + socket.gethostbyname(dest) + ") 56(84) bytes of data."
        executePing(dest)
    except socket.gaierror:
        print sys.argv[0] + ": unknown host " + dest


if __name__ == "__main__":
    try:
        destination = sys.argv[1]
    except IndexError:
        print "USE: sudo " + sys.argv[0] + " <insert host here>"
        sys.exit(0)
    ping(destination)
    sys.exit(0)
