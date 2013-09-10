""" scraper.py 
Attempt to scrape information from nuggets as they are added to the
database."""
import logging

def nugget_create(ngt):
    logging.debug('entered scraper.nugget_create(..)')
    ngt.scraped = True
    pass

def nugget_update(ngt):
    pass

def nugget_delete(ngt):
    pass
