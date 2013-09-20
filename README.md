hactar
======

Hactar is a personal todo list, diary and knowledge management system. Your
personal AI (not really).


Hactar is made up of three components that are designed to be modular:

 * **backend** - Stores data (sqlite?)
 * **core** - Contains logic and connects frontend to backend
 * **frontend** - Displays information and enables user interaction.

Hactar may also support plugins that add extra functionality such as scraping
websites and intelligent searching. These plugins should only mainly interact
with the core (not the front or back ends).

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
 1. add nugget/bookmark with text/description
 2. search nuggets by topic/keywords

Betty likes to keep to-do lists. Hactar will accept various tasks and
attempt to prioritise them for betty. Tasks can have information attached to
them, due dates and contain subtasks.

Data model
----------

Information is stored in a **nugget**. A nugget consists of:
 * description (markdown)
 * keywords
 * added date
 * modified date
 * uri (optional)
 * id (hash of url or blob)

Data must be unique, i.e. each uri may only exist once.

TODO and action items are represented by a **task**, this consists of:
 * text (markdown, should be one line)
 * priority
 * due datetime (optional)
 * start datetime
 * finish datetime
 * subtasks
 * nuggets

Feature Priority
----------------
 1. search nuggets
 2. basic plugin architecture (scraping etc.)
 3. delete nuggets
 4. update nuggets
