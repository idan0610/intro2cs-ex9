import socket
from player import *

BUFF_SIZE = 1024
TIMEOUT = 30
TOTAL_SUM = 30
ERRORS_LIMIT = 5
QUIT = "QUIT"
ERROR = "ERROR"
ERROR_INPUT = "ERROR bad input. try again."
WIN = "you win"
LOSE = "you lose"
WELCOME = "welcome to the game"


class numbers():
    def __init__(self, server, game_arguments):
        """
        The function initiates a new Numbers object (game)

        :param server: GameServer object, the server running the game
        :param game_arguments: int, number of players
        :return: None
        """
        self.__server = server
        self.__sum = 0
        self.__game_argument = game_arguments
        self.__players_list = []

    def players_connection(self):
        """
        The function get connections from clients, create a player object
        for each client, add it to the list of players and send a welcome
        message to the client

        :return: None
        """
        for i in range(self.__game_argument):
            # Get connections until the limit of number of players taken from
            # game arguments
            server_socket = self.__server.get_socket()
            server_socket.listen(5)
            client_conn, client_address = server_socket.accept()
            player = Player(client_conn, client_address)
            self.__server.send_TEXT_message(client_conn, WELCOME)
            self.__players_list.append(player)

    def players_disconnection(self):
        """
        The function disconnect all the players sockets

        :return: None
        """
        for i in range(len(self.__players_list)):
            player = self.__players_list[i]
            player_conn = player.get_socket()
            player_conn.close()

    def remove_player(self, player, index):
        """
        The function send an END message to the player and change its status
        to False

        :param player: Player object
        :return: None
        """
        player_conn = player.get_socket()
        self.__server.send_END_message(player_conn)
        player.set_status(False)

    def recv_data(self, player):
        """
        The function receive data from player, check if it is valid according
        the game rules and returns the data if it is valid (QUIT or number
        between 1 to 9) or ERROR if it is not valid (string other then
        QUIT or number not between 1 to 9)

        :param player: Player object
        :return: data: string
        """
        player_conn = player.get_socket()
        player_errors = 0  # Max limit of tries for input is 5
        server = self.__server

        while player_errors < ERRORS_LIMIT:
            if player_errors == 0:
                # First try for input, ask player asking for
                # number
                msg = "sum is " + str(self.__sum) + " enter number:"
            else:
                # Not the first try, explain the player he made a mistake
                msg = ERROR_INPUT

            server.send_TEXT_message(player_conn, msg)
            server.send_GO_message(player_conn)
            player_conn.settimeout(TIMEOUT)  # Timeout for input is 30 seconds
            try:
                data = server.recv_data(player_conn)
            except socket.timeout:
                # If the player didn't entered input on time
                data = ERROR
                break

            if data == QUIT or data == ERROR:
                break
            else:
                # Take only the data after "MOVE "
                data = data[5:]

            if data.isdigit():
                # The data is number, convert it to int and check if it is on
                # range
                data = int(data)
                if data <= 0 or data >= 10:
                    # If the data is not in range
                    player_errors += 1
                    continue
                else:
                    break
            else:
                # The data is not a number
                player_errors += 1
        else:
            # The player reached his limit of tries
            data = ERROR

        return data

    def end_game(self, winner_player, winner_index):
        """
        The function end the game in case it finished correctly

        :param winner_player: Player object, the winner
        :param winner_index: int, the winner index
        :return: Noe
        """
        # First, inform the winner he won, and remove him from game
        server = self.__server
        player_conn = winner_player.get_socket()
        server.send_TEXT_message(player_conn, WIN)
        self.remove_player(winner_player, winner_index)

        # Now, inform each loser he lost, and remove him also
        for i in range(len(self.__players_list)):
            loser_player = self.__players_list[i]
            if loser_player.get_status():
                # Inform only the players still in game
                loser_player_conn = loser_player.get_socket()
                server.send_TEXT_message(loser_player_conn, LOSE)
                self.remove_player(loser_player, i)

    def get_next_index(self, index):
        """
        The function find the next active player and returns its index
        (assume he is exist)

        :param index: int, the index of the last player played
        :return: index: int, the index of next player
        """

        found = False
        while not found:
            # Run until you find the next player active
            if index + 1 == len(self.__players_list):
                # If the test reached the end of players list, return to the
                # start of list
                index = 0
            else:
                index += 1
            player = self.__players_list[index]
            # If the current player status is True, we found the next active
            # player
            found = player.get_status()

        return index

    def players_left(self):
        """
        The function finds how many active players left in game

        :return: counter: int, number of active players left
        """
        counter = 0
        for i in range(len(self.__players_list)):
            player = self.__players_list[i]
            if player.get_status():
                # If the player is active
                counter += 1
        return counter


    def game(self):
        """
        This function is the main function responsible running the game. The
        server calls this function to start the game

        :return: None
        """
        self.players_connection()  # Connect the players
        server = self.__server
        # We start with index = -1 because on first iteration of the while
        # loop, the index will change to 0 (first player)
        index = -1
        while True:
            if self.players_left() == 0:
                # If there are no players left, there is an error with
                # connection, print an error message and break the loop
                print(ERROR)
                break

            # Get the index of the next player
            index = self.get_next_index(index)

            player = self.__players_list[index]
            player_conn = player.get_socket()

            if self.players_left() == 1:
                # If there is only 1 player, this is because all other players
                # left, so the remaining player is the winner
                server.send_TEXT_message(player_conn, WIN)
                self.remove_player(player, index)
                break

            data = self.recv_data(player)

            if data == QUIT or data == ERROR:
                # If the player asked to quit, or did not entered a valid
                # input, remove it from game
                self.remove_player(player, index)
                continue
            else:
                # If the data is valid, add it to the sum
                self.__sum += data

            if self.__sum >= TOTAL_SUM:
                # If sum reached 30, the game has ended
                self.end_game(player, index)

        self.players_disconnection()  # Disconnect all players