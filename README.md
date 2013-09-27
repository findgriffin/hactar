hactar
======

Hactar is a personal todo list, diary and knowledge management system. Your
personal AI (not really).

Hactar may also support plugins that add extra functionality such as scraping
websites and intelligent searching. These plugins should only mainly interact
with the core (not the front or back ends). Hactar uses the flask
microframwork, sqlalchemy as it's orm and sqlite as it's backend.

Planned plugins (in planned implementation order):
 1. scraper - scrape linked urls for information that can later be searched
 2. advanced search - return synonyms, related topics, near matches etc.
 3. dumper - dump related topics into cheatsheets

User stories
------------

Alice is a programmer and uses the internet to find snippets and examples to
help her in her work. She uses hactar to bookmark code snippets, guides,
critical documentation and other information that she may need in the future.
Later alice can search for related terms, eg. 'multithreading in python' to
find previously bookmarked information.
The tasks that alice needs to complete are:
 1. add meme/bookmark with text/description
 2. search meme by topic/keywords

Betty likes to keep to-do lists. Hactar will accept various events and
attempt to prioritise them for betty. Events can have information attached to
them, due dates and contain subevents.

Data model
----------

Information is stored in a **meme**. A meme is defined by a title OR URL a meme
also MUST have a description (in markdown). Data must be unique, i.e. each url
or title may only exist once.

TODO and action items are represented by a **event**. Events can have due
dates, start times finish times etc.

In the future **memes** and **events** may be linked (eg. events may have
sub-events).

Feature Priority
----------------
 1. Implement upgrading of db schema
 1. Implement tasks (using google calendar API)
 1. AJAXify (eg. update web page status)
