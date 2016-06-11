import socket
import sys
import importlib

NUMBER_OF_ARGUMENTS = 4
ARGUMENTS_IN_FILE = 2
BUFF_SIZE = 1024
TEXT = "TEXT "
GO = "GO"
END = "END"
MOVE = "MOVE"
QUIT = "QUIT"
ERROR = "ERROR"

class GameServer():
    def __init__(self, port):
        """
        The function initiates a new GameServer object, creates a new socket
        and connect him to the host

        :param port: int, the port number
        :param game: string, the game that played now
        :param game_arguments: int, arguments of the game (number of players)
        :return: None
        """
        self.__host = socket.gethostname()
        self.__port = port
        self.__address = (self.__host, self.__port)
        self.__conn = socket.socket()
        self.__conn.bind(self.__address)

    def get_socket(self):
        """
        The function returns the players list

        :return: list of Player objects
        """
        return self.__conn

    def send_TEXT_message(self, conn, str_msg):
        """
        The function send a TEXT message to the conn like "TEXT msg"

        :param conn: socket
        :param str_msg: string, the message
        :return: None
        """
        msg = bytes(TEXT + str_msg, "utf-8")
        conn.sendall(msg)

    def send_GO_message(self, conn):
        """
        The function send a GO message to the conn

        :param conn: socket
        :return: None
        """
        msg = bytes(GO, "utf-8")
        conn.sendall(msg)

    def send_END_message(self, conn):
        """
        The function send an END message to the conn

        :param conn: socket
        :return: None
        """
        msg = bytes(END, "utf-8")
        conn.sendall(msg)

    def recv_data(self, conn):
        """
        The function receive data from conn and decode it from bytes

        :param conn: socket
        :return: string: the data received
        """

        data = conn.recv(BUFF_SIZE).decode("utf-8")
        data_type = data[:4]
        if MOVE in data_type or QUIT in data_type:
            # If the data is valid according the protocol
            return data
        else:
            # If the data is not valid, return error
            return ERROR

    def close(self):
        """
        The function close the socket of the server

        :return: None
        """
        self.__conn.close()


game_arguments = 0
port = 0
game_name = ""

arguments = sys.argv
# Get arguments of program
if len(arguments) == NUMBER_OF_ARGUMENTS:
    # If the arguments entered with the command to run the program
    port = int(arguments[1])
    game_name = arguments[2]
    game_arguments = int(arguments[3])
elif len(arguments) == ARGUMENTS_IN_FILE:
    # If the arguments located on a file
    filename = arguments[1]
    file = open(filename)
    port = int(file.readline().rstrip('\n'))
    game_name = file.readline().rstrip('\n')
    game_arguments = int(file.readline().rstrip('\n'))
    file.close()

server = GameServer(port)

# Call the requested game taken from arguments and run it using the
# game arguments
game_class = importlib.import_module(game_name)
game = getattr(game_class, game_name)(server, game_arguments)
game.game()

server.close()  # After the game finished, close the server