""" backend.py A superclass for all Hactar backends.  This is intended to be
similar to an interface. I.e. it defines the methods that a backend must
implement.
"""
import logging


class Backend(object):
    """ A superclass for all Hactar backends."""

    loc = None
    log_level = logging.WARN
    log = logging

    def __init__(self, location):
        """ Initialise using data located at location."""
        self.loc = location
        super(Backend, self).__init__()

    def add_nugget(self, ngt):
        """ Store a nugget in the backend."""
        pass

    def get_nuggets(self, terms=None):
        """ Return the nuggets of this user, filtered by terms."""
        pass
