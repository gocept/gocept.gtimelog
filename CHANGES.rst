Changelog
=========

3.0 (unreleased)
----------------

Backwards incompatible changes
++++++++++++++++++++++++++++++

- Remove the GTK-GUI from this package. Use the upstream
  https://github.com/gtimelog/gtimelog for GUI from now on.

- Drop support for Python 2.7.

Features
++++++++

- Add support for Python 3.7, 3.8, 3.9.

- Add ability to start the name of a bugtracker in ``gtimelogrc`` with
  ``disabled`` so it gets ignored during bugtracker upload.

Bug fixes
+++++++++

- Fix collmex tasks download: Probably due to an Collmex API change the task
  list was empty when newly downloaded.


2.0 (2021-04-07)
----------------

Note
++++

This will be the last release with GTK/GUI support. The upstream package did
diverge too much from this code base, so this part is dropped. The CLI tools
and upload scripts will be still maintained in the future.

This will also be the last release compatible with Python 2.

Changes
+++++++

- Update the holidays of `gtl-progess` to 2018.

- Improve gtl-progres terminal color detection.

- Display progress of work done in current month and year in `gtl-progress`
  output.

- No longer ignore project `urlaub` in progress scripts.

- Drop JIRA support as the package is no longer installable on Python 2.

- Require ``pytest < 5`` to keep Python 2 support.

- Migrate to Github.


1.1.0 (2016-02-03)
------------------

- Add integration to notification center (MacOS >= 10.9).

  When running the upload (e.g. via a cronjob) you now get notified via MacOSs
  notification center. Clicking the notification opens the timelog in your
  configured editor.


1.0 (2015-11-18)
----------------

- Bump dependencies to newest versions. Also bump package version to 1.0 as
  its now stable for a long time.

- Allow unicode in task description.

- Allow using '*' as a project in the bugtracker project list to support
  defaulting to a tracker. Has lowest score and any specific project will
  override.

- Add error reporting ticket # but no tracker was found.

- ``gtl-progress``: Workaround for Python on MacOS and Nix which is not having
  curses build in.


0.10.0 (2015-06-08)
-------------------

- Improve error reporting when timelog entries are out of order (i.e. end before begin)

- Don't put out colors in ``gtl-progress`` when terminal doesn't support it.

- Use locally build `` jira-python`` (now named ``jira``) instead of
  ``jira-python`` which no longer existis on PyPI.

- Ignore inactive projects and tasks when updating tasklist from collmex.
  (#13840)


0.9.0 (2014-02-25)
------------------

- Uploading via ``bin/gtl-upload`` defaults to the last seven days when given
  no explicit date to upload.


0.8.6 (2013-12-06)
------------------

- Fix `decode_passwords` feature to again allow umlauts in task
  descriptions.

- Allow to use ``decode_passwords = rot13`` to encode passwords using the
  ROT13 algorithm.


0.8.5 (2013-12-05)
------------------

- Fixed recent fix: actually use the encoding opt-in in the other place, too.


0.8.4 (2013-12-05)
------------------

- Fixed recent change: actually use the encoding opt-in.


0.8.3 (2013-12-05)
------------------

- Work around jira-python bug #72 with non-ASCII server error messages.

- Removed traces of Hour tracker, including dependency on lxml.

- Obfuscate plain-text passwords in .gtimelogrc to at least make them less
  readily readable by someone happening to see you open the file; off by
  default. Encode your passwords with base64 and set
  ``gtimelog:decode_passwords = base64`` to use obfuscation.

- Find the tracker for a project by longest prefix match, independent of the
  order of trackers in gtimelogrc.


0.8.2 (2013-09-25)
------------------

- Improve reporting of entries which cannot be matched.

- Fix commandline upload (broken after jira/redmine refactoring).


0.8.1 (2013-09-24)
------------------

- Work around jira-python bug #60 that makes multiple connections to different
  servers impossible.


0.8 (2013-09-19)
----------------

- Introduce command-line utility ``gtl-progress`` which calculates the work-done
  progress of a given (or the current by default) week.

- Introduce command-line utility ``gtl-log`` which can be used to add timelog
  entries from the command-line. A bash completion script is shipped to auto
  complete projects and tasks.

- Remove HT upload from upload script.

- Add JIRA bugtracker: supports uploading time logs and getting issue subject
  for Collmex reporting (#12846).


0.7.0 (2012-07-17)
------------------


- Assert that no entries with start after end are uploaded to collmex.

- Day parameter of cli is now optional (default: today).


0.6.1 (2012-02-21)
------------------

- Fixed brown-bag release.


0.6.0 (2012-02-21)
------------------

- Don't use inactive tasks in collmex.


0.5.2 (2012-02-06)
------------------

- Fixed brown-bag release.


0.5.1 (2012-02-06)
------------------

- Fixed daily and weekly report functions which were broken since version
  0.5.


0.5 (2012-01-26)
----------------

- Introduce command-line upload utility ``gtimelog-cli`` (#10105).


0.4.2 (2011-05-16)
------------------

- Make sure timelog comments uploaded to Redmine are at most 255 characters
  long, avoid including duplicate comments in the same time entry (#9016).


0.4.1 (2011-04-11)
------------------

- Fix bug that too many Redmine time entries were deleted (#8909).


0.4.0 (2011-04-07)
------------------

- Change Redmine integration to use the REST API (#8901).
- Collmex uploads the whole week (#8808).
- Fix bug with umlauts in Collmex (#6474).


0.3.1 (2011-04-06)
------------------

- Update URLs for Redmine 1.1


0.3.0 (2011-04-05)
------------------

- Change Redmine integration so it does not require a plugin on the Redmine
  server. Users upgrading need to configure the name of the activity to use.
- Multiple Redmine servers are now supported (see README.txt).
- Filling Redmine has been extracted into its own command and is no longer done
  automatically along with HT or Collmex (#8884).
- Fix encoding problem with HT (#6474).


0.2.0 (2010-09-28)
------------------

- Use Rest-API to get issue subject.


0.1.9 (2010-04-09)
------------------

- Prevent an error with completion entries being None that occured on OS X.


0.1.8 (2010-04-07)
------------------

- Repair auto-completion that broke in 0.1.7.


0.1.7 (2010-04-01)
------------------

- Don't use lower-casing for autocompletion.

- Fix Collmex upload: First normalise projects, then sort them.


0.1.6 (2010-03-29)
------------------

- Support Redmine 0.9 with form ``authenticity_token``


0.1.5 (2010-02-26)
------------------

- Avoid showing duplicate entries in auto-completion,
  when loading auto completion from history at startup.


0.1.4 (2010-02-26)
------------------

- More relaxed, flexible auto completion.


0.1.3 (2010-02-19)
------------------

- Nothing changed yet.


0.1.2 (2009-11-23)
------------------

- Populate history with all previous entries, sort reverse-chronological.
- Added 'delete last entry' command.


0.1.1 (2009-11-15)
------------------

- Added option ``log_level`` which sets the default log level (``DEBUG``,
  ``ERROR``).
- Added log window. Log messages with level ``DEBUG`` will show up here
  instead of at the shell.


0.1 (2009-11-06)
----------------

- begin Changelog

- added import of projects and tasks from Collmex

- added export of activities to Collmex
