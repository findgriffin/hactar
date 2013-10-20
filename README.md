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

Betty likes to keep to-do lists. Hactar will accept various actions and
attempt to prioritise them for betty. Actions can have information attached to
them, due dates and contain subactions.

Data model
----------

Information is stored in a **meme**. A meme is defined by a title OR URL a meme
also MUST have a description (in markdown). Data must be unique, i.e. each url
or title may only exist once.

Information is only useful if it leads to *outcomes* in the real world, hence
hactar stores **actions**. Actions are anything that the user does, has done,
is doing or will do. 

The various fields of an action can often be left blank. 

A **task** is an action with a 'due' date/time.

* A task is completed when it has a finish time.
* A task may also have a start time, points or priority.

An **event** is an action with a start and/or finish time and has 3 states:

* latent
* ongoing
* complete

In the future **memes** and **actions** may be linked (eg. actions may have
sub-actions).

Feature Priority
----------------
 1. Demagicify whoosh integration
 1. Implement upgrading of db schema
 1. Implement asynchronous/background tasks
 1. Implement tasks (using google calendar API)
 1. AJAXify (eg. update web page status)
