import sqlite3
from Crypto.Hash import SHA256
import random


# This class is a simple handler for all of our SQL database actions
# Practicing a good separation of concerns, we should only ever call 
# These functions from our models

# If you notice anything out of place here, consider it to your advantage and don't spoil the surprise

def random_salt():
    s = ''
    symbols = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789!@#$%^&*'
    length = len(symbols) - 1

    for i in range(256):
        s += symbols[random.randint(0, length)]
    return s


def hash_password(salt, password):
    hashed_pwd = SHA256.new((password + salt).encode()).hexdigest()
    return hashed_pwd


class SQLDatabase():
    '''
        Our SQL Database

    '''

    # Get the database running
    def __init__(self, database_arg=":memory:"):
        self.conn = sqlite3.connect(database_arg)
        self.cur = self.conn.cursor()

    # SQLite 3 does not natively support multiple commands in a single statement
    # Using this handler restores this functionality
    # This only returns the output of the last command
    def execute(self, sql_string):
        out = None
        for string in sql_string.split(";"):
            try:
                out = self.cur.execute(string)
            except:
                pass
        return out

    # Commit changes to the database
    def commit(self):
        self.conn.commit()

    # -----------------------------------------------------------------------------

    # Sets up the database
    # Default admin password
    def database_setup(self):
        self.user_database_setup()
        self.friend_list_database_setup()
        self.communication_database_setup()
        self.communication_self_database_setup()
        self.post_database_setup()
        self.help_database_setup()

    def user_database_setup(self):

        # Clear the database if needed
        self.execute("DROP TABLE IF EXISTS Users")
        self.commit()

        # Create the users table
        self.execute("""CREATE TABLE Users(
            username TEXT PRIMARY KEY,
            salt CHAR(256),
            password TEXT,
            admin INTEGER DEFAULT 0
        )""")

        self.commit()

        # Add our admin user
        salt = random_salt()
        admin_password = hash_password(salt, '88888888')
        self.add_user('admin', salt, admin_password, admin=1)

    def friend_list_database_setup(self):

        # Clear the database if needed
        self.execute("DROP TABLE IF EXISTS FriendList")
        self.commit()

        # Create the users table
        self.execute("""CREATE TABLE FriendList(
               username TEXT PRIMARY KEY REFERENCES Users(username),
               friend_name TEXT REFERENCES Users(username)
           )""")

        self.commit()

    def help_database_setup(self):
        # Clear the database if needed
        self.execute("DROP TABLE IF EXISTS HelpList")
        self.commit()

        # Create the users table
        self.execute("""CREATE TABLE HelpList(
               username TEXT PRIMARY KEY REFERENCES Users(username),
               help TEXT
           )""")

        self.commit()

        # self.add_friend('admin', '111')

    def post_database_setup(self):

        # Clear the database if needed
        self.execute("DROP TABLE IF EXISTS Post")
        self.commit()

        # Create the users table
        self.execute("""CREATE TABLE Post(
            content TEXT,
            title TEXT,
            sender TEXT,
            rank INTEGER
        );

        """)

        self.commit()

    def add_help(self, sender, help_msg):
        sql_cmd = """
                        INSERT INTO HelpList
                        VALUES( '{sender}', '{help}');
                    """

        sql_cmd = sql_cmd.format(sender=sender, help=help_msg)

        self.execute(sql_cmd)
        self.commit()
        return True

    def find_allhelp(self):
        sql_query = """
                                select *
                                from HelpList 
                        """
        self.execute(sql_query)
        self.commit()
        results = self.cur.fetchall()
        if results is not None:
            return results
        else:
            return "None"


    def add_post_info(self, post_msg, title, sender):
        sql_cmd = """
                INSERT INTO Post (content, title, sender, rank) 
                SELECT '{post_msg}', '{title}', '{sender}', IFNULL(MAX(rank), 0) + 1
                FROM Post;
            """

        sql_cmd = sql_cmd.format(post_msg=post_msg, title=title, sender=sender)

        self.execute(sql_cmd)
        self.commit()
        return True

    def all_post(self):
        sql_cmd = """
                           SELECT *
                           FROM Post
                       """
        self.execute(sql_cmd)
        self.commit()
        fetch = self.cur.fetchall()
        return fetch

    def delete_certain_rank(self, rank):
        sql_cmd = """
                        DELETE FROM Post
                        WHERE rank = '{rank}';
                    """

        sql_cmd = sql_cmd.format(rank=rank)

        self.execute(sql_cmd)
        self.commit()
        return True

    def add_friend(self, username, friends):
        sql_cmd = """
                INSERT INTO FriendList
                VALUES('{username}','{friends}');
            """
        sql_cmd = sql_cmd.format(username=username, friends=friends)
        self.execute(sql_cmd)
        self.commit()
        return True

    def remove_friend(self, username, friend_name):
        sql_query = """
                        select *
                        from FriendList
                        where username = '{username}'
                """
        sql_query = sql_query.format(username=username)
        self.execute(sql_query)
        fetch = self.cur.fetchone()[1]
        if "," in fetch:
            fs = fetch.split(",")
            fs.remove(friend_name)
            new_fs = ",".join(fs)
            sql_cmd_1 = """
                            UPDATE FriendList SET friend_name = '{new_friend}' WHERE username = '{username}'
                            """

            sql_cmd = sql_cmd_1.format(new_friend=new_fs, username=username)
            self.execute(sql_cmd)
            self.commit()
        else:
            sql_cmd_2 = """
                            DELETE FROM FriendList WHERE username = '{username}';
                            """
            sql_cmd = sql_cmd_2.format(friend_name=friend_name, username=username)

            self.execute(sql_cmd)
            self.commit()

        return True

    def communication_database_setup(self):
        # Clear the database if needed

        self.execute("DROP TABLE IF EXISTS Communication")
        self.commit()

        # Create the users table
        self.execute("""CREATE TABLE Communication(
               sender TEXT,
               receiver CHAR,
               encrypted_message BLOB
           )""")

        self.commit()
        return True

    def communication_self_database_setup(self):
        # Clear the database if needed

        self.execute("DROP TABLE IF EXISTS CommunicationSelf")
        self.commit()

        # Create the users table
        self.execute("""CREATE TABLE CommunicationSelf(
               sender TEXT,
               receiver CHAR,
               encrypted_message BLOB
           )""")

        self.commit()
        return True

    def add_communication_details(self, sender, receiver, message):
        sql_cmd = """INSERT INTO Communication
                VALUES('{sender}','{receiver}',"{message}");
            """
        print(type(message))
        sql_cmd = sql_cmd.format(sender=sender, receiver=receiver, message=message)

        self.execute(sql_cmd)
        self.commit()
        return True

    def add_communication_self_details(self, sender, receiver, message):
        sql_cmd = """INSERT INTO CommunicationSelf
                VALUES('{sender}','{receiver}',"{message}");
            """

        sql_cmd = sql_cmd.format(sender=sender, receiver=receiver, message=message)

        self.execute(sql_cmd)
        self.commit()
        return True
        # Check login username

    def check_friendName(self, username, friend):
        sql_query = """
                select *
                from FriendList
                where username = '{username}'
        """
        sql_query = sql_query.format(username=username)
        self.execute(sql_query)
        # self.commit()
        # print(self.cur.fetchone())
        fetch = self.cur.fetchone()
        if fetch is not None:
            if "," not in fetch[1]:
                if " " in fetch[1]:
                    friends = fetch[1].split(" ")
                    friends.remove("")
                else:
                    friends = [fetch[1]]
            else:
                friends = fetch[1].split(",")
            if friend in friends:
                return True
            else:
                if self.check_login_username(friend):
                    friends.append(friend)
                    return ",".join(friends)
                else:
                    return False
        else:
            return friend + " "

    def modify_friend(self, username, friend):
        sql_cmd = """
                        UPDATE FriendList SET friend_name = '{new_friend}' WHERE username = '{username}'
                        """

        sql_cmd = sql_cmd.format(new_friend=friend, username=username)

        self.execute(sql_cmd)
        self.commit()
        return True

    def find_friend(self, curr_username):
        sql_query = """
                        select *
                        from FriendList 
                        where username = '{curr_username}'
                """
        sql_query = sql_query.format(curr_username=curr_username)
        self.execute(sql_query)
        self.commit()
        results = self.cur.fetchone()
        if results is not None:
            return results[1]
        else:
            return "None"

    def find_me(self, sender):
        sql_query = """
                        select sender, encrypted_message
                        from Communication
                        where receiver = '{sender}'
                """
        sql_query = sql_query.format(sender=sender)
        self.execute(sql_query)
        self.commit()

        results = self.cur.fetchall()
        return results

    def find_other(self, sender):
        sql_query = """
                        select receiver, encrypted_message
                        from CommunicationSelf
                        where sender = '{sender}'
                """
        sql_query = sql_query.format(sender=sender)
        self.execute(sql_query)
        self.commit()

        results = self.cur.fetchall()
        return results

    # -----------------------------------------------------------------------------
    # User handling
    # -----------------------------------------------------------------------------

    # Add a user to the database
    def add_user(self, username, salt, password, admin=0):
        sql_cmd = """
                INSERT INTO Users
                VALUES('{username}','{salt}', '{password}', {admin});
            """

        sql_cmd = sql_cmd.format(username=username, salt=salt, password=password, admin=admin)

        self.execute(sql_cmd)
        self.commit()
        return True

    # -----------------------------------------------------------------------------
    def change_username(self, new_username, old_username):
        sql_cmd = """
                    UPDATE Users SET username = '{new_username}' WHERE username = '{old_username}'
                    """

        sql_cmd = sql_cmd.format(new_username=new_username, old_username=old_username)

        self.execute(sql_cmd)
        self.commit()
        return True

    def change_user_password(self, username, new_password, new_salt):
        sql_cmd = """
                    UPDATE Users SET password = '{new_password}', salt = '{new_salt}' WHERE username = '{username}'
                    """

        sql_cmd = sql_cmd.format(new_password=new_password, new_salt=new_salt, username=username)

        self.execute(sql_cmd)
        self.commit()
        return True

    # Check login credentials
    def check_credentials(self, username, password):
        sql_query = """
                SELECT salt 
                FROM Users
                WHERE username = '{username}' 
            """

        sql_query = sql_query.format(username=username, password=password)

        self.execute(sql_query)
        salt_db = self.cur.fetchone()

        ex_pw = hash_password(salt_db[0], password)

        sql_query_2 = """
                        SELECT * 
                        FROM Users
                        WHERE username = '{username}' AND password = '{password}'
                    """
        sql_query_2 = sql_query_2.format(username=username, password=ex_pw)

        self.execute(sql_query_2)
        # If our query returns
        if self.cur.fetchone():
            return True
        else:
            return False

    # Check login username
    def check_login_username(self, username):
        sql_query = """
                select username
                from Users
                where username = '{username}'
        """
        sql_query = sql_query.format(username=username)
        self.execute(sql_query)
        self.commit()

        if self.cur.fetchone():
            return True
        else:
            return False

    def find_allUser(self):
        sql_query = """
                        select username
                        from Users
                        where admin = 0
                """
        self.execute(sql_query)
        self.commit()

        results = self.cur.fetchall()
        return results

    def check_admin(self, username):
        sql_query = """
                select username
                from Users
                where admin = 1
        """
        sql_query = sql_query.format(username=username)
        self.execute(sql_query)
        self.commit()

        if self.cur.fetchone() == username:
            return True
        else:
            return False

    def check_deleteUser(self, user_name):
        sql_query = """
                        select username
                        from Users
                        where username = '{username}'
                """
        sql_query = sql_query.format(username=user_name)
        self.execute(sql_query)
        self.commit()

        if self.cur.fetchone():
            return True
        else:
            return False

    def remove_user(self, user_name):
        sql_cmd = """
                            DELETE FROM Users WHERE username = '{old_username}'
                            """

        sql_cmd = sql_cmd.format(old_username=user_name)

        self.execute(sql_cmd)
        self.commit()
        return True
