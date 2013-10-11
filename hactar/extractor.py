#! /usr/bin/env python
import sys

import BeautifulSoup as bs

from scraper import visible

def extract_text(content):
    """Extraxt text from html page"""
    soup = bs.BeautifulSoup(content)
    texts = soup.findAll(text=True)
    title = soup.title.string
    page_text = filter(visible, texts)
    content = u'\n'.join(page_text)
    return content, title

def generate_text(name):
    with open(name+'.html', 'rb') as html_file:
        text, title = extract_text(unicode(html_file.read(), errors='ignore'))
    with open(name+'.txt', 'wb') as text_file:
        text_file.write(text)


if __name__ == '__main__':
    
    generate_text(sys.argv[1])
