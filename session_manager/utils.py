from datetime import datetime, timedelta
import pytz


def twentyfourhoursfromnow():
    """ Helper function for getting datetime 1 day from now
    """
    utc=pytz.UTC
    return utc.localize(datetime.now()) + timedelta(1)


def oneweekfromnow():
    """ Helper function for getting datetime 1 week from now
    """
    utc=pytz.UTC
    return utc.localize(datetime.now()) + timedelta(7)

def yesterday():
    """ Helper function for getting datetime from yesterday
    """
    utc=pytz.UTC
    return utc.localize(datetime.now()) + timedelta(-1)

special_chars = [
    '!',
    '@',
    '#',
    '$',
    '%',
    '^',
    '&',
    '*',
    '(',
    ')',
    '~',
    ';',
    ':',
    '<',
    '>',
    '"',
    '?',
    '/',
    "'",
    '[',
    ']',
    '|',
    '\\'
    '-',
    '_',
    '{',
    '}',
]
