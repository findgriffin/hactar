import re

from requests import get
import BeautifulSoup as bs


def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head',
            'title']:
        return False
    elif re.match('<!--.*-->', str(element)):
        return False
    if len(element) < 1 or element.isspace():
        return False
    return True

def get_data(uri):
    resp = get(uri)
    status_code = resp.status_code
    title = re.search('<title>(.*)</title>', resp.content)# just title for now
    texts = bs.BeautifulSoup(resp.content).findAll(text=True)
    page_text = filter(visible, texts)
    if title:
        title = title.group().lstrip('<title>').rstrip('</title>')
    else:
        title = 'unknown'
    return status_code, title, ' '.join(page_text)


if __name__ == "__main__":
    import sys
    code, title, text = get_data(sys.argv[-1])
    print "%s: %s" % (title, code)
    print 'text:'
    print text
