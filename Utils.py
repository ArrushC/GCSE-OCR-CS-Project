import sqlite3 as connector


class Util(object):
    """
    Enables developers to use manipulative functions to enhance their source code.
    """

    class Math:
        """
        Full of mathematical functions that allow developers to apply them to
        mathematical scenarios in programming.
        """
        ceil = lambda top, bottom: -(-top // bottom)
        half = lambda top: Util.Math.ceil(top, 2)

    class String:
        """
        Full of string functions that allow developers to manipulate strings
        effectively in their program.
        """
        # Divides a string into a list of chunks, containing a specific amount of characters.
        divide_string = lambda string, selection: (
            [string[loop_no * selection: (loop_no + 1) * selection].strip() for loop_no in
             range(Util.Math.ceil(len(string.strip()), selection) + 1)])


class Menu(object):
    """
    Provides a flexible, textual menu for the user, along with features that allows itself
    to be configured easily by the developer.

    :argument title: Sets the title of the menu.

    :argument width: Affects the width of the textual menu. Cannot logically be 0 or a negative integer.
                     If this argument is not passed, then this class will calculate the appropriate width
                     according to the length of the title.
    """

    # initialises variables as a new instance is made.
    def __init__(self, title: str = "", width: int = None, pretty_print: bool = False):
        self.menu_title, self.menu_width = title, (len(title) + 2 if (
            (width is None) or (width <= 0) or (width < Util.Math.half(len(self.menu_title)))) else width)
        self.options, self.content, = {}, ""
        self.is_edit, self.pretty_print = True, pretty_print
        self.ipt_msg = ""

    # sets a new title for the menu.
    def new_title(self, new_title: str):
        self.menu_title, self.menu_width = new_title, len(new_title) + 2
        self.is_edit = True

    # sets a new width for the menu.
    def new_width(self, new_width: int):
        self.menu_width = new_width if new_width >= Util.Math.half(len(self.menu_title)) else ValueError(
            "Menu width provided cannot be lesser than half of the title!")
        self.is_edit = True

    # adds an option to the list.
    def add(self, option: str, option_no: int = None):
        self.options[(option_no if option_no is not None else len(list(self.options.keys())) + 1)] = option
        self.is_edit = True
        return self

    # removes an option from the list with the specified option number.
    def remove(self, option_no: int):
        [self.options.pop(key) if key == option_no else self.options for key in list(self.options.keys())] \
            if 1 <= option_no <= len(list(self.options.keys())) else None
        self.is_edit = True
        return self

    # returns a map of options.
    def get_options(self):
        return self.options

    # displays the menu.
    def display(self):
        # returns a separator for separating the title and the options.
        def separator(end="\n"):
            return "+" + (self.menu_width * "-") + "+" + end

        def render(display_list: list, text_width: int):
            rendered, length = "", len(display_list)
            for i in range(length):
                fmt_str = "{:<{whitespace}}|"
                if i != length - 1:
                    fmt_str += "\n|" + (" " * 5)  # spaces
                rendered += fmt_str.format(display_list[i], whitespace=text_width + 1)
            return rendered

        # returns a divided string which is then formatted into a menu pattern.
        def get_divided_content(option: str, text_width: int):
            return render(Util.String.divide_string(option, text_width), text_width)

        def get_divided_pretty(option: str, text_width: int):
            lst = option.split(" ")  # splitting the words
            length = len(lst)
            display = []
            index = 0
            for i in range(length):
                prnt = ' '.join(lst[index:i + 1])
                fut = lst[i + 1] if (i + 1) != length else ""
                if len(prnt) + len(fut) >= text_width:
                    display.append(prnt)
                    index = i + 1
                elif (i + 1 == length) and (len(prnt) < text_width):
                    display.append(prnt)
            return render(display, text_width)

        def get_longest_length():
            """
            Returns a possible amount of characters depending on the quantity of options. For example, if the quantity
            of options were to be greater than 10, the display of the options after item no. 10 would ruin the menu
            display as the menu only calculated for single digits not 2 digits.
            :return: The amount of possible characters depending on the quantity of options.
            """
            return len(str(len(self.options)))

        # If changes were made to the items in the map before/after display OR if the menu is preferred to be pretty-printed.
        if self.is_edit or self.pretty_print:
            text_width = self.menu_width - (5 + get_longest_length())
            self.content = separator() + "| {:^{display_width}} |".format(self.menu_title,
                                                                          display_width=self.menu_width - 2) + "\n" + separator()

            for (item_no, item) in self.options.items():
                item_length = len(item)  # the amount of characters in an option.
                self.content += "| (" + str(item_no) + ") "

                if item_length > text_width:
                    """
                    What this section does is that when the length of an option is greater than
                    the available text width of the menu, It will split after every x characters
                    where x is the available text width (i.e. If an option is 27 characters long 
                    and the available text width is 14 characters, the option will split into 2 
                    sections where each string contains 14 characters.
                    """
                    if self.pretty_print:
                        self.content += get_divided_pretty(item, text_width) + "\n"
                    else:
                        self.content += get_divided_content(item, text_width) + "\n"
                else:
                    self.content += item.strip() + (" " * (text_width - item_length + 1)) + "|\n"
            self.content += separator()
            print(self.content)
            self.is_edit = False
        else:
            """
            To improve memory usage, another variable is made: is_edit. The sole purpose of this variable is to
            signify if a change has been made to the values of the option map. If there was a change made, then
            the value of content variable will change to give an updated view of the menu. Else, the content
            value will be simply printed.
            """
            print(self.content)


class SQLManager:
    """
    Provides a coherently sustained connection with the sql database, providing functions that
    allow the data values or the database to be used entierly.

    :argument url: The location of the database.
    """

    # sqlite statements that will be used and modified accordingly.
    TABLE_CREATE = "CREATE TABLE IF NOT EXISTS {} ({})"
    VALUE_INSERT = "INSERT INTO {} ({}) VALUES ({})"
    VALUE_UPDATE = "UPDATE {} SET {} WHERE {}"
    VALUE_SELECT = "SELECT {} FROM {}"
    VALUE_SELECT_EXISTS = "SELECT EXISTS(SELECT 1 FROM {} WHERE {})"

    # initialises variables as an instance is made.
    def __init__(self, url):
        self.db = connector.connect(url)
        self.c = self.db.cursor()
        self.toFormat = ""

    # converts an array into string.
    def ats(self, array, quotation_marks=False):
        string = str([list(array)[i] for i in range(len(list(array)))]) \
            .replace("[", "").replace("]", "")
        return string.replace("\"", "").replace("\'", "") if not quotation_marks else string

    # converts an array into string except with the modification that '=' wil be appended between both values..
    def dts(self, data):
        return ''.join([field + " = " + value + ("," if i+1 != len(data.items()) else "") for i, (field, value) in enumerate(data.items())])

    # closes the connection of the database.
    def close(self):
        self.db.close()

    # executes an sql statement from the database variable.
    def execute_statement(self, sql):
        self.db.execute(sql)
        self.db.commit()

    # executes an sql statement from the cursor.
    def execute_statement_cursor(self, sql):
        self.c.execute(sql)

    # creates a table
    def create_table(self, tblName, *fields):
        self.toFormat = self.TABLE_CREATE
        self.execute_statement_cursor(self.toFormat.format(tblName, self.ats(fields)))

    # inserts a value into the table.
    def insert_value(self, tblName, **fav):
        self.toFormat = self.VALUE_INSERT.format(tblName, self.ats(fav.keys(), False), self.ats(fav.values(), True))
        self.execute_statement(self.toFormat)

    # updates a value from a field in the table.
    def update_value(self, tblName, condition, **fav):
        self.toFormat = self.VALUE_UPDATE + ("WHERE {}" if condition != "" else "")
        self.execute_statement(self.VALUE_UPDATE.format(tblName, self.dts(fav), condition))

    # selects a value(s) from the table.
    def select_value(self, tblName, condition="", one_record=False, *fields):
        self.toFormat = self.VALUE_SELECT
        self.toFormat = self.toFormat.format(
            self.ats(fields) if ((fields is not None) and (self.ats(fields) != "")) else "*", tblName, condition)
        self.execute_statement_cursor(self.toFormat)
        if one_record:
            return self.c.fetchone()
        else:
            return self.c.fetchall()

    # checks if a value exists in the table.
    def value_exists(self, tblName, condition):
        self.toFormat = self.VALUE_SELECT_EXISTS.format(tblName, condition)
        self.execute_statement_cursor(self.toFormat)
        return self.c.fetchone()[0] == 1
