
import socket
import utils
import sys
import string
import select
import re
class Client:
    LISTPATTERN = re.compile(r"/list")
    CREATEPATTERN = re.compile(r"/create")
    JOINPATTERN=re.compile(r"/join")
    MSG_LENGTH=200;
    def __init__(self,host,port,name):
        self._host=host
        self._port=port
        self._socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.get_channel_command="/get channel"
        self._channel=""
        self._name=name
    def create_channel(self,channel):
        self._channel=channel
    def join_channel(self,channel):
        self.channel=channel
    def get_channel(self):
        return self._channel
    def prompt(self):
        sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)
        sys.stdout.flush()
    def connect(self):
        try:
            self._socket.connect((self._host,12345))
            self._socket.settimeout(2)
            self._socket.send(self._name+"succssfully connected to {0}{1}".format(self._host,self._port))
            print ("connected to the {0}{1}".format(self._host,self._port))
        except Exception:
            print("cannot connected to{0}{1}".format(self._host,self._port))
            sys.exit()
    def send_message_loop(self):
        while True:
            socket_list = [sys.stdin, self._socket]
            ready_to_read, ready_to_write, in_error = select.select(socket_list, [], [])
            for sock in ready_to_read:
                 if sock == self._socket:
                     # incoming message from remote server      , s
                    data = sock.recv(4096)
                    if not data:
                        print( '\nDisconnected from chat server ')
                        sys.exit()
                    else:
                        print(self.recover_msg(data))
                 else:
                    msg = sys.stdin.readline()
                    create_channel_match = re.search(self.CREATEPATTERN, msg)
                    join_command_match = re.search(self.JOINPATTERN, msg)
                    print(create_channel_match)
                    print(join_command_match)
                    if create_channel_match:
                         channel=re.split(self.CREATEPATTERN,msg)[1].strip(" ").strip("\n")
                         print(channel)
                         self._channel=channel
                         msg+="/name={0} /channel={1}".format(self._name,self._channel)
                         print(msg)
                    if join_command_match:
                         print(re.split(self.JOINPATTERN, msg))
                         channel = re.split(self.JOINPATTERN, msg)[1].strip(" ").strip("\n")
                         print(channel)
                         self._channel = channel
                         msg += "/name={0} /channel={1}".format(self._name, self._channel)
                         print(msg)
                    self._socket.send(self.fill_message(msg).encode("utf-8"))
                    self.prompt()
    def fill_message(self,data):
        if len(data)>self.MSG_LENGTH:
            return data[0:len(data)]
        else:
            #fill  the data until its lenth is equal to the MSG_LENGTH
           new_data=str(data)
           while len(new_data)<self.MSG_LENGTH:
               new_data+=" "
           return new_data

    """
    As the message received from the server are filled with space character after the content of the message
    so we need to  recover  the original message
    """
    def recover_msg(self,data):
        if not len(data)==self.MSG_LENGTH:
            return data
        else:
            i=len(data)-1
            while data[i]==" ":
                i=i-1
            return data[0:i+1]
if __name__ == "__main__":
        if (len(sys.argv) < 4):
            print ('Usage : python host port name')
            sys.exit()
        client=Client(sys.argv[1],int(sys.argv[2]),sys.argv[3])

        client.connect()
        client.send_message_loop()



