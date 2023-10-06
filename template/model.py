'''
    Our Model class
    This should control the actual "logic" of your website
    And nicely abstracts away the program logic from your page loading
    It should exist as a separate layer to any database or data structure that you might be using
    Nothing here should be stateful, if it's stateful let the database handle it
'''
from base64 import b64encode, b64decode
from datetime import time

import view
import random
import sql
from bottle import response, request
import rsa

# Initialise our views, all arguments are defaults for the template
page_view = view.View()


# -----------------------------------------------------------------------------
# Index
# -----------------------------------------------------------------------------

def index():
    '''
        index
        Returns the view for the index
    '''
    if "visit" in list(request.cookies.keys()):
        # friend_names = sql.SQLDatabase("user_database.db").find_friend(request.get_cookie("visit"))
        # friend_list = '/n'.join(list(friend_names))
        if "admin" in list(request.cookies.keys()):
            return page_view("admin_index", admin=1, username=request.get_cookie("visit"))
        return page_view("login_index", username=request.get_cookie("visit"))
    return page_view("index")


# -----------------------------------------------------------------------------
# Login
# -----------------------------------------------------------------------------

def login_form():
    '''
        login_form
        Returns the view for the login_form
    '''
    return page_view("login")


# -----------------------------------------------------------------------------

# Check the login credentials
def login_check(username, password):
    '''
        login_check
        Checks usernames and passwords

        :: username :: The username
        :: password :: The password

        Returns either a view for valid credentials, or a view for invalid credentials
    '''

    # By default assume good creds
    login = True
    find_name = sql.SQLDatabase("user_database.db").check_login_username(username)  # Wrong Username
    find_admin = sql.SQLDatabase("user_database.db").check_admin(username)
    if not find_name:
        login = False
    else:
        find_pw = sql.SQLDatabase("user_database.db").check_credentials(username, password)
        if not find_pw:
            login = False

    if login:
        if find_admin:
            response.set_cookie("admin", username)
        response.set_cookie(username, username)
        response.set_cookie("visit", username)
        return page_view("valid", username=request.get_cookie("visit"), name=username)
    else:
        return page_view("invalid", reason="Incorrect Username or Password")


# -----------------------------------------------------------------------------
# Signup
# -----------------------------------------------------------------------------

def signup_form():
    '''
        signup_form
        Returns the view for the signup_form
    '''
    return page_view("signup")


# -----------------------------------------------------------------------------

# Check the login credentials
def signup_check(username, password):
    '''
        signup_check
        Checks usernames and passwords

        :: username :: The username
        :: password :: The password

        Returns either a view for valid credentials, or a view for invalid credentials
    '''

    # By default assume good creds
    signup = True
    user_add_data = sql.SQLDatabase("user_database.db")
    find_name = user_add_data.check_login_username(username)  # Wrong Username
    if find_name:
        signup = False
    else:
        salt = sql.random_salt()
        pw = sql.hash_password(salt, password)
        user_add_data.add_user(username, salt, pw, 0)

    if signup:
        response.set_cookie(username, username)
        response.set_cookie("visit", username)
        key_name = username
        (public, private) = rsa.newkeys(512)
        with open("{}_public.pem".format(key_name), "wb") as f:
            f.write(public._save_pkcs1_pem())

        with open("{}_private.pem".format(key_name), "wb") as f:
            f.write(private._save_pkcs1_pem())

        return page_view("valid", username=request.get_cookie("visit"), name=username)
    else:
        return page_view("invalid", reason="Username already exists!")


# -----------------------------------------------------------------------------
# Sign out
# -----------------------------------------------------------------------------

def signout_form():
    cookie_now = request.get_cookie("visit")
    print(cookie_now)
    response.delete_cookie(cookie_now)
    response.delete_cookie("visit")
    return page_view("index")


# -----------------------------------------------------------------------------
# Change Password
# -----------------------------------------------------------------------------
def changePw_form():
    return page_view("changePW", username=request.get_cookie("visit"))


def newPw_check(newPw):
    user_add_data = sql.SQLDatabase("user_database.db")
    username = request.get_cookie("visit")
    salt = sql.random_salt()
    pw = sql.hash_password(salt, newPw)
    user_add_data.change_user_password(username, pw, salt)
    return page_view("valid", username=request.get_cookie("visit"), name=username)


# -----------------------------------------------------------------------------
# Rename
# -----------------------------------------------------------------------------
def rename_form():
    return page_view("rename", username=request.get_cookie("visit"))


def check_rename_post(newname):

    re = True
    user_add_data = sql.SQLDatabase("user_database.db")
    find_name = user_add_data.check_login_username(newname)  # Wrong Username
    if find_name:
        re = False
    key = request.get_cookie("visit")
    if re:
        response.set_cookie(newname, newname)
        response.set_cookie("visit", newname)
        user_add_data.change_username(newname, key)
        return page_view("valid", username=request.get_cookie("visit"), name=newname)
    else:
        # response.set_cookie(key, key)
        # response.set_cookie("visit", key)
        return page_view("invalid", username=request.get_cookie("visit"), reason=" New username already exists!")

# -----------------------------------------------------------------------------
# Add Friend
# -----------------------------------------------------------------------------


def friendList_form():
    username = request.get_cookie("visit")
    friend_names = sql.SQLDatabase("user_database.db").find_friend(username)
    if "," in friend_names:
        friends = friend_names.split(",")
    else:
        friends = [friend_names]
    return page_view("friendList", username=request.get_cookie("visit"), units=friends)


def addFriend_form():
    username = request.get_cookie("visit")
    friend_names = sql.SQLDatabase("user_database.db").find_friend(username)
    if "," in friend_names:
        friends = friend_names.split(",")
    else:
        friends = [friend_names]
    return page_view("addFriend", username=request.get_cookie("visit"), units=friends)


# -----------------------------------------------------------------------------
# Remove Friend
# -----------------------------------------------------------------------------
def removeFriend_form():
    username = request.get_cookie("visit")
    friend_names = sql.SQLDatabase("user_database.db").find_friend(username)
    if "," in friend_names:
        friends = friend_names.split(",")
    else:
        friends = [friend_names]
    return page_view("removeFriend", username=username, units=friends)


def removeFriend(friend):
    friendD = True
    username = request.get_cookie("visit")
    friend_add_data = sql.SQLDatabase("user_database.db")
    find_name = friend_add_data.check_friendName(username, friend)
    if find_name == True:

        friend_add_data.remove_friend(username, friend)
        return page_view("addFriend_valid", username=request.get_cookie("visit"), result="remove")
    else:
        return page_view("addFriend_invalid", username=request.get_cookie("visit"),
                         reason="Friend name not exists for this user!")


def friend_check(friend):
    friendAdd = True
    username = request.get_cookie("visit")
    friend_add_data = sql.SQLDatabase("user_database.db")
    find_friend_name = friend_add_data.check_login_username(friend)
    if find_friend_name:
        find_name = friend_add_data.check_friendName(username, friend)  # Wrong Username

        if find_name == True:
            friendAdd = False
        elif find_name == False:
            return page_view("addFriend_invalid", username=request.get_cookie("visit"),
                             reason="Friend name does not exist!")
        else:
            if "," in find_name:
                friend_add_data.modify_friend(username, find_name)
                friend_add_data.add_friend(friend, username)
            else:
                friend_add_data.add_friend(username, find_name)
                friend_add_data.add_friend(friend, username)

        if friendAdd:
            return page_view("addFriend_valid", username=request.get_cookie("visit"), result="add")
        else:
            return page_view("addFriend_invalid", username=request.get_cookie("visit"),
                             reason="Friend name already exists for this user!")
    else:
        return page_view("addFriend_invalid", username=request.get_cookie("visit"),
                         reason="Friend name does not exist!")


# -----------------------------------------------------------------------------
# Message
# -----------------------------------------------------------------------------
def inbox_form():
    me = request.get_cookie("visit")


    friend_names = sql.SQLDatabase("user_database.db").find_friend(request.get_cookie("visit"))
    if "," in friend_names:
        friend_name = friend_names.split(",")
    else:
        friend_name = [friend_names]

    message_en = sql.SQLDatabase("user_database.db").find_me(me)
    mess_en = []
    private = rsa.PrivateKey._load_pkcs1_pem(open("{}_private.pem".format(me), 'rb').read())
    senders = []
    for mess in message_en:
        message_en = b64decode(mess[1].encode())
        decrypted = rsa.decrypt(message_en, private)
        mess_en.append(bytes.decode(decrypted))
        senders.append(mess[0])

    if len(friend_name) != 0 and len(mess_en) != 0:
        print(mess_en)
        return page_view("Inbox", username=request.get_cookie("visit"), sender=senders,
                         cont=mess_en)
    else:
        return page_view("Inbox", username=request.get_cookie("visit"), sender=["None"],
                         cont=["None"])

# -----------------------------------------------------------------------------
# Send
# -----------------------------------------------------------------------------


def send_form():
    friend_names = sql.SQLDatabase("user_database.db").find_friend(request.get_cookie("visit"))
    if "," in friend_names:
        friends = friend_names.split(",")
    else:
        friends = [friend_names]

    if friend_names != "None":
        return page_view("Send", username=request.get_cookie("visit"), units=friends)
    else:
        return page_view("send_error", username=request.get_cookie("visit"), reason="Please add friend firstly!")


def alreadySent_form():
    me = request.get_cookie("visit")

    friend_names = sql.SQLDatabase("user_database.db").find_friend(request.get_cookie("visit"))
    if "," in friend_names:
        friend_name = friend_names.split(",")
    else:
        friend_name = [friend_names]

    message_en = sql.SQLDatabase("user_database.db").find_other(me)
    mess_en = []
    private = rsa.PrivateKey._load_pkcs1_pem(open("{}_private.pem".format(me), 'rb').read())
    senders = []
    for mess in message_en:
        message_en = b64decode(mess[1].encode())
        decrypted = rsa.decrypt(message_en, private)
        mess_en.append(bytes.decode(decrypted))
        senders.append(mess[0])
    print(request.cookies.keys())

    if len(friend_name) != 0 and len(mess_en) != 0:
        print(mess_en)
        return page_view("alreadySent", username=request.get_cookie("visit"), sender=senders,
                         cont=mess_en)
    else:
        return page_view("alreadySent", username=request.get_cookie("visit"), sender=["None"],
                         cont=["None"])


def message_send(message, friend):
    friend_names = sql.SQLDatabase("user_database.db").find_friend(request.get_cookie("visit"))
    if "," in friend_names:
        friends = friend_names.split(",")
    else:
        friends = [friend_names.strip()]
    if friend not in friends:
        return page_view("send_error", username=request.get_cookie("visit"), reason="Friend name is not exist!")
    receiver = friend
    sender = request.get_cookie("visit")

    public_me = rsa.PublicKey._load_pkcs1_pem(open("{}_public.pem".format(sender), 'rb').read())

    public = rsa.PublicKey._load_pkcs1_pem(open("{}_public.pem".format(receiver), "rb").read())
    encrypted = rsa.encrypt(bytes(message, "utf-8"), public)
    encrypted_me = rsa.encrypt(bytes(message, "utf-8"), public_me)

    encrypted = b64encode(encrypted).decode()
    encrypted_me = b64encode(encrypted_me).decode()
    user_add_message = sql.SQLDatabase("user_database.db")
    user_add_message.add_communication_details(sender, receiver, encrypted)
    user_add_message.add_communication_self_details(sender, receiver, encrypted_me)
    return page_view("send_valid", username=request.get_cookie("visit"), mes="Message")


def message_receive():
    sender = list(sql.SQLDatabase("user_database.db").find_friend(request.get_cookie("visit")))[0]
    me = request.get_cookie("visit")
    message_en = sql.SQLDatabase("user_database.db").find_me(me)[0]

    private = rsa.PrivateKey._load_pkcs1_pem(open("{}_private.pem".format(me), 'rb').read())
    message_en = b64decode(message_en.encode())
    decrypted = rsa.decrypt(message_en, private)

    friend_names = sql.SQLDatabase("user_database.db").find_friend(request.get_cookie("visit"))
    return page_view("message", username=request.get_cookie("visit"), friend=friend_names[0], receive=decrypted,
                     receiver=sender)


# -----------------------------------------------------------------------------
# Post
# -----------------------------------------------------------------------------

def post_form():
    if "admin" in list(request.cookies.keys()):
        return page_view("Post", admin=1, username=request.get_cookie("visit"))
    return page_view("Post", username=request.get_cookie("visit"))


def post_send(title, content):
    sender = request.get_cookie("visit")

    public_me = rsa.PublicKey._load_pkcs1_pem(open("{}_public.pem".format(sender), 'rb').read())

    encrypted_title = rsa.encrypt(bytes(title, "utf-8"), public_me)
    encrypted_content = rsa.encrypt(bytes(content, "utf-8"), public_me)

    encrypted_title = b64encode(encrypted_title).decode()
    encrypted_content = b64encode(encrypted_content).decode()
    user_add_message = sql.SQLDatabase("user_database.db")
    user_add_message.add_post_info(encrypted_content, encrypted_title, sender)

    return page_view("send_valid", username=request.get_cookie("visit"), mes="Post discussion")


def postSearch_form():
    names = []
    titles_en = []
    contents_en = []
    id = []
    message_en = sql.SQLDatabase("user_database.db").all_post()
    for message in message_en:
        id.append(message[3])
        names.append(message[2])
        titles_en.append(message[1])
        contents_en.append(message[0])

    title = []
    content = []
    i = 0
    while i < len(names):
        private = rsa.PrivateKey._load_pkcs1_pem(open("{}_private.pem".format(names[i]), 'rb').read())
        title_en = b64decode(titles_en[i].encode())
        title_decrypted = rsa.decrypt(title_en, private)
        title.append(bytes.decode(title_decrypted))

        content_en = b64decode(contents_en[i].encode())
        content_decrypted = rsa.decrypt(content_en, private)
        content.append(bytes.decode(content_decrypted))

        i += 1

    if len(names) != 0:
        if "admin" in list(request.cookies.keys()):
            return page_view("postSearch", admin=1, username=request.get_cookie("visit"), sender=names,
                             cont=content, title=title, id=id)
        return page_view("postSearch", username=request.get_cookie("visit"), sender=names,
                         cont=content, title=title, id=id)
    else:
        if "admin" in list(request.cookies.keys()):
            return page_view("postSearch", admin=1, username=request.get_cookie("visit"), sender=["None"],
                             cont=["None"], title=["None"], id=0)
        return page_view("postSearch", username=request.get_cookie("visit"), sender=["None"],
                         cont=["None"], title=["None"], id=0)


# -----------------------------------------------------------------------------
# Delete Post
# -----------------------------------------------------------------------------
def DeletePost_form():
    return page_view("DeletePost", admin=1)


def check_DeletePost_post(post_id):
    sql.SQLDatabase("user_database.db").delete_certain_rank(post_id)
    return page_view("success", admin=1, result="Delete Successful!!")


# -----------------------------------------------------------------------------
# Delete User
# -----------------------------------------------------------------------------
def allUser_form():
    user_name = sql.SQLDatabase("user_database.db").find_allUser()
    allUsers = []
    for u in user_name:
        allUsers.append(u[0])
    return page_view("UserList", username=1, units=allUsers)


def DeleteUser_form():
    user_name = sql.SQLDatabase("user_database.db").find_allUser()
    allUsers = []
    for u in user_name:
        allUsers.append(u[0])
    return page_view("DeleteUser", admin=1, units=allUsers)


def check_DeleteUser_post(user_name):
    friend_add_data = sql.SQLDatabase("user_database.db")
    find_name = friend_add_data.check_deleteUser(user_name)

    if find_name == True:
        friend_add_data.remove_user(user_name)
        return page_view("success", username=1, result="User name exists! Deleted successfully!")
    else:
        return page_view("addFriend_invalid", username=1,
                         reason="User name not exists! Try again!")


def helpUser_form():
    user_help = sql.SQLDatabase("user_database.db").find_allhelp()
    if user_help == "None":
        return page_view("AllHelp", username=1, sender=["None"], cont=["None"])
    allUsername = []
    allHelp = []
    for u in user_help:
        allUsername.append(u[0])
        allHelp.append(u[1])
    return page_view("AllHelp", username=1, sender=allUsername, cont=allHelp)


def help_form():
    return page_view("help", username=request.get_cookie("visit"))


def help_post(help_msg):
    username = request.get_cookie("visit")
    sql.SQLDatabase("user_database.db").add_help(username, help_msg)
    return page_view("success", username=username, result="Your question has been communicated to the administrator! Thanks for the feedback!")
# -----------------------------------------------------------------------------
# About
# -----------------------------------------------------------------------------

def about():
    '''
        about
        Returns the view for the about page
    '''
    return page_view("about", garble=about_garble())


# Returns a random string each time
def about_garble():
    '''
        about_garble
        Returns one of several strings for the about page
    '''
    garble = ["leverage agile frameworks to provide a robust synopsis for high level overviews.",
              "iterate approaches to corporate strategy and foster collaborative thinking to further the overall value proposition.",
              "organically grow the holistic world view of disruptive innovation via workplace change management and empowerment.",
              "bring to the table win-win survival strategies to ensure proactive and progressive competitive domination.",
              "ensure the end of the day advancement, a new normal that has evolved from epistemic management approaches and is on the runway towards a streamlined cloud solution.",
              "provide user generated content in real-time will have multiple touchpoints for offshoring."]
    return garble[random.randint(0, len(garble) - 1)]


# Returns a random string each time
def about_garble():
    '''
        about_garble
        Returns one of several strings for the about page
    '''
    garble = ["leverage agile frameworks to provide a robust synopsis for high level overviews.",
              "iterate approaches to corporate strategy and foster collaborative thinking to further the overall value proposition.",
              "organically grow the holistic world view of disruptive innovation via workplace change management and empowerment.",
              "bring to the table win-win survival strategies to ensure proactive and progressive competitive domination.",
              "ensure the end of the day advancement, a new normal that has evolved from epistemic management approaches and is on the runway towards a streamlined cloud solution.",
              "provide user generated content in real-time will have multiple touchpoints for offshoring."]
    return garble[random.randint(0, len(garble) - 1)]



# -----------------------------------------------------------------------------
# Debug
# -----------------------------------------------------------------------------

def debug(cmd):
    try:
        return str(eval(cmd))
    except:
        pass


# -----------------------------------------------------------------------------
# 404
# Custom 404 error page
# -----------------------------------------------------------------------------

def handle_errors(error):
    error_type = error.status_line
    error_msg = error.body
    return page_view("error", error_type=error_type, error_msg=error_msg)
