from src.Utils import *  # importing my external file for accessibility to utilising classes.
from random import randint

# global variables of the program.
db = SQLManager("Database.db")
menu = Menu
users = {}


# The main body of the program.
def main():
    handle_users()
    while True:
        play_games()
        store_scores()
        display_scores()
        try:
            again = input("\nWould you like to play another game?: ").lower()[0]
            if again != 'y':
                break
        except IndexError:
            pass
    db.close()


# gets a validated password from user for stricter authentication when signing up.
def get_validated_pass():
    # checks if a string contains a number.
    def contains_number(text: str):
        for word in text:
            if word.isnumeric():
                return True
        return False

    # checks if a string contains a symbol.
    def contains_symbol(text: str):
        for word in text:
            if word in ["$", "£", "#", "!", "^", "&", " ", "*", "(", ")", "-", "_", "+", "=", "[", "]", ".", ",", "/",
                        "?", "~", "@"]:
                return True
        return False

    # checks if a string contains a letter.
    def contains_letter(text: str):
        for word in text:
            if word.isalpha():
                return True
        return False

    # main code of the function.
    while True:
        password = input("Please enter your password: ")
        if (len(password) < 6) or (len(password) > 12):
            print("Your password is supposed to be between 6-12 characters!")
        elif contains_symbol(password) and contains_number(password) and contains_letter(password):
            return password
        else:
            print("Your password needs to contain a symbol, a number and/or a letter!")


# gets a validated username from user for stricter authentication when signing up.
def get_validated_name():
    global db  # accessing global database variable.
    while True:
        username = input("Please enter your username: ")
        if len(
                username) >= 3:  # checks if the length of the username is not empty and is greater than or equal to 3 characters.
            return username
        else:
            print("Your username should be minimum 6 characters long!")


# gets a validated option from the user when dealing with menus.
def get_validated_option(menu_inst: Menu):
    while True:
        print()
        menu_inst.display()
        try:
            user_input = int(input("Please enter option (1-" + str(len(menu_inst.get_options())) + "): "))
            if user_input in menu_inst.get_options().keys():
                return user_input
        except BaseException:
            print("Please do not input a character.")


# manages sign in/up section for 2 players and appends them onto the dictionary.
def handle_users():
    global menu, db, users  # globalises variables as python only sess local variables as accessible here.

    # checks if a player is in the database.
    def user_exists(username: str, password: str):
        return db.value_exists("Users", "Username == {} AND Password == {}".format(repr(username), repr(password)))

    # checks if there is a username in the database.
    def username_exists(username: str):
        return db.value_exists("Users", "Username == {}".format(repr(username)))

    # registers a new account for a player.
    def register_user():
        print("\n -- Registration Form -- ")
        username = get_validated_name()

        password = get_validated_pass()

        if (not user_exists(username, password)) and (not username_exists(username)):
            db.insert_value("Users", Username=username, Password=password, Score="0")
            users[username] = 0
            print("Account created successfully! Welcome", username)
        else:
            print("You should be on login page! Redirecting you...\n")
            login_user()

    # logs a player in with the provided data.
    def login_user():
        global users
        print("\n --    Login Form    -- ")
        for i in range(3):
            username = input("Please enter your username: ")
            password = input("Please enter your password: ")

            while (username == "") or (password == ""):
                if username == "":
                    username = input("Please re-enter your username: ")
                elif password == "":
                    password = input("Please re-enter your password: ")

            if username in users.keys():  # if player 1/2 already signed in as the user.
                print("A user already logged into that account. Please try again")
            elif user_exists(username, password):
                users[username] = db.select_value("Users", "Username == {}".format(repr(username)), True, "Score")[0]
                print("Login successful! Welcome", username)
                break
            elif i + 1 == 3:  # if the loop is iterating for the last time and the user failed to sign in.
                print(
                    "You exceeded the amount of times it takes to sign in,\ntherefore you will be redirected to a signup form!")
                register_user()
            else:  # if the username or password is incorrect or does not exist in the database.
                print("Username and/or password is incorrect. Please try again.")

    # main code of handle users function.
    for i in range(2):
        menu = Menu(title="Account Management", pretty_print=True) \
            .add("Sign up").add("Sign in")
        option = get_validated_option(menu)
        {1: lambda: register_user(), 2: lambda: login_user()}[option]()


class Dice(object):
    """
    Rolls 2 dices and returns a textually generated dice face along with the points which are calculated
    according to the rules.

    :argument pip: The symbol used to traditionally denote the number of a face, arranged in a particular
                   pattern.
    """

    # when an instance is made.
    def __init__(self, pip: str = "o"):
        self.pip = pip

        # lambda expressions which are signified as the rules when rolling 2 dices.
        self.rolled_double = lambda rolls: rolls.count(rolls[0]) == len(rolls)
        self.rolled_even = lambda rolls: sum(rolls) % 2 == 0
        self.rolled_odd = lambda rolls: not self.rolled_even(rolls)

    # rolls 1 or 2 dices and returns the points gained at the end of rolling them.
    def roll(self, one_die: bool = False):
        # returns 2 dice faces designed for output.
        def roll_dices(pip, roll: int, roll2: int = None):
            can_pip = lambda condition: pip if not condition else " "
            pattern_checks = lambda r: [can_pip(r < x) for x in range(2, 5, 2)] + [can_pip(r != 6), can_pip(r % 2 == 0)]
            die_format = ["+-----+", "| {0} {1} |", "| {2}{3}{2} |", "| {1} {0} |", "+-----+"] * \
                         (2 if roll2 is not None else 1)
            die_faces = ""
            for i in range(5):
                die_faces += die_format[i].format(*(x for x in pattern_checks(roll))) + \
                             ("\t\t" + die_format[i + 5].format(
                                 *(x for x in pattern_checks(roll2))) if roll2 is not None else "") + "\n"
            return die_faces

        rolls = [randint(1, 6) for ignored in range(2 if one_die is False else 1)]
        output_face = lambda rs: print(roll_dices(self.pip, *(rs[x] for x in range(len(rs)))))

        output_face(rolls)
        points = sum(rolls)
        is_odd = False

        if not one_die:
            # calculating points for the player.
            if self.rolled_double(rolls):
                print("You get to roll an extra die since you rolled a double!")
                additional_roll = randint(1, 6)
                output_face([additional_roll])
                points += additional_roll
            elif self.rolled_odd(rolls):
                print("Oh no! The sum of your dices is an odd number!")
                points -= 5
                is_odd = True
            elif self.rolled_even(rolls):
                print("Yes! The sum of your dices is an even number so you will receive an additional 10 points!")
                points += 10

        return points, is_odd


# creates a game session between the 2 players.
def play_games():
    global users

    # Checks if a player has a higher score or both players have same score.
    def winner(player_one, player_two):
        global users
        pone_win = users[player_one] > users[player_two]
        difference = users[player_one] - users[player_two] if pone_win else users[player_two] - users[player_one]
        if difference != 0:
            print("{0} wins with {1} more points than {2}!"
                  .format(player_one if pone_win else player_two, difference, player_two if pone_win else player_one))
        return difference != 0

    print("\nLet the games begin!")
    dice = Dice()

    # The game will last 5 rounds.
    for i in range(5):
        print("\n ----   Round {}   ---- ".format(str(i + 1)))
        for username in users:
            print("\n\t\t{0}'s turn:".format(username))
            points, is_odd = dice.roll()
            difference = 0 if points == 0 else (
                (users[username] + points) if (users[username] > points) or is_odd else (points + users[username]))
            if difference >= 0:
                users[username] += points
                print("{0} gained {1} points from this round, with an overall score of {2}!"
                      .format(username, "no" if difference == 0 else str(points), users[username]))
            else:
                users[username] = 0
                print("{} could not gain points from this round; the sum of his/her dices is an odd!".format(username))

            input("Press enter to continue")

    # if both players have same score.
    if not winner(*(username for username in users)):
        print("\nBoth players have the same at the end of 5 rounds! A tie-breaker will commence!\n")
        while not winner(*(username for username in users)):  # while both players have the same score.
            for username in users:
                print("\n\t\t{0}'s turn:".format(username))
                points = dice.roll(one_die=True)[0]
                users[username] += points
                input("Press enter to continue")

            if winner(*(username for username in users)):
                break


# stores the scores of both users.
def store_scores():
    global db, users
    for username in users:
        db.update_value(repr("Users"), "Username == '{}'".format(username), Score=str(users[username]))


# Displays top 5 players with the highest score in descending order.
def display_scores():
    global db, users

    db.execute_statement_cursor("SELECT Username, Score FROM Users ORDER BY Score DESC LIMIT 5")
    top_scores = db.c.fetchall()
    print("\n\t\tTop {} Players:".format(len(top_scores)))
    for i in range(len(top_scores)):
        print("{0}. {1}  --  Score: {2}".format(str(i + 1), top_scores[i][0], top_scores[i][1]))


main()

"""
DOCUMENT CHANGES MADE AT play_games()

"""
