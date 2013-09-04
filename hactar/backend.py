""" backend.py A superclass for all Hactar backends.  This is intended to be
similar to an interface. I.e. it defines the methods that a backend must
implement.
"""


class Backend():
    loc = None
    def __init__(self, location='test.sqlite'):
        """ Initialise using data located at location."""
        pass

    def add_nugget(self, ngt):
        pass

    def get_nuggets(self):
        pass
