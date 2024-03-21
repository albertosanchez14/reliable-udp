from socket import *
import sys
import time


class Packet:
    def __init__(self, type=None, seqnum=None, length=None, data=None):
        self.type = type
        self.seqnum = seqnum
        self.length = length
        self.data = data

    def encode(self) -> bytes:
        """
        Function to encode the packet
        """
        return f"{self.type},|,{self.seqnum},|,{self.length},|,{self.data}".encode()
    
    def decode(self, packet: bytes):
        """
        Function to decode the packet
        """
        packet = packet.decode()
        packet = packet.split(",|,")
        self.type = int(packet[0])
        self.seqnum = int(packet[1])
        self.length = int(packet[2])
        self.data = packet[3]
        return self
    
    def __str__(self):
        return f"Type: {self.type}, Seqnum: {self.seqnum}, Length: {self.length}, Data: {self.data}"


class Sender:
    def __init__(self, senderPort):
        self._senderPort = senderPort

    def stablish_udp(self) -> None:
        self._clientSocket = socket(AF_INET, SOCK_DGRAM)
    
    def send(self, receiverAddress, receiverPort, timeout, file_name) -> None:
        """
        Function to send the file over UDP
        """
        # Clear the log files
        open("seqnum.log", "w").close()
        open("ack.log", "w").close()
        # Set to store the acks
        acks = set()
        # Get the data packets from the file
        data = self._load_file(file_name)        
        # Send the data packets
        while len(acks) < len(data):
            # Send the packets
            self._send_packets(data, acks, timeout, receiverAddress, receiverPort)
            # Receive the acks in the timeout
            start = time.time() * 1000
            end = start
            acklog = open("ack.log", "a", newline="\n")
            acklog.write("Acks received: ")
            while end - start < timeout:
                try:
                    # Wait for the acks
                    self._clientSocket.settimeout(timeout/1000)
                    message, serverAddress = self._clientSocket.recvfrom(2048)
                    self._clientSocket.settimeout(None)
                    # Get the ack packet
                    packet = Packet().decode(message)
                    acks.add(packet.seqnum)
                    # Log the acks
                    acklog.write(str(packet.seqnum) + ", ")
                    end = time.time() * 1000
                except TimeoutError:
                    end = time.time() * 1000
            # Remove the last comma
            acklog.seek(acklog.tell() - 2, 0)
            acklog.truncate()
            # Close the log file
            acklog.write("\n")
            acklog.close()
        
        # Send EOT
        eot_packet = Packet(2, 0, 0, None)
        self._clientSocket.sendto(eot_packet.encode(), (receiverAddress, receiverPort))
        
        # Receive the EOT ACK
        message, serverAddress = self._clientSocket.recvfrom(2048)
        packet = Packet().decode(message)
        if packet.type == 1:
            self._clientSocket.close()
            return

    def _load_file(self, file_name) -> list[Packet]:
        """
        Function to load the file into packets of 500 bytes
        """
        data = []
        seqnum = 1
        with open(file_name, "r", encoding="utf-8-sig") as file:
            chunk = file.read(500)
            data.append(Packet(0, seqnum, len(chunk), chunk))
            while chunk:
                chunk = file.read(500)
                seqnum += 1
                data.append(Packet(1, seqnum, len(chunk), chunk))
        return data

    def _send_packets(self, data: list[Packet], acks, timeout, receiverAddress, receiverPort) -> None:
        """
        Function to send the packets
        """
        # Open the log file
        seqnumlog = open("seqnum.log", "a")
        seqnumlog.write("Sending packets: ")
        # Send the packets
        for packet in data:
            if packet.seqnum not in acks:
                seqnumlog.write(str(packet.seqnum) + ", ")
                self._clientSocket.sendto(packet.encode(), (receiverAddress, receiverPort))
        # Remove the last comma
        seqnumlog.seek(seqnumlog.tell() - 2, 0)
        seqnumlog.truncate()
        # Close the log file
        seqnumlog.write("\n")
        seqnumlog.close()
        return


if __name__ == "__main__":
    # Arguments
    if len(sys.argv) != 6:
        print("Usage: python3 sender.py <receiverAddress> <receiverPort> <senderPort> <timeout> <file_name>")
        sys.exit()
    receiverAddress = sys.argv[1]
    if not sys.argv[2].isdigit():
        print("The receiverPort must be a number")
        sys.exit()
    receiverPort = int(sys.argv[2])
    if not sys.argv[3].isdigit():
        print("The senderPort must be a number")
        sys.exit()
    senderPort = int(sys.argv[3])
    if not sys.argv[4].isdigit():
        print("The timeout must be a number")
        sys.exit()
    timeout = int(sys.argv[4])
    file_name = sys.argv[5]
    # Sender
    sender = Sender(senderPort)
    # Stablish the UDP connection
    sender.stablish_udp()
    # Send the file
    sender.send(receiverAddress, receiverPort, timeout, file_name)
