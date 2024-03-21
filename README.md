# Reliable UDP file transfer

Implementation of a reliable file transfer protocol, which could be used to
reliably transfer a text file from one host to another over UDP. The protocol is able to handle network errors.

## Run the program
To run the program first it is necessary to run the receiver.py file with the following arguments:
```console
> python receiver.py <receiverPort> <drop_prob> <file_name>
```
Where the 4 required arguments are the following:
 - receiverPort = UDP port number used by the receiver to receive data from the sender
 - drop_prob = drop probability
 - file_name = name of the file into which the received data is written

When the receiver.py is running then it is needed to run the sender.py file using also the terminal with the following command:
```console
 > python sender.py <receiverAddress> <receiverPort> <senderPort> <timeout> <file_name>
```
Where the 6 required arguments are the following:
 - receiverAddress = host address of the receiver
 - receiverPort = UDP port number used by the receiver to receive data from the sender
 - senderPort = UDP port number used by the sender to send data and receive ACKs from the receiver
 - timeout = timeout interval in units of millisecond
 - file_name = name of the file to be transferred

## Logs
Each program generates 2 log files, the sender.py generates the seqnum.log and ack.log and the receiver.py generates the arrival.log and dropped.log.

- seqnum.log: Records the sequence number of the packets sent.
- ack.log: Records the sequence numbers of all the ACK packets that the sender receives during the entire period of transmission.
- arrival.log: Records the sequence numbers of all the data packets that the receiver receives during the entire period of transmission.
- dropped.log: Records the sequence numbers of all the data packets dropped by the receiver.

## Testing
To test the program I will transfer a simple text.

### File transfer with loss (drop probability = 0)
First I execute the command:
```console
python.exe receiver.py 9994 0 received.txt 
```
And then I execute:
```console
python.exe sender.py ubuntu2204-002 9994 9992 50 test.txt
```
As the drop rate is 0, the drop.log file is empty because no package was lost and arrival.log, ack.log and seqnum.log have the packets logged from lower to higher because all packages are sent in order and all of them are acknowledge.

### File transfer with loss (drop probability = 0.5)
First I execute the command:
```console
python.exe receiver.py 9994 0.5 received.txt 
```
And then I execute:
```console
python.exe sender.py ubuntu2204-002 9994 9992 50 test.txt
```
Now the drop rate is 0.5 and some packages are dropped in the process. Because of this the sender needs to send the non acknowledge packets.

### Transfering Mary Shelley's Frankenstein
Now my final test will be to transfer a larger file like Mary Shelley’s magnum opus “Frankenstein” with a high drop probability as it is 0.8.
First I execute the command:
```console
python.exe receiver.py 9994 0.8 received.txt 
```
And then I execute:
```console
python.exe sender.py ubuntu2204-002 9994 9992 50 frankenstein.txt
```
After a couple of seconds the logs are printed and the text is transfered. To check that the file has been succesfully transfered I have used the webpage diffchecker.com and I have seen that both files are identical, which can be see using the following link: https://www.diffchecker.com/CxVFiZMO/.
