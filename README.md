# Common Helper Files

File and filesystem related helper functions incl.:

* Fail safe file operations: *They log errors but never throw an exception*
* Git version string generator
* Large file handling

## Known Issues
It seems that recent versions of setuptools can't handle a "." in the requirements list.
Therfore, [hurry.filesize](https://pypi.python.org/pypi/hurry.filesize) must be installed manually in advance.

```sh
$ sudo -EH pip3 install hurry.filesize
``` 

