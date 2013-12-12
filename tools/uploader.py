#!/usr/bin/python
# coding: utf-8

from ftplib import FTP, error_perm
import os
import re
import getpass
import sys
import shutil

__current_abpath = os.path.realpath(os.path.dirname(__file__)) + "/"
ROOT_PATH = os.path.dirname(os.path.dirname(__current_abpath))

if ROOT_PATH not in sys.path:
    sys.path.insert(0, ROOT_PATH)

from ppf import config
from ppf.install		import init_db
import dlibs
from dlibs.d_os		import recursive_glob2

# Consider: How about to use ftptool?
class UFTP(FTP):
    '''
    # TODO: Error control. FTP has no exception for bad address
    >>> #ftp_fails = UFTP("aa", "bb", "bb")

    >>> host = config.server_host
    >>> user = config.server_user_id
    >>> passwd = config.server_passwd
    >>> ftp = UFTP(host, user, passwd)
    >>> path = "/home/ptmono/aaaauuu/bbbccc/nnnyyy/icu/ync/tny/kkc"

    >>> ftp.mkd('/home')			#doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    error_perm: 550 Create directory operation failed.
    
    >>> # exists
    >>> ########
    >>> ftp.exists("/abs")
    False

    >>> # _directoryInfo
    >>> ################
    >>> d_info = ftp._directoryInfo(path)
    >>> d_info
    [46, 42, 38, 34, 27, 20, 12, 5, 0]

    >>> # _exists_level
    >>> ###############
    >>> d_level = ftp._exists_level(path, d_info)
    >>> d_level
    6
    >>> path[:d_info[d_level]]
    '/home/ptmono'

    >>> path2 = '/aaa/bbb/ccc/ddd'
    >>> d_info2 = ftp._directoryInfo(path2)
    >>> ftp._exists_level(path2, d_info2)
    3

    >>> ftp.dirs_not_exists(path)
    ['/home/ptmono/aaaauuu', '/home/ptmono/aaaauuu/bbbccc', '/home/ptmono/aaaauuu/bbbccc/nnnyyy', '/home/ptmono/aaaauuu/bbbccc/nnnyyy/icu', '/home/ptmono/aaaauuu/bbbccc/nnnyyy/icu/ync', '/home/ptmono/aaaauuu/bbbccc/nnnyyy/icu/ync/tny', '/home/ptmono/aaaauuu/bbbccc/nnnyyy/icu/ync/tny/kkc']
    >>> ftp.dirs_not_exists('/home/ptmono/')
    []
    >>> ftp.dirs_not_exists('/home/ptmono')
    []
    >>> ftp.dirs_not_exists('/home/')
    []
    >>> ftp.dirs_not_exists('/home/ptmono/abc')
    ['/home/ptmono/abc']
    >>> ftp.dirs_not_exists('/home/ptmono/abc', is_dir=False)
    []

    >>> ftp._d_mkds(path)
    >>> os.removedirs(path)

    ### === Upload
    ### __________________________________________________________
    >>> server_path = "/home/ptmono/anan/ccd"
    >>> ftp.upload(server_path, UploadInfoCommon._getFileListFromListFile('installer_file_list'))

    >>> client_filename = ROOT_PATH + "/teest.bbcsyn"
    >>> server_filename = server_path + "/teest.bbcsyn"
    >>> fd = open(client_filename, 'w')
    >>> fd.write("aaa")
    >>> fd.close()

    >>> ftp.upload(server_path, client_filename)
    >>> # Check server side file
    >>> fd = open(server_filename)
    >>> print fd.read()
    aaa
    >>> fd.close()
    >>> os.remove(client_filename)

    >>> dummy = '/home/ptmono/Desktop/Documents/works/0cvs/trunk/ppf/files/dummy_upload.file'
    >>> shutil.rmtree(path[:path.rfind("/")], ignore_errors=True)

    '''

    def d_cwd(self, dirname):
        '''
        There is not dirname, then create dirname and cwd to dir.
        '''
        try:
            return self.cwd(dirname)
        except error_perm, msg:
            if msg.args[0][:3] == '550':
                self.d_mkds(dirname)
                self.cwd(dirname)

    def d_mkds(self, dirname):
        "Create directory with subdirectories."
        try:
            return self.mkd(dirname)
        except error_perm, msg:
            if msg.args[0][:3] == '550':
                self._d_mkds(dirname)

    def _d_mkds(self, dirname):
        directories_to_be_created = self.dirs_not_exists(dirname)

        for subd in directories_to_be_created:
            self.mkd(subd)

    def dirs_not_exists(self, path, is_dir=True):
        '''Returns the list of subdirectories not exists with path. If
        IS_DIR is True, the function treats the path as directory.
        '''
        result = []
        if is_dir: path = self._directory_have_to_last_slash(path)
        dir_info = self._directoryInfo(path)
        dir_level = self._exists_level(path, dir_info)

        dead_dir_info = dir_info[:dir_level]

        for p in dead_dir_info:
            result.append(path[:p])

        result.reverse()
        return result

    def upload(self, path, target):
        '''

        path: root directory of ftp
        target: filename. It is not absolute path. based on the root
        directory of client. It can be string or list.
        '''
        if isinstance(target, list):
            self._uploadFiles(path, target)
        elif isinstance(target, str):
            self._uploadFile(path, target)

    # TODO: Can merge _uploadFile and _uploadFiles.
    def _uploadFile(self, path, filename):
        '''
        PATH is target path.
        FILENAME is absolute path or related path for project root.
        '''

        self.d_cwd(path)
        if filename == '': return
        
        # uploader.py is at tools directory. To create the file descriptor
        # we need absolute filename.
        # We can take either absolute path or related path.
        if filename[0] == '/':
            ab_filename = filename
            # We need related name for in ftp.
            filename = filename.replace(ROOT_PATH + '/', '')
        else:
            ab_filename = ROOT_PATH + '/' + filename

        # SITE CHMOD uses owner/member/others permission
        # representation
        permission = os.stat(ab_filename)
        permission_chmod = oct(permission.st_mode)[3:]
        try:
            fd = open(ab_filename, 'rb')
        except IOError, err:
            # Is a directory error
            # Just create directory
            if err[0] == 21:
                self.d_mkds(filename)
                self.voidcmd('SITE CHMOD ' + permission_chmod + ' ' + filename)
                return
        try:
            self.storbinary('STOR %s' % filename, fd)

        except error_perm, msg:
            if msg[0][:3] == '553':
                dirname = filename[:filename.rfind('/')]
                self.d_mkds(dirname)
                self.storbinary('STOR %s' % filename, fd)
        self.voidcmd('SITE CHMOD ' + permission_chmod + ' ' + filename)
        fd.close()


    def storbinary(self, cmd, fp, blocksize=8192, callback=None, rest=None):
        """Store a file in binary mode.  A new port is created for you.

        Args:
          cmd: A STOR command.
          fp: A file-like object with a read(num_bytes) method.
          blocksize: The maximum data size to read from fp and send over
                     the connection at once.  [default: 8192]
          callback: An optional single parameter callable that is called on
                    on each block of data after it is sent.  [default: None]
          rest: Passed to transfercmd().  [default: None]

        Returns:
          The response code.
        """
        self.voidcmd('TYPE I')
        conn = self.transfercmd(cmd, rest)

        while 1:
            buf = fp.read(blocksize)
            if not buf: break
            conn.sendall(buf)
            if callback: callback(buf)
        conn.close()
        return self.voidresp()



    def _uploadFiles(self, path, filelist):
        '''
        path: root directory of ftp
        filelist: the list of file in client
        '''
        self.d_cwd(path)
        for f in filelist:
            if f == '': continue
            if f[0] == '#': continue

            # uploader.py places in tools. To create the file descriptor
            # we need absolute filename.
            ab_filename = ROOT_PATH + '/' + f

            # SITE CHMOD uses owner/member/others permission
            # representation
            permission = os.stat(ab_filename)
            permission_chmod = oct(permission.st_mode)[3:]
            try:
                fd = open(ab_filename, 'rb')
            except IOError, err:
                # Is a directory error
                # Just create directory
                if err[0] == 21:
                    self.d_mkds(f)
                    self.voidcmd('SITE CHMOD ' + permission_chmod + ' ' + f)
                    continue
            try:
                self.storbinary('STOR %s' % f, fd)
            except error_perm, msg:
                if msg[0][:3] == '553':
                    dirname = f[:f.rfind('/')]
                    self.d_mkds(dirname)
                    self.storbinary('STOR %s' % f, fd)
            self.voidcmd('SITE CHMOD ' + permission_chmod + ' ' + f)
            fd.close()


    def exists(self, path):
        "Is there the path?"
        current = self.pwd()
        try: self.cwd(path)
        except error_perm: return False
        self.cwd(current)
        return True

        
    def _directoryInfo(self, filename):
        result = []
        while filename:
            p = filename.rfind('/')
            if p == -1: break
            result.append(p)
            filename = filename[:p]
        return result

    def _exists_level(self, filename, directory_info):
        "Return how many dead subdirectory from exist directory."
        level = 0
        for pointer in directory_info:
            dirname = filename[:pointer]
            if self.exists(dirname): return level
            level += 1

    def _directory_have_to_last_slash(self, dirname):
        if not dirname[-1] == '/':
            dirname = dirname + '/'
        return dirname

class UploadInfoCommon:
    '''
    >>> uic = UploadInfoCommon()

    >>> ### setFilesFromCommaSeparatedString
    >>> ####################################
    >>> sstring = "aa,bb,cc"
    >>> uic.setFilesFromCommaSeparatedString(sstring)
    >>> uic.files
    ['aa', 'bb', 'cc']
    '''
    def __init__(self):
        self.host = ""
        self.user = ""
        self.password = ""
        self.dir_to_be_installed = ""
        self.files_list_file = None
        self.files = None

    def setHost(self, host): self.host = host
    def setUser(self, user): self.user = user
    def setPassword(self, pwd): self.password = pwd
    def setFiles(self, files): self.files = files

    def setFilesFromListFile(self, listfile):
        self.files = self._getFileListFromListFile(listfile)

    def setFilesFromCommaSeparatedString(self, sstring):
        self.files = sstring.split(",")


    def get(self):
        pass

    @classmethod
    def _getFileListFromListFile(self, filename):
        '''
        We specify the names of files to be uploaded in the file. FILELIST
        is the file.
        '''
        results = []
        fd = open(filename, 'r')
        content = fd.read()
        fd.close()
        
        for path in content.split("\n"):
            # To support asterisk
            paths = recursive_glob2(path)
            results.extend(paths)
        return results


class UploadInfoFromInput(UploadInfoCommon):
    def get(self):
        example = \
            """
#Example
 Host: localhost
 User: ptmono
 Password: PASSWORD
 Directory: /home/myAccount/installDirectory
 File list: file_list_to_be_installed

"""
        sys.stdout.write(example)
        self.host = raw_input("Host: ")
        self.user = raw_input("User: ")
        self.passwd = getpass.getpass()
        self.dir_to_be_installed = raw_input("Install directory: ")
        self.files_list_file = raw_input("The file contains files list: ")
        if self.files_list_file == '':
            # TODO: comma separate input to be list
            self.files = raw_input("The list of file: ")
        else:
            self.files = self._getFileListFromListFile(self.files_list_file)
        
    def getHost(self): pass
    def getUserId(self): pass

    
class UploadInfoFromConfig(UploadInfoCommon):
    def get(self):
        self.host = config.server_host
        self.user = config.server_user_id
        self.passwd = config.server_passwd
        self.dir_to_be_installed = config.server_root_directory
        self.files = self._getFileListFromListFile(config.list_of_files_to_be_installed)
        # - install.py will create dbs/0000000001.html and dbs/index.json
        # - file permission will sync with the uploaded files.
        init_db()               # Init index.json


class UploadInfoDb(UploadInfoCommon):
    def get(self):
        self.host = config.server_host
        self.user = config.server_user_id
        self.passwd = config.server_passwd
        self.dir_to_be_installed = config.server_root_directory
        self.files = self.getDbFiles()

        # The html files contains css. We have to remove that to see on
        # web.
        self.prepare_htmls(config.htmls_d)
        return self.files

    @classmethod
    def getDocId(self, filename):
        match = re.match('.*([0-9]{10}).*', filename)
        return match.group(1)
            

    def getDbFiles(self):
        
        files = os.listdir(config.htmls_d)
        html_files = self._get_only_html_files(files, config.dbs_d)
        html_files.append(config.dbs_d + config.index_file)
        return html_files

    @classmethod
    def _get_only_html_files(self, files, prefix=None):
        result = []
        regex = config.html_extension + '$'
        
        for file in files:
            if re.search(regex, file):
                if prefix:
                    result.append(os.path.join(prefix,file))
                else:
                    result.append(file)
        return result

    @classmethod
    def prepare_htmls(self, path):
        """
        Our local htmls has their css to preview the content on the
        browser. It conflict the html on the server. The server require
        only body of html. This method will extract body of html and
        replace the content of the file on PATH.
        """

        abpath = os.path.abspath(path)
        files = os.listdir(abpath)
        html_files = self._get_only_html_files(files)

        html_files = [os.path.join(abpath, f) for f in html_files]

        from post import MuseArticle
        
        for abfn in html_files:
            body = MuseArticle.getHtmlBody(abfn)
            fd = open(abfn, 'w')
            try:
                print(len(body))                
                fd.write(body)
                fd.close()                
            except TypeError as err:
                # empty body
                print(abfn)
                fd.close()

        
class Uploader:
    '''
    >>> uploader = Uploader("kfsdjkf") #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    TypeError: 'str' object is not callable

    '''
    msg_upload_err = "We had bad attribute. We need correct host and file infomation."

    def __init__(self, upload_info_obj):
        try:
            self.upload_info = upload_info_obj()
            self.upload_info.get()
        except AttributeError, err:
            if isinstance(upload_info_obj, UploadInfoCommon):
                self.upload_info = upload_info_obj
                self.upload_info.get()
            else:
                raise AttributeError(err)

    def upload(self):
        ftp = UFTP(self.upload_info.host,
                   self.upload_info.user,
                   self.upload_info.passwd)
        ftp.upload(self.upload_info.dir_to_be_installed,
                   self.upload_info.files)


def uploadFile(filename):
    '''
    '''
    host = config.server_host
    user = config.server_user_id
    passwd = config.server_passwd
    dir_to_be_installed = config.server_root_directory
    uploader = UFTP(host, user, passwd)
    uploader.upload(dir_to_be_installed, filename)



def upload_with_config():
    uploader = Uploader(UploadInfoFromConfig)
    uploader.upload()

usage = \
'''
%s [option]

usage: options

  --with-config       : Use the configuration of config.py
  --syncdb            : upload posts and index.json into server
  -h, --help          : Shows this
'''


def main():
    try:
        opt = sys.argv[1]
        if opt == "--with-config":
            uploader = Uploader(UploadInfoFromConfig)
            uploader.upload()
        elif opt == "--syncdb":
            uploader = Uploader(UploadInfoDb)
            uploader.upload()
        else:
            print usage % ("uploader.py")
            
    except IndexError:
        uploader = Uploader(UploadInfoFromInput)
        uploader.upload()

if __name__ == "__main__":
    main()
