## Error 1

[Reference](https://stackoverflow.com/questions/56738345/could-not-install-packages-due-to-an-environmenterror-could-not-find-a-suitable)

You need to allow pip to reference to the correct certificate. check the certificate first;

> python -c "import certifi; print(certifi.where())"

Then first test it manually;

> pip install -r requirements.txt --cert=<the above certificate path>

If that works fine, then update this path on pip.conf file located at $HOME/.pip/pip.conf (or %APPDATA%\pip\pip.ini on Windows). e.g.

> [global]
> cert = /usr/local/share/ca-certificate/mycert.crt

## Error 2

[Reference](https://github.com/python/cpython/issues/108721)

Remove all duplicates and just keep 1 version of the TFS certificate.