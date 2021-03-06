#!/usr/bin/env python
# vim:fileencoding=utf-8
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__ = 'GPL v3'
__copyright__ = '2013, Kovid Goyal <kovid at kovidgoyal.net>'

import shutil

MAX_SAVEPOINTS = 100

def cleanup(containers):
    for container in containers:
        try:
            shutil.rmtree(container.root, ignore_errors=True)
        except:
            pass

class State(object):

    def __init__(self, container):
        self.container = container
        self.message = None

class GlobalUndoHistory(object):

    def __init__(self):
        self.states = []
        self.pos = 0

    @property
    def current_container(self):
        return self.states[self.pos].container

    def open_book(self, container):
        self.states = [State(container)]
        self.pos = 0

    def add_savepoint(self, new_container, message):
        self.states[self.pos].message = message
        extra = self.states[self.pos+1:]
        cleanup(extra)
        self.states = self.states[:self.pos+1]
        self.states.append(State(new_container))
        self.pos += 1
        if len(self.states) > MAX_SAVEPOINTS:
            num = len(self.states) - MAX_SAVEPOINTS
            cleanup(self.states[:num])
            self.states = self.states[num:]

    def rewind_savepoint(self):
        ''' Revert back to the last save point, should only be used immediately
        after a call to add_savepoint. If there are intervening calls to undo
        or redo, behavior is undefined. This is intended to be used in the case
        where you create savepoint, perform some operation, operation fails, so
        revert to state before creating savepoint. '''
        if self.pos > 0 and self.pos == len(self.states) - 1:
            self.pos -= 1
            cleanup([self.states.pop().container])
            ans = self.current_container
            ans.message = None
            return ans

    def undo(self):
        if self.pos > 0:
            self.pos -= 1
            return self.current_container

    def redo(self):
        if self.pos < len(self.states) - 1:
            self.pos += 1
            return self.current_container

    @property
    def can_undo(self):
        return self.pos > 0

    @property
    def can_redo(self):
        return self.pos < len(self.states) - 1

    @property
    def undo_msg(self):
        if not self.can_undo:
            return ''
        return self.states[self.pos - 1].message or ''

    @property
    def redo_msg(self):
        if not self.can_redo:
            return ''
        return self.states[self.pos].message or ''

