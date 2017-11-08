
import sys
import socket
import select
import re
import utils
class Server:
    host = "127.0.0.1"
    socket_list = []
    # The channel_dict refers to the mapping from the channel to the sockets the chennel has
    channel_sock_dict={}
    #The channel_dict refers to the  mapping from  the sock to the channel it belongs to
    sock_channel_dict={}
    sock_name_dict={}
    server_socket=None
    REC_BUFFER = 4096
    MSG_LENGTH=200
    port = 80
    ListCOMMAND=re.compile(r'/list')
    CREATECHANNELCOMMAND=re.compile(r'/create ')
    JOINCHANNELCOMMND=re.compile(r'/join')
    #use this pattern to get the name and channel from the received data
    CHANNEL_NAME_PATTERN = re.compile(r'/name=|/channel=')

    #init the server
    def __init__(self,port):
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.port=port
            self.server_socket.bind((self.host,port))
            self.server_socket.listen(10)
      # add server socket object to the list of readable connections
            self.socket_list.append(self.server_socket)
            print ("Chat server started on port " + str(self.port))
            # broadcast chat messages to all connected clients
    def create_channel(self,sock,name,channel):
        if not self.channel_sock_dict.has_key(channel):
            self.channel_sock_dict[channel]=[sock]
            print(self.channel_sock_dict[channel])
            self.sock_channel_dict[sock]=[channel]
            print(self.sock_channel_dict[sock])
            self.sock_name_dict[sock]=name
            print(self.sock_name_dict[sock])



    # send the list of all the channels' names to the appointed socket
    def send_channel_list(self,sock):
        result=""
        for key in self.channel_sock_dict.keys():
            result+=key
        sock.send(result.encode("utf-8"))
    def join_channel(self,name,channel,sock):
        channel.strip("\n")
        print("Now entering the join_channel_function")
        print(channel)
        print(self.channel_sock_dict.keys())
        if  not self.channel_sock_dict.keys().__contains__(channel):
            sock.send("The channel does not exist".encode("utf-8"))
            return False
        if  sock not in self.socket_list:
            print("Now entering the sock judge section")
            sock.close()
            return False
        self.channel_sock_dict[channel].append(sock)
        print(self.channel_sock_dict[channel])
        if not sock in self.sock_channel_dict.keys():
            self.sock_channel_dict[sock]=[channel]
            print(self.sock_channel_dict[sock])
        else:
            self.sock_channel_dict[sock].append(channel)
            print(self.sock_channel_dict[sock])
        if not self.sock_name_dict.has_key(sock):
            self.sock_name_dict[sock]=name
            print(self.sock_name_dict[sock])

        self.broadcast_to_channel(self,channel,sock,"[%s:%s] joined the ")

        return True
    def receive_send_message(self):
        while True:
            # get the list sockets which are ready to be read through select
            # 4th arg, time_out  = 0 : poll and never block

            ready_to_read, ready_to_write, in_error = select.select(self.socket_list, [], [], 0)
            for sock in ready_to_read:
                # a new connection request recieved
                if sock is self.server_socket:
                    sockfd, addr = self.server_socket.accept()
                    self.socket_list.append(sockfd)
                    print ("Client [%s:%s] connected" %addr)

                # a message from a client, not a new connection
                else:
                  try:

                    # In Windows, sometimes when a TCP program closes abruptly,
                    # a "Connection reset by peer" exception will be thrown
                     data = sock.recv(self.REC_BUFFER)
                     if data:
                        # The following are the reguar expression match results of all the commands pattern
                        print(data)
                        list_command_match=re.search(self.ListCOMMAND,data)
                        create_channel_match=re.search(self.CREATECHANNELCOMMAND,data)
                        join_command_match=re.search(self.JOINCHANNELCOMMND,data)
                        print(list_command_match)
                        print(create_channel_match)
                        print(join_command_match)
                        if list_command_match:
                            self.send_channel_info(sock)
                            continue
                        if create_channel_match:
                            #The create command message should be "/create channel=/w+ name=/w+
                            print(re.split(self.CHANNEL_NAME_PATTERN, data))
                            channel=re.split(self.CHANNEL_NAME_PATTERN, data)[2].strip("\n")
                            name=re.split(self.CHANNEL_NAME_PATTERN,data)[1]
                            print(channel)
                            print(name)
                            # create the channel and bind the channel and name to the socket
                            self.create_channel(sock, name,channel)
                            continue
                        if join_command_match:
                            channel = re.split(self.CHANNEL_NAME_PATTERN, data)[2]
                            name = re.split(self.CHANNEL_NAME_PATTERN, data)[1]
                            if self.join_channel(name,channel,sock):
                                self.broadcast_to_channel(channel,sock,name+"has login in the room")
                            continue
                        print("Now the command parse is over")
                        print(self.sock_channel_dict[sock])
                        for channel in self.sock_channel_dict[sock]:
                            print("now entering the channel selection before the broadcast_to_channel function ")
                            print(channel)
                            self.broadcast_to_channel(channel,sock,self.sock_name_dict[sock]+data)

                  except:
                      continue

        self.server_socket.close()

    def remove_connection(self,sock,addr):
        print ( "Client (%s, %s) is offline" % addr)
        sock.close()
        self.socket_list.remove(sock)

    def broadcast_to_channel(self,channel,sock, message):
        print ("now entering into the broadcast_to_channel function ")
        for socket in self.channel_sock_dict[channel]:
            print(socket)
            # send the message only to peer
            if socket != self.server_socket and socket != sock:
                try:
                    socket.send(message.encode('utf-8'))
                except:
                    # broken socket connection may be, chat client pressed ctrl+c for example
                    socket.close()
                    self.socket_list.remove(socket)
    def split_msg(self,messgae):


if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print ('Usage : python Server.py  port')
        sys.exit()
    port=sys.argv[1]
    server=Server(int(port))
    server.receive_send_message()

