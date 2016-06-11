import socket

class Player():
    def __init__(self, socket, address):
        """
        The function initiates a new Player object
        :param socket: socket, connection of player
        :param address: address
        :return: None
        """
        self.__socket = socket
        self.__address = address
        self.__status = True  # status of player, is active or not

    def get_socket(self):
        """
        The function returns the socket of the player

        :return: self.__socket: socket of player
        """
        return self.__socket

    def get_status(self):
        """
        The function returns the status of player

        :return: self.__status: bool, the status of player
        """
        return self.__status

    def set_status(self, value):
        """
        The function set the status of player to value

        :param value: bool, new status of player (True or False)
        :return: None
        """
        self.__status = value

