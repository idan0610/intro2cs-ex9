import socket
import sys

BUFF_SIZE = 1024
TEXT = "TEXT"
GO = "GO"
END = "END"
MOVE = "MOVE "
QUIT = "QUIT"
ERROR = "ERROR"


class GameClient():

    def __init__(self, game, host, port):
        """
        The function initiates a new GameClient object, creates a new socket
        and connect him to the host

        :param game: string, the game that played now
        :param host: string, name of computer of host
        :param port: int, the port number
        :return: None
        """

        self.__game = game
        self.__host = host
        self.__port = port
        self.__address = (host, port)
        self.__conn = socket.socket()
        self.__conn.connect(self.__address)
        self.__is_active = True

    def get_is_active(self):
        """
        The function returns the status of the client

        :return: is_active: bool
        """

        return self.__is_active

    def recv_data(self):
        """
        The function receive data from the host and decode it from bytes

        :return: string: the data received
        """

        return self.__conn.recv(BUFF_SIZE).decode("utf-8")

    def send_MOVE_message(self, str_msg):
        """
        The function send a MOVE message to the host like "MOVE msg"

        :param str_msg: string the message
        :return: None
        """

        msg = bytes(MOVE + str_msg, "utf-8")  # Convert to bytes
        self.__conn.sendall(msg)

    def send_QUIT_message(self):
        """
        The function send a QUIT message to the host

        :return: None
        """

        msg = bytes(QUIT, "utf-8")  # Convert to bytes
        self.__conn.sendall(msg)

    def handling_data(self, data):
        """
        The function take the data received from host and handling it
        according to its type

        :param data: string, data got from recv_data
        :return: None
        """

        data_type = data[:4]  # Slice the first 4 chars to check its type
        if TEXT in data_type:
            # The data is TEXT type, print it from after the string "TEXT "
            print(data[5:])
        elif GO in data_type:
            # The data is GO type, request for input and send it
            str_msg = input()
            if str_msg in "quit" or str_msg == "QUIT":
                # If the client send "quit" or "QUIT", he will disconnect
                self.send_QUIT_message()
            else:
                self.send_MOVE_message(str_msg)
        else:
            # If data_type is END, or the server deviate from the protocol,
            # close the connection and change is_active to False
            self.close()
            self.__is_active = False

    def close(self):
        """
        The function close the socket of the client

        :return: None
        """
        self.__conn.close()

# Get arguments of the file
arguments = sys.argv
game = arguments[1]
host = arguments[2]
port = int(arguments[3])

client = GameClient(game, host, port)

while True:
    data = client.recv_data()
    client.handling_data(data)

    if not client.get_is_active():
        # if the client is no longer active
        break