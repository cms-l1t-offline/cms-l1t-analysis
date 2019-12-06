"""
Reproduce the standard glob package behaviour but use TSystem to be able to
query remote file systems such as xrootd
"""
from __future__ import print_function
from rootpy.ROOT import gSystem
import glob as gl
import os.path
import fnmatch
import sys
if sys.version_info[0] > 2:
    from urllib.parse import urlparse
else:
    from urlparse import urlparse

__all__ = ["glob", "iglob"]


def __directory_iter(directory):
    while True:
        try:
            file = gSystem.GetDirEntry(directory)
            if not file:
                break
            yield file
        except TypeError:
            break


def split_url(url):
    parsed_uri = urlparse(url)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    path = parsed_uri.path
    return domain, path


def glob(pathname):
    # Let normal python glob try first
    try_glob = gl.glob(pathname)
    if try_glob:
        return try_glob

    # If pathname does not contain a wildcard:
    if not gl.has_magic(pathname) and root_exists(pathname):
        return [pathname]

    # Else use ROOT's remote system querying
    return xrootd_glob(pathname)


def root_exists(pathname):
    # For some reason this method returns the opposite of what you'd expect
    # Also, dodgy function naming...
    return not gSystem.AccessPathName(pathname)


def root_glob(pathname):
    # Split the pathname into a directory and basename
    # (which should include the wild-card)
    dirs, basename = os.path.split(pathname)

    if gl.has_magic(dirs):
        dirs = root_glob(dirs)
    else:
        dirs = [dirs]

    files = []
    for dirname in dirs:
        # Uses `TSystem` to open the directory.
        # TSystem itself wraps up the calls needed to query xrootd.
        dirname = gSystem.ExpandPathName(dirname)
        directory = gSystem.OpenDirectory(dirname)

        if directory:
            for file in __directory_iter(directory):
                if file in [".", ".."]:
                    continue
                if not fnmatch.fnmatchcase(file, basename):
                    continue
                files.append(os.path.join(dirname, file))
            try:
                gSystem.FreeDirectory(directory)
            except TypeError:
                pass
    return files


def xrootd_glob(pathname):
    from pyxrootd.client import FileSystem
    # Split the pathname into a directory and basename
    dirs, basename = os.path.split(pathname)

    if gl.has_magic(dirs):
        dirs = xrootd_glob(dirs)
    else:
        dirs = [dirs]

    files = []
    for dirname in dirs:
        host, path = split_url(dirname)
        query = FileSystem(host)

        if not query:
            raise RuntimeError("Cannot prepare xrootd query")

        _, dirlist = query.dirlist(path)
        for entry in dirlist["dirlist"]:
            filename = entry["name"]
            if filename in [".", ".."]:
                continue
            if not fnmatch.fnmatchcase(filename, basename):
                continue
            files.append(os.path.join(dirname, filename))

    return files


def iglob(pathname):
    for name in glob(pathname):
        yield name


if __name__ == "__main__":
    test_paths = [
        "data/*root",
        "data/L1Ntuple_test_3.root",
        "d*/*root",
        "root://eoscms.cern.ch//eos/cms/store/group/dpg_trigger/"
        "comm_trigger/L1Trigger/L1Menu2016/Stage2/"
        "l1t-integration-v88p1-CMSSW-8021/SingleMuon/"
        "crab_l1t-integration-v88p1-CMSSW-8021__SingleMuon_2016H_v2/"
        "161031_120512/0000/L1Ntuple_999.root",
        "root://eoscms.cern.ch//eos/cms/store/group/dpg_trigger/"
        "comm_trigger/L1Trigger/L1Menu2016/Stage2/"
        "l1t-integration-v88p1-CMSSW-8021/SingleMuon/"
        "crab_l1t-integration-v88p1-CMSSW-8021__SingleMuon_2016H_v2/"
        "161031_120512/0000/L1Ntuple_99*.root",
        "root://eoscms.cern.ch//eos/cms/store/group/dpg_trigger/"
        "comm_trigger/L1Trigger/L1Menu2016/Stage2/"
        "l1t-integration-v88p1-CMSSW-8021/SingleMuon/"
        "crab_l1t-integration-v88p1-CMSSW-8021__SingleMuon_2016H_v2/"
        "161031_120512/000*/L1Ntuple_99*.root",
    ]
    for i, path in enumerate(test_paths):
        expanded = glob(path)
        print(i, path)
        print(i, expanded, len(expanded))
