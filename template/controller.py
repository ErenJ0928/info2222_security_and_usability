'''
    This file will handle our typical Bottle requests and responses 
    You should not have anything beyond basic page loads, handling forms and 
    maybe some simple program logic
'''
from datetime import time

from bottle import route, get, post, error, request, static_file, response, template

import model


#-----------------------------------------------------------------------------
# Static file paths
#-----------------------------------------------------------------------------

# Allow image loading
@route('/img/<picture:path>')
def serve_pictures(picture):
    '''
        serve_pictures

        Serves images from static/img/

        :: picture :: A path to the requested picture

        Returns a static file object containing the requested picture
    '''
    return static_file(picture, root='static/img/')

#-----------------------------------------------------------------------------

# Allow CSS
@route('/css/<css:path>')
def serve_css(css):
    '''
        serve_css

        Serves css from static/css/

        :: css :: A path to the requested css

        Returns a static file object containing the requested css
    '''
    return static_file(css, root='static/css/')

#-----------------------------------------------------------------------------

# Allow javascript
@route('/js/<js:path>')
def serve_js(js):
    '''
        serve_js

        Serves js from static/js/

        :: js :: A path to the requested javascript

        Returns a static file object containing the requested javascript
    '''
    return static_file(js, root='static/js/')

#-----------------------------------------------------------------------------
# Pages
#-----------------------------------------------------------------------------

# Redirect to login
@get('/')
@get('/home')
def get_index():
    '''
        get_index
        
        Serves the index page
    '''
    return model.index()

#-----------------------------------------------------------------------------

# Display the login page
@get('/login')
def get_login_controller():
    '''
        get_login
        
        Serves the login page
    '''

    return model.login_form()

#-----------------------------------------------------------------------------

# Attempt the login
@post('/login')
def post_login():
    '''
        post_login
        
        Handles login attempts
        Expects a form containing 'username' and 'password' fields
    '''


    # Handle the form processing
    username = request.forms.get('username')
    password = request.forms.get('password')

    # Call the appropriate method
    return model.login_check(username, password)


# Display the signup page
@get('/signup')
def get_signup_controller():
    '''
        get_signup

        Serves the signup page
    '''
    return model.signup_form()


# -----------------------------------------------------------------------------

# Attempt the signup
@post('/signup')
def post_signup():
    '''
        post_signup

        Handles signup attempts
        Expects a form containing 'username' and 'password' fields
    '''

    # Handle the form processing
    username = request.forms.get('username')
    password = request.forms.get('password')

    # Call the appropriate method
    return model.signup_check(username, password)


#-----------------------------------------------------------------------------
# Display the signout page
@get('/signOut')
def get_signup_controller():
    '''
        get_signup

        Serves the signup page
    '''
    return model.signout_form()

# -----------------------------------------------------------------------------

# Display the add friend page
@get('/addFriend')
def get_addFriend_controller():
    '''
        get_addFriend

        Serves the addFriend page
    '''
    return model.addFriend_form()


# -----------------------------------------------------------------------------

# Attempt the signup
@post('/addFriend')
def post_addFriend():
    '''
        post_addFriend

        Handles addFriend attempts
        Expects a form containing 'friend' fields
    '''

    # Handle the form processing
    friend = request.forms.get('friend')

    # Call the appropriate method
    return model.friend_check(friend)

# -----------------------------------------------------------------------------

@get('/removeFriend')
def get_removeFriend_controller():

    return model.removeFriend_form()


# -----------------------------------------------------------------------------

# Attempt the signup
@post('/removeFriend')
def post_removeFriend():
    '''
        post_addFriend

        Handles addFriend attempts
        Expects a form containing 'friend' fields
    '''

    # Handle the form processing
    friend = request.forms.get('friend')

    # Call the appropriate method
    return model.removeFriend(friend)

# Display the add friend page
@get('/changePw')
def get_changePw_controller():

    return model.changePw_form()


# -----------------------------------------------------------------------------

# Attempt the signup
@post('/changePw')
def post_pw():
    # Handle the form processing
    newPw = request.forms.get('password')

    # Call the appropriate method
    return model.newPw_check(newPw)


# Display the rename
@get('/rename')
def get_rename_controller():

    return model.rename_form()


@get('/friendList')
def get_rename_controller():

    return model.friendList_form()


@get('/UserList')
def get_allUser_controller():

    return model.allUser_form()
# -----------------------------------------------------------------------------


@get('/DeleteUser')
def get_DeleteUser_controller():

    return model.DeleteUser_form()


@post('/DeleteUser')
def post_DeleteUser():

    user_name = request.forms.get('user')

    # Call the appropriate method
    return model.check_DeleteUser_post(user_name)


@get('/DeletePost')
def get_DeletePost_controller():

    return model.DeletePost_form()


@post('/DeletePost')
def post_DeleteUser():

    post_id = request.forms.get('ID')

    # Call the appropriate method
    return model.check_DeletePost_post(post_id)

# Attempt the signup
@post('/rename')
def post_newName():


    # Handle the form processing
    new_name = request.forms.get('newName')

    # Call the appropriate method
    return model.check_rename_post(new_name)

# -----------------------------------------------------------------------------
# Display the send message page
@get('/message')
def get_message_controller():
    '''
        get_messsage

        Serves the messsage page
    '''
    return model.message_form()


# -----------------------------------------------------------------------------
@get('/inbox')
def get_inbox_controller():

    return model.inbox_form()


@get('/alreadySent')
def get_inbox_controller():

    return model.alreadySent_form()

@get('/Send')
def get_inbox_controller():

    return model.send_form()

# Attempt the messsage
@post('/Send')
def post_Send():
    '''
        post_messsage

        Handles messsage attempts
        Expects a form containing 'friend' fields
    '''

    # Handle the form processing
    friend = request.forms.get('friend')
    message = request.forms.get('message')

    # Call the appropriate method
    return model.message_send(message, friend)

@get('/Post')
def get_post_controller():

    return model.post_form()


@post('/Post')
def post_Send():

    # Handle the form processing
    title = request.forms.get('Title')
    content = request.forms.get('content')

    # Call the appropriate method
    return model.post_send(title, content)

@get('/postSearch')
def get_post_controller():

    return model.postSearch_form()
@post('/Refresh')
def post_Refresh():
    '''
        post_messsage

        Handles messsage attempts
        Expects a form containing 'friend' fields
    '''


    # Call the appropriate method
    return model.message_receive()
# -----------------------------------------------------------------------------


@get('/help')
def get_help_controller():

    return model.help_form()


@post('/help')
def post_help():

    help_msg = request.forms.get('help_msg')

    # Call the appropriate method
    return model.help_post(help_msg)


@get('/HelpUser')
def get_helpUser_controller():

    return model.helpUser_form()

@get('/about')
def get_about():
    '''
        get_about
        
        Serves the about page
    '''
    return model.about()
#-----------------------------------------------------------------------------

# Help with debugging
@post('/debug/<cmd:path>')
def post_debug(cmd):
    return model.debug(cmd)

#-----------------------------------------------------------------------------

# 404 errors, use the same trick for other types of errors
@error(404)
def error(error): 
    return model.handle_errors(error)
