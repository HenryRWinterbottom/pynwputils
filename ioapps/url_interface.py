"""
Module
------

    url_interface.py

Description
-----------

    This module contains functions to parse a Uniform Resource Locator
    (URL) paths.

Functions
---------

    get_contents(url, fail_nonread=False, fail_schema=False,
                timeout=10)

        This function attempts to collect the contents of a URL path
        `url` specified upon entry.

    get_weblist(url, ext=None, include_dirname=False)

        This function builds a list of files beneath the specified URL
        file path.

    read_webfile(url, ignore_missing=False, split=None, return_string=False)

        This function collects the contents of a specified URL path
        and returns a Python list containing the respective contents.

Requirements
------------

- bs4; https://www.crummy.com/software/BeautifulSoup/

- urllib; https://github.com/python/cpython/tree/3.10/Lib/urllib/

Author(s)
---------

    Henry R. Winterbottom; 02 December 2022

History
-------

    2022-12-02: Henry Winterbottom -- Initial implementation.

"""

# ----

# pylint: disable=broad-except

# ----

import os
import urllib.request
from typing import List, Union

import requests
from bs4 import BeautifulSoup
from requests.exceptions import MissingSchema
from utils.exceptions_interface import URLInterfaceError
from utils.logger_interface import Logger

# ----

# Define all available module properties.
__all__ = ["get_contents", "get_weblist", "read_webfile"]

# ----

logger = Logger(caller_name=__name__)

# ----


def get_contents(
    url: str, fail_nonread: bool = False, fail_schema: bool = False, timeout: int = 10
) -> Union[str, None]:
    """
    Description
    -----------

    This function attempts to collect the contents of a URL path `url`
    specified upon entry.

    Parameters
    ----------

    url: ``str``

        A Python string specifying the URL path contents to be
        collected.

    Keywords
    --------

    fail_nonread: ``bool``, optional

        A Python boolean valued variable specifying whether to fail
        when a URL path is non-readable and/or does not contain
        readable contents.

    fail_schema: ``bool``, optional

        A Python boolean valued variable specifying whether to fail if
        a MissingSchema exception is raised by the requests package.

    timeout: ``int``, optional

        A Python integer value specifying the duration period for
        which to allow the URL request to be valid.

    Returns
    -------

    data: ``Union[str, None]``

        A Python string containing the contents of the URL path `url`
        specified upon entry; if the contents are unable to be
        collected, and the keyword parameter arguments are specified
        accordingly, NoneType is returned.

    Raises
    ------

    URLInterfaceError:

        - raised if the URL path is non-readable and `fail_nonread` is
          `True` upon entry.

        - raised if the schema for the URL path could not be
          determined and `fail_schema` is `True` upon entry.

    """

    # Initialize the output string.
    contents = None

    # Parse the URL path and collect the contents of the respective
    # URL; proceed acccordingly.
    try:
        request = requests.get(url, stream=True, timeout=timeout)
        if "Content-Length" in request.headers:
            msg = f"Collecting contents from URL {url}."
            logger.info(msg=msg)
            url_req = urllib.request.Request(url)
            with urllib.request.urlopen(url_req) as url_resp:
                contents = url_resp.read().decode("utf-8")
        else:
            if fail_nonread:
                msg = f"The URL path {url} is a non-readable path. Aborting!!!"
                raise URLInterfaceError(msg=msg)

            if not fail_nonread:
                msg = f"The URL path {url} is a non-readable path; returning NoneType."
                logger.warn(msg=msg)
    except MissingSchema as exc:
        if fail_schema:
            msg = f"The schema for URL path {url} could not be determined. Aborting!!!"
            raise URLInterfaceError(msg=msg) from exc
        if not fail_schema:
            msg = (
                f"The schema for URL path {url} could not be determined; returning "
                "NoneType."
            )
            logger.warn(msg=msg)

    return contents


# ----


def get_weblist(url: str, ext: str = None, include_dirname: bool = False) -> List:
    """
    Description
    -----------

    This function builds a list of files beneath the specified URL
    file path.

    Parameters
    ----------

    url: ``str``

        A Python string specifying the path to the internet
        (world-wide web; WWW) file to be retrieved.

    Keywords
    --------

    ext: ``str``, optional

        A Python string specifying the web filename extension; if
        NoneType on entry the value defaults to to an empty string.

    include_dirname: ``bool``, optional

        A Python boolean valued variable specifying whether to append
        the URL path directory name to the retrieved file names; if
        `False` upon entry, the retrieved files will simply be the
        basename for the respective retrieved file names.

    Returns
    -------

    weblist: ``List``

        A Python list containing the files beneath the specified URL.

    Raises
    ------

    URLInterfaceError:

        - raised if an Exception is encountered while attempting to
          parse the URL path contents; the respective error message
          accompanys the message string passed to the URLError class.

    """

    # Collect the contents of the URL file path into memory and parse
    # the contents of the URL file path; proceed accordingly.
    try:
        request = urllib.request.Request(url=url)
        with urllib.request.urlopen(url=request) as response:
            url_contents = response.read()
        soup = BeautifulSoup(url_contents, "html.parser")
    except Exception as errmsg:
        msg = f"Retrieving the URL path {url} failed with error {errmsg}. Aborting!!!"
        raise URLInterfaceError(msg=msg) from errmsg

    # Compile a list of all URL file paths beneath the respective URL
    # file path provided upon entry; compile a list of the respective
    # files in accordance with the function attributes provided upon
    # entry; proceed accordingly.
    try:
        if ext is None:
            ext = str()
        webfiles = (
            node.get("href")
            for node in soup.find_all("a")
            if node.get("href").endswith(ext)
        )
        weblist = []
        for webfile in webfiles:
            if include_dirname:
                filename = os.path.join(os.path.dirname(url), webfile)
            if not include_dirname:
                filename = webfile
            weblist.append(filename)
    except Exception as errmsg:
        msg = (
            f"Compilation of URL paths beneath URL {url} failed with "
            f"error {errmsg}. Aborting!!!"
        )
        raise URLInterfaceError(msg=msg) from errmsg

    return weblist


# ----


def read_webfile(
    url: str,
    ignore_missing: bool = False,
    split: str = None,
    return_string: bool = False,
) -> List:
    """
    Description
    -----------

    This function collects the contents of a specified URL path and
    returns a Python list containing the respective contents.

    Parameters
    ----------

    url: ``str``

        A Python string specifying the path to the internet
        (world-wide web; WWW) file to be retrieved.

    Keywords
    --------

    ignore_missing: ``bool``, optional

        A Python boolean valued variable specifying whether to ignore
        URL path requests that raise `urllib.error.HTTPError`; if
        `True` upon entry the returned list (see below) will be an
        empty list.

    split: ``str``, optional

        A Python string specifying the string/characters to be used to
        split the contents of the respective file.

    return_string: ``bool``, optional

        A Python boolean valued variable specifying whether to return
        the contents of the URL path as a string; if `False` upon
        entry, the default format of the file (typically bytes) will
        be returned.

    Returns
    -------

    contents: ``List``

        A Python list containing the contents of the specified URL
        path.

    Raises
    ------

    URLInterfaceError:

        - raised if an exception is encountered while establishing the
          URL path request.

        - raised if the opening the specified URL path fails due to a
          missing endpoint; raised only if ignore_missing is `False`
          upon entry.

        - raised if an exception is encountered while parsing the
          contents of the URL file path specified upon entry.

    """

    # Establish a connection to the specified URL file path; proceed
    # accordingly.
    try:
        request = urllib.request.Request(url=url)
    except Exception as errmsg:
        msg = (
            f"Retrieving the URL path {url} failed with error {errmsg}. " "Aborting!!!"
        )
        raise URLInterfaceError(msg=msg) from errmsg

    # Read the contents of the URL file path; proceed accordingly.
    try:
        # Open the URL path and collect the contents of the file; the
        # contents will be returned as strings if return_string is
        # True upon entry; otherwise the default format of the file is
        # returned.
        contents = []
        try:
            with urllib.request.urlopen(url=request) as response:
                contents = response.read()
            if return_string:
                contents = str(contents)
            if split is not None:
                contents = str(contents).split(split)

        # If an urllib.error.HTTPError exception is raised (i.e., the
        # URL path does not exist), proceed in accordance with the
        # attributes provided upon entry.
        except urllib.error.HTTPError as url_error:
            if ignore_missing:
                msg = (
                    f"Opening URL {url} path failed with error {url_error}; "
                    "collection of URL path contents will not be "
                    "performed."
                )
                logger.warn(msg=msg)
            if not ignore_missing:
                msg = (
                    f"Opening URL path {url} failed with error {url_error}. "
                    "Aborting!!!"
                )
                raise URLInterfaceError(msg=msg) from errmsg
    except Exception as errmsg:
        msg = (
            f"Reading the contents of URL path {url} failed with error "
            f"{errmsg}. Aborting!!!"
        )
        raise URLInterfaceError(msg=msg) from errmsg

    return contents
