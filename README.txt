Time Tracking Tools
-------------------

This package contains a bunch of Python scripts that I use to keep track of
my (working, mostly) time.


GTimeLog
--------

The most interesting of those is GTimeLog, which is a Gtk+ application.  Here's
how it works: every day, when you arrive to work, start up gtimelog and type
"arrived".  Then start doing some activity (e.g. reading mail, or working on
a task).  Whenever you stop doing an activity (either when you have finished
it, or when you switch to working on something else), type the name of the
activity into the gtimelog prompt.  Try to use the same text if you make
several entries for an activity (history helps here -- just use the up and down
arrow keys).  They key principle here is to name the activity after you've
stopped working on it, and not when you've started.  Of course you can type
the activity name upfront, and just delay pressing the Enter key until you're
done.

There's also a Tasks pane that lists tasks found in ~/.gtimelog/tasks.txt.
You can click on those to save typing.  Or you can specify a URL in
~/.gtimelog/gtimelogrc and download the task list from a wiki or wherever.

There are three broad categories of activities: ones that count as work (coding,
planning, writing proposals or reports, answering work-related email), ones
that don't (browsing the web for fun, reading personal email, chatting with
a friend on the phone for two hours, going out for a lunch break) and ones
which count as "half-work" (This are activities where only half of the time
spent for is counted as work. Depending on your employer, time spend in train
or plane when you do not work as described above, may count as "half-work".)

To indicate which activities are not work related add two asterisks to the
activity name. To indicate that an activity is "half-work" add '/2' at the end
of the activity name.
Look at the following examples::

  lunch **
  browsing slashdot **
  napping on the couch **
  in train to Frankfurt/2

GTimeLog displays all the things you've done today, and calculates the total
time you spent working, and the total time you spent "slacking".  It also
advises you how much time you still have to work today to get 8 hours of work
done (the number of hours in a day is configurable in ``~/.gtimelog/gtimelogrc``).
There are two basic views: one shows all the activities in chronological order,
with starting and ending times; while another groups all entries with the same
into one activity and just shows the total duration.

At the end of the day you can send off a daily report by choosing File -> Daily
Report.  A mail program (Mutt in a terminal, unless you have changed it in
``~/.gtimelog/gtimelogrc``) will be started with all the activities listed in it.
My Mutt configuration lets me edit the report before sending it.

If you make a mistake and type in the wrong activity name, or just forget to
enter an activity, don't worry.  GTimeLog stores the time log in a simple plain
text file ``~/.gtimelog/timelog.txt``.  Every line contains a timestamp and the
name of the activity that was finished at the time.  All other lines are
ignored, so you can add comments if you want to -- just make sure no comment
begins with a timestamp.  You do not have to worry about GTimeLog overwriting
your changes -- GTimeLog always appends entries at the end of the file, and
does not keep the log file open all the time.  You do have to worry about
overwriting changes made by GTimeLog with your editor -- make sure you do not
enter any activities in GTimeLog while you have timelog.txt open in a text
editor.


Future Plans
------------

Configuration dialog.  The ability to browse through history (view daily and
weekly reports for past days and weeks).


Other Tools
-----------

timelog.py is an earlier, less powerful text-mode version of gtimelog.  You
type in activity names, and timelog writes them down into timelog.txt with
timestamps prepended.

today.py can generate a daily report from timelog.txt.  It does not group
activities with the same name, and it does not spawn a mail client.
You can also specify the date on the command line -- generating reports for
earlier days is not yet possible with GTimeLog.

sum.py can help you consolidate daily reports.  It is designed to work as a
filter: it reads lines from the standard input, extracts durations from
those lines (formatted as "N hours, M min" at the end of the line, and
separated by at least two spaces from other text), sums them and prints the
total.  If you use vim for editing daily reports, you can select a bunch of
lines and pipe them through sum.py.

difftime.py is a hacky interactive calculator that I used to generate daily
reports from timelog.txt before today.py and gtimelog.py could automate the
task.  The biggest feature of difftime.py (it's raison d'etre if you will)
is the ability to calculate the duration between two timestamps.


Data Formats
------------

These tools were designed for easy interoperability.  There are two data
formats: one is used for timelog.txt, another is used for daily reports.
They are both human and machine readable, easy to edit, easy to parse.

Timelog.txt is already described above.  Here is a more formal grammar::

  file ::= (entry|comment)*

  entry ::= timestamp ":" space title newline

  comment ::= anything* newline

  title ::= anything*

  timestamp is 'YYYY-MM-DD HH:MM' with a single space between the date and
  time.

Daily reports look like this::

  random text
  random text
  Entry title                Duration
  Entry title                Duration
  random text
  Entry title                Duration
  Entry title                Duration
  random text

Formal grammar::

  report ::= (entry|comment)*

  entry ::= title space space duration newline

  comment ::= anything* newline

  title ::= anything*

  duration ::= hours "," space minutes
            |  hours space minutes
            |  hours
            |  minutes

  hours ::= number space "hour"
         |  number space "hours"

  minutes ::= number space "min"

There is a convention that entries that include two asterisks in their titles
indicate slacking or pauses between work activities.

Task list is a text file, with one task per line.  Empty lines and lines
starting with a '#' are ignored.  Task names should consist of a group name
(project name, XP-style story, whatever), a colon, and a task name.  Tasks will
be grouped.  If there is no colon on a line, the task will be grouped under
"Other".

Hourtracker
-----------
If you're using the hourtracker version from gocept, add a new section
to your configuration file::

    [hours]
    url = http://www.myhourtracker.com/
    username = foo
    password = bar
    tasks = http://www.myhourtracker.com/tasks
    projects = http://www.myhourtracker.com/projects

Specify the projects and tasks like the following example::

    2006-07-25 09:37: operations: General activities: Morgen meeting
    date       time   project     task                description

Note: You don't have to provide the _full_ project and task name. In
the example above the string 'operat' will probably match operations
if nothing else starts with 'operat' in the project listing of the
hour tracker system.

Start your gtimelog in the console first. It'll print out useful debug
information.

Use the File > Fill Hour Tracker menuitem to upload your hours.


Redmine
-------

If you're using the Redmine issue tracker, you can upload the gtimelog data
there, too. This will happen automatically with the 'Fill Hour Tracker' command
if the following configuration is provided::

    [redmine]
    url=https://www.my-redmine.com/
    api_key=123deadbeef
    activity=9
    projects = My_Project1
               My_Project2

Only tasks that belong to the projects listed there will be uploaded to Redmine.

You can provide multiple [redmine] sections, but take care to give them unique
names (e. g. [redmine1], [redmine2], [redmine-foo], [redmine-bar]).

The api_key is available on the "My account" page.

Unfortunately, the Redmine activity can't be retrieved currently, so the ID to
use needs to be given in the configuration. You can look it up in the HTML
source of /issues/123/time_entries/new.


Holidays
--------

Holidays are indicated by ending a line in '$$$'. Holidays are
substracted from required work time, so it's necessary to have two
entries for a holiday those duration is the time you would work when
you are not in holiday.

CAUTION: Only use this feature, if you do _not_ want to save your
holiday times in hourtracker.


Author
------

Marius Gedminas
<marius@pov.lt>


Contributors
------------

Thom May
Dafydd Harries
Ignas Mikalajūnas
Michael Howitz
Roman Joost

Icon
----

gtimelog.png is really a renamed copy of gnome-set-time.png from
/usr/share/pixmaps/

