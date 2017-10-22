===========
 Git tasks
===========

.. image:: https://travis-ci.org/Gustra/git-tasks.svg?branch=master
    :target: https://travis-ci.org/Gustra/git-tasks

Git plugin for managing task branches on the command line, and adding task
information lines to commit messages.

Keeping track of which tasks are currently being worked on in a repository can
be a problem if there are a lot of concurrent tasks, or if the frequency of
updates is low, so that it is easy to forget the current tasks between
sessions.

This is where ``git-tasks`` comes in and takes care of tracking those tasks.
When starting a task, a task branch is created which maps to a configured task
system. Information about the task is fetched from the task management system
when needed.

Features overview:

* Starting tasks and switching between tasks (branches)
* List current tasks
* Print status for all tasks
* Commit message hook which adds a task line in the commit message

The following task system backends are supported:

Generic
   An external command is run when fetching data from a task/ticket system

Github
   Connects to the issues for a Github repository

------------
 User Guide
------------

Configuration
=============

Introduction
------------

``git-tasks`` requires a configuration file with at least of one backend
configured. This is needed so that task branches can be identified by the
program. All configuration files are written in YAML_ syntax and the minimal
configuration is::

    systems:
    - type: generic

This will consider branches matching the regular expression ``task-[0-9]+$``
to be task branches. In this case the information and the functionality will
be limited, since there is no backend to provide meta-data about tasks.

A more complete example::

    systems:

    - name: Tasks-R-us in-house ticket system
      type: generic
      command: /env/bin/tasks-r-us
      patterns:
      - "dev-[0-9]+[a-z]*$"
      - "support-[0-9]+$"

    - name: Bugzilla
      type: generic
      command: bugzilla-wrapper
      patterns: [ "task-[0-9]+$" ]

Supported Systems
-----------------

Each system entry in the configuration file is a key-value object, and all
top-level values are common. Most backends have system-specific setting which
are stored as a key-value object under the key ``our``, for the lack of a
better keyword.

Common data
...........

The following data items are set for any backend system:

type
   (Mandatory). The system backend for this entry.

name
   (Optional). A human-readable name for this system.

credentials-file
   (Optional). Path to a credentials file if this backend requires
   authentication. The content is system-specific, eg. for Github it must
   hold "user" and "password" in YAML format.

our
   (Optional). System-specific configurations.

patterns
   (Optional). A list of regular expressions used to match branch names to
   tasks for this entry.

Generic Specifics
.................

command
   Command to execute when meta-data is to be fetched from the system

Provides a generic interface for fetching meta-data about tasks. This can be
used to interface an in-house developed ticket system, or to connect to any
system for which ``git-tasks`` lacks innate support for.

The command must implement the following interface:

get-task *id*
   print a task structure in YAML format on stdout. The task structure has the
   the following keys, where all are optional:

   title
      The task title/subject/heading

   status
      Current status/state, e.g. new, ongoing, triaged, closed etc. The value
      is not interpreted by ``git-tasks``

Example::

    > bugzilla-wrapper get-task ticket-4567
    title: Motor fails to start if choke is held
    status: in-progress

Github Specifics
................

repository
   (Mandatory). Project or id which uniquely identifies the repository on
   Github, eg. "someuser/some-repo", "repository/NN".

Provides connection to the Github repository issues system.

Starting/switching tasks
========================

``git tasks start`` *branch*

where *branch* is the branch representation of the task identifier, eg.
``issue-22``, ``jira-78``, ``tuleap-1234``. This will switch to the given task
and create the branch if needed. The normal git checkout command is used,
which may fail if there are uncommitted changes.

The ``prepare-commit-msg`` hook will be installed into the ``.git/hooks``
directory if it is absent.

Listing current tasks
=====================

Lists the branches in the repository which can be associated with the defined
backend systems::

    git tasks list

Show tasks' status
==================

Prints the current task branches, their status and title::

    git tasks status

Example::

    > git tasks status
    jira-56 (New): Intermittent alarm in HAL
    task-b5 (Closed): refactory boyance.c
    task-a78 (Waiting for verification): Write User Guide

References
==========

:: _YAML: https://yaml.org/
