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
import time
import array

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

CODE_RESPONSE = 0

ERRORS = {
    3: "From %s icmp_seq:%d Destination Host Unreachable",
    4: "From %s icmp_seq:%d Source quench",
    5: "From %s icmp_seq:%d Redirection",
    11: "From %s icmp_seq:%d Time to live exceeded",
    12: "From %s icmp_seq:%d Parameter problem"
}

# ICMP Package definition
class IPPacket:
    def __init__(self, ipPackage):
        self.version = int(bin(ord(ipPackage[0]))[:-4],2);
        self.ihl = int(bin(ord(ipPackage[0]))[5:],2);  # 4 right bits from first byte. (IHL which is the number of 32-bit words.)
        self.tos = ord(ipPackage[1])
        self.totalLength = (ord(ipPackage[2]) << 8) + ord(ipPackage[3])
        self.id = (ord(ipPackage[4]) << 8) + ord(ipPackage[5])
        self.flags = ord(ipPackage[6])
        self.offset = ord(ipPackage[7])
        self.ttl = ord(ipPackage[8])
        self.protocol = ord(ipPackage[9])
        self.headerChecksum = (ord(ipPackage[10]) << 8) + ord(ipPackage[11])
        self.source = socket.inet_aton(self.__getIpAddress(ipPackage[12:16]))
        self.destination = socket.inet_aton(self.__getIpAddress(ipPackage[16:20]))

        ipHeaderSize = self.ihl * 4;  #(IHL is the number of 32-bit words.)
        self.icmpPacket = ICMPPacket(ipPackage[ipHeaderSize:])

        header = ipPackage[:ipHeaderSize];
        self.__validateHeaderCheckSum(header)

    def __getIpAddress(self, addressBytes):
        return ".".join([ str(ord(c)) for c in addressBytes])

    def __validateHeaderCheckSum(self, header):
        if cksum(header) != 0:
            print "IP header CheckSum error"
            return False
        return True

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

    def __init__(self, icmpPacket):
        if icmpPacket:
            self.type = ord(icmpPacket[0])
            self.code = ord(icmpPacket[1])
            self.ckecksum = (ord(icmpPacket[3]) << 8) + ord(icmpPacket[2])  # 3rd & 4th byte as a number
            self.id = (ord(icmpPacket[4]) << 8) + ord(icmpPacket[5])
            self.seq = (ord(icmpPacket[6]) << 8) + ord(icmpPacket[7])
            self.data = icmpPacket[8:]
            self.__validateCheckSum(icmpPacket)


    def __validateCheckSum(self, icmpPacket):
        # checksum calculation and comparison with incoming
        if cksum(icmpPacket) != 0:
            print "ICMP CheckSum error"
            return False
        return True


# Placeholder for statistics values
class PingData:
    def __init__(self):
        self.pktsRcvd = 0
        self.responsesRcvd = 0
        self.requestsRcvd = 0
        self.errors = 0


def printStats(pingData, initTime):
    print "\n--- ping statistics ---"
    # Show errors if any
    if pingData.pktsRcvd:
        print "%d packets received, +%d requests, +%d responses, +%d errors, listening during %dms" % \
              (pingData.pktsRcvd, pingData.requestsRcvd, pingData.responsesRcvd, pingData.errors, ((time.time() - initTime) * 1000))
    else:
        print "Nothing was received, waited for %dms" % ((time.time() - initTime) * 1000)


def recvPacket(sock, pingData):
    while True:
        try:
            pktRcv, pktFrom = sock.recvfrom(4096)

            ipPackt = IPPacket(pktRcv);
            pingData.pktsRcvd += 1

            if ipPackt.icmpPacket.type == 8:
                # Echo reply
                pingData.requestsRcvd += 1
                print "REQUEST RECEIVED: %d bytes from %s: ttl=%d " % (len(pktRcv) - 20, " (" + pktFrom[0] + ")", ipPackt.ttl)
                continue

            if ipPackt.icmpPacket.type == 0:
                # Echo reply
                pingData.responsesRcvd += 1
                print "RESPONSE RECEIVED: %d bytes from %s: ttl=%d " % (len(pktRcv) - 20, " (" + pktFrom[0] + ")", ipPackt.ttl)
                continue

            errorCode = ipPackt.icmpPacket.type
            if ERRORS.__contains__(errorCode):
                pingData.errors += 1
                print "ERROR RECEIVED ", ERRORS.get(errorCode) % (pktFrom[0], ipPackt.icmpPacket.seq)
        except socket.error:
            continue


def executePing():
    initTime = time.time()
    pingData = PingData()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        recvPacket(sock, pingData)
    except KeyboardInterrupt:
        printStats(pingData, initTime)
        print "closing"
    finally:
        sock.close()


if __name__ == "__main__":
    try:
        print "PING listener.... starting"
        executePing()
    except socket.gaierror:
        print "PING listener: socket error received "
