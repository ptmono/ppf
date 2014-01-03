#!/usr/bin/env python
# coding: utf-8

import pickle
from dlibs.common import *
from nltk import FreqDist
import collections

import os
from dlibs.logger			import loggero


def save_to_pickle(filename, data):
    try:
        fd = open(filename, 'w')
        pickle.dump(data, fd)
    except:
        fd = open(filename, 'wb')
        pickle.dump(data, fd, 2)

    fd.close()

def open_to_pickle(filename):
    try:
        fd = open(filename, 'r')
        return pickle.load(fd)
    except:
        fd = open(filename, 'rb')
        return pickle.load(fd)


def get_samples(path, separator='\n'):
    try:
        fd = open(path, 'r')
    except:
        fd = oepn(filename, 'rb')

    # Remove empty strings
    return [u(ele) for ele in filter(None, fd.read().split(separator))]
    



class DfreqDist(FreqDist):
    """
    >>> raw = Data.get_dataset_as_raw()
    >>> tokens = regexp_tokenize(raw, pattern=Var.tokenize_regexp)
    >>> tokens = filter_tokens(tokens, Var.filter_regexp)
    >>> ana = Analize(tokens)
    >>> ana.counted_word_list(1000)
    OrderedDict([(1681, ['및']), (2997, ['모집'])])
    
    """
    def counted_word_list(self, min_count):
        result = {}
        for word in self:
            count = self[word]
            if count < min_count: break

            try:
                result[count].append(word)
            except KeyError:
                result[count] = [word]
        return collections.OrderedDict(sorted(result.items()))

    def save_counted_word_list(self, min_count, filename):
        counted_word_list = self.counted_word_list(min_count)
        fd = open(filename, 'w')
        for count in reversed(counted_word_list):
            msg = str(count) + '\t' + ", ".join(counted_word_list[count]) + "\n"
            try:
                fd.write(msg)
            except UnicodeEncodeError:
                fd.write(msg.encode('utf-8'))
        fd.close()


class File(object):
    """
    The class is used to open a file safely. There is two process AA and
    BB. AA couldn't read the file during BB is writting the _file. AA will
    wait for the time correlated with lock_wait_time and
    lock_wait_interval. The time is lock_wait_time * lock_wait_interval.

    """
    def __init__(self, filename, mode, lock_interval=1):

        self.filename = filename
        self.mode = mode
        self._lock_filename = self._lock_filename()
        self.lock_wait_count = 0
        self.lock_wait_time = 5
        self.lock_wait_interval = lock_interval
        # We couldn't remove the lock and backup that is created by other
        # object.
        self.permission_lockfile = False
        self.permission_backupfile = False
        self.fd = self._init()

    def _init(self):
        loggero().debug("Init file... %s" % id(self))
        try:
            self._waitUnlock()
        except IOError as err:
            # There is unlock file. We wait self.lock_wait_time X
            # self.lock_wait_interval seconds. The object assumes that
            # there are no process which locking the file for the seconds.
            # We forcely restore the file.

            # TODO: Log that. Think more about vulnerability.

            # Fixme: If serveral process continuosly lock the file, it
            # will over the seconds. It will be critical problem.
            self.restore()
            self._unlockForce()
            self._removeBackupForce()
            
        if self.mode == 'r':
            try:
                self.fd = open(self.filename, self.mode)
                return self.fd
            except FileNotFoundError as err:
                loggero().debug("File not found...")
                self._unlockForce()
                loggero().debug("Unlock...")                
                self._removeBackupForce()
                loggero().debug("Remove backup...")
                raise FileNotFoundError(err)
            
        elif self._checkFile():
            self._lock()
            self._backup()

        else:
            self._lock()
            self.permission_backupfile = True

        try:
            fd = open(self.filename, self.mode)
        except IOError:
            dirname = self.filename[:self.filename.rfind('/')]
            os.makedirs(dirname)
            fd = open(self.filename, self.mode)
        return fd
        

    # def __call__(self):
    #     if self.mode == 'w':
    #         return self.write()
    #     return self.read()

    def read(self):
        return self.fd.read()

    def write(self, content):
        self.fd.write(content)
        

    def close(self):
        # If no self.fd, there is lock file. It means other File object do
        # not complete IO for the document by accident such as blackout.
        # It means we will resore the backup file at later. To prevent the
        # files we use self.permission_lockfile and
        # self.permission_backupfile.
        if (self.mode in ['w', 'w+', 'r+', 'a', 'a+']) and self.permission_lockfile and self.permission_backupfile:
            self._unlockForce()
            self._removeBackupForce()
        self.fd.close()

    def _remove(self):
        "It is not used. Just for test."
        self.close()
        os.remove(self.filename)

    def _checkFile(self):
        return os.path.exists(self.filename)

    def _checkBackupFile(self):
        filep = os.path.exists(self._backup_filename())
        if filep:
            True
        else:
            False

    def _backup_filename(self):
        dirname = os.path.dirname(self.filename)
        filename = os.path.basename(self.filename)
        return dirname + "/#" + filename + "#"
        

    def _backup(self):
        fd = open(self.filename, 'r')
        content = fd.read()
        fd.close()

        # Fixme: Is need error handling?
        fd = open(self._backup_filename(), 'w')
        fd.write(content)
        fd.close()
        self.permission_backupfile = True

    def _removeBackupForce(self):
        try:
            os.remove(self._backup_filename())
        except OSError:
            # No such file or directory
            pass

    def restore(self):
        filename = self._backup_filename()
        fd = open(filename, 'r')
        content = fd.read()
        fd.close()

        fd = open(filename, 'w')
        fd.write(content)
        fd.close()
        
    def _lock_filename(self):
        
        result = self.filename + ".lock"
        return result

    def _checkLockp(self):
        return os.path.exists(self._lock_filename)

    def _lock(self):
        "Lock the file"
        self._waitUnlock()
        loggero().debug("Create lock file... %s" % id(self))
        fd = open(self._lock_filename, 'w')
        fd.close()
        self.permission_lockfile = True

    def _unlockForce(self):
        try:
            os.remove(self._lock_filename)
        except OSError:
            # No such file or directory
            pass

    def _waitUnlock(self):
        """
        Raise IOError when can not unlock.
        """
        if self._checkLockp():
            while (self.lock_wait_count < self.lock_wait_time):
                time.sleep(self.lock_wait_interval)
                if not self._checkLockp():
                    return True
                self.lock_wait_count += 1
            raise IOError("Already exists lock file %s" % self._lock_filename)
    
