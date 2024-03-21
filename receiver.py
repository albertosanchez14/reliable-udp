from socket import *
import random
import sys
from sender import Packet


class Receiver:
    def __init__(self, receiverPort, drop_prob, file_name):
        self._receiverPort = receiverPort
        self._drop_prob = drop_prob
        self._file_name = file_name
        # Data structures to store the received packets
        self.received_packets = []

    def stablish_udp(self):
        self._serverSocket = socket(AF_INET, SOCK_DGRAM)
        self._serverSocket.bind(('', self._receiverPort))

    def receive(self):
        """
        Function to start the receive process
        """
        # Clear the .log files
        open("arrival.log", "w").close()
        open("drop.log", "w").close()
        # Receive the first packet
        message, clientAddress = self._serverSocket.recvfrom(2048)
        packet = Packet().decode(message)
        # Log the received packet
        arrival_log = open("arrival.log", "a")
        arrival_log.write("Received packets: ")
        last_seqnum = 0
        # Log the dropped packets
        drop_log = open("drop.log", "a")
        drop_log.write("Dropped packets: ")
        # Packet is not EOT
        while packet.type != 2:
            # Log the packets
            if packet.seqnum <= last_seqnum:
                # Received packets
                arrival_log.seek(arrival_log.tell() - 2, 0)
                arrival_log.truncate()
                arrival_log.write("\nReceived packets: " + str(packet.seqnum) + ", ")
                # Dropped packets
                drop_log.seek(drop_log.tell() - 2, 0)
                drop_log.truncate()
                drop_log.write("\nDropped packets: ")
            else:
                arrival_log.write(str(packet.seqnum) + ", ")
            last_seqnum = packet.seqnum
            # Receive the corresponding ack packet
            ack_packet = self.rec_packet(packet, drop_log)
            # Send the ACK packet
            if ack_packet is not None:
                self._serverSocket.sendto(ack_packet.encode(), clientAddress)
            # Get the next packet
            message, clientAddress = self._serverSocket.recvfrom(2048)
            packet = Packet().decode(message)
        # Close the log file
        arrival_log.seek(arrival_log.tell() - 2, 0)
        arrival_log.truncate()
        arrival_log.close()
        drop_log.seek(drop_log.tell() - 2, 0)
        drop_log.truncate()
        drop_log.close()
        # Send EOT
        eot_packet = Packet(2, packet.seqnum, 0, None)
        self._serverSocket.sendto(eot_packet.encode(), clientAddress)
        # Packet is EOT, write the received data to the file
        self._save_to_file()
        # Close the connection
        self._serverSocket.close()
        return

    def rec_packet(self, packet, drop_log) -> Packet | None:
        """
        Function to handle the received packet
        """
        # If the packet is not EOT, drop the packet with the specified/input probability; 
        if random.random() < self._drop_prob:
            drop_log.write(str(packet.seqnum) + ", ")
            return None
        # If the packet is not an EOT and was not dropped, acknowledge the packet; 
        # the seqnum of the ACK packet should be the same as the seqnum of the received packet; 
        seqnum = packet.seqnum
        ack_packet = Packet(0, seqnum, 0, None)
        # If the packet is a duplicate (i.e., if it was previously received, 
        # not dropped and acknowledged), it should be discarded;
        for pack in self.received_packets:
            if seqnum == pack.seqnum:
                return None
        # If the packet is out-of-order, it should be buffered. 
        # Save the packet
        self.received_packets.append(packet)
        return ack_packet
    
    def _save_to_file(self) -> None:
        """
        Function to save the received data to a file
        """
        f = open(self._file_name, 'wb')
        # Received data should be reordered before it is saved in the file.
        self.received_packets.sort(key=lambda x: x.seqnum)
        for packet in self.received_packets:
            f.write(packet.data.encode())
        f.close()


if __name__ == "__main__":
    # Handle the input arguments
    if len(sys.argv) != 4:
        print("Usage: python receiver.py <receiver_port> <drop_prob> <file_name>")
        sys.exit(1)
    if not sys.argv[1].isdigit():
        print("The receiver port must be an integer")
        sys.exit(1)
    if not sys.argv[2].replace(".", "").isdigit():
        print("The drop probability must be a float")
        sys.exit(1)
    elif float(sys.argv[2]) < 0 or float(sys.argv[2]) > 1:
        print("The drop probability must be between 0 and 1")
        sys.exit(1)
    # Get the input parameters
    receiverPort = int(sys.argv[1])
    drop_prob = float(sys.argv[2])
    file_name = sys.argv[3]
    # Create the receiver
    receiver = Receiver(receiverPort, drop_prob, file_name)
    # Stablish the UDP connection
    receiver.stablish_udp()
    # Start the receive process
    receiver.receive()
