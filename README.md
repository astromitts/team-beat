# Django Session Manager
This template repository comes with register, log in,
and log out views to get a jump start on building a 
Django project that requires user authentication.

It can generate login tokens for passwordless logins 
and password reset tokens. 

It does not include any email functionality for automated
support emails for login or reset tokens.

Extend or override the template files to customize.

### Settings
LOGIN_SUCCESS_REDIRECT (String)
urls.py path name of the view to redirect users to after
successful log in


## Middleware
Session manager middleware handles redirecting
unauthenticated users from accessing views that require
authentication, as well as rendering an error page for 
404s and uncaught exceptions to give a good UX.

### Settings
MIDDLEWARE_DEBUG (Boolean)
Set to True to bypass the middleware authentication/error 
handling

DEFAULT_ERROR_TEMPLATE (String)
Static path to the HTML template to use to display error
messages to users. The following context is passed to it 
from the middleware function:
status_code: Int, HTML status code of the error
error_message: String, error message to display on page

AUTHENTICATION_REQUIRED_REDIRECT (String)
urls.py path name of the view to redirect unauthenticated
users to when they attempt to access a restricted page

## Tests

All view logic should be covered via tests.py, to run:
`python manage.py test --settings=project.test_settings`
