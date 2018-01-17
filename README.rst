thoth-pkgdeps
-------------

A tool to extract dependencies from a installation log.

This tool allows you to extract core information printed to standard output during installation of packages using tools like yum, dnf or pip.

A simple usage can be:

.. code-block:: console

  $ pip3 install --user flask | thoth-pkgdeps extract -i -
  [
    {
      "handler": "yum",
      "result": []
    },
    {
      "handler": "pip3",
      "result": [
        {
          "already_satisfied": null,
          "artifact": null,
          "from": null,
          "package": "flask",
          "version_installed": "0.12.2",
          "version_specified": null
        },
        {
          "already_satisfied": "/usr/lib/python3.6/site-packages",
          "from": [
            {
              "package": "flask",
              "version_specified": null
            }
          ],
          "package": "Jinja2",
          "version_installed": null,
          "version_specified": ">=2.4"
        },
        {
          "already_satisfied": "/usr/lib/python3.6/site-packages",
          "from": [
            {
              "package": "flask",
              "version_specified": null
            }
          ],
          "package": "itsdangerous",
          "version_installed": null,
          "version_specified": ">=0.21"
        },
        {
          "already_satisfied": "/usr/lib64/python3.6/site-packages",
          "from": [
            {
              "package": "flask",
              "version_specified": null
            }
          ],
          "package": "Werkzeug",
          "version_installed": null,
          "version_specified": ">=0.7"
        },
        {
          "already_satisfied": "/usr/lib/python3.6/site-packages",
          "from": [
            {
              "package": "flask",
              "version_specified": null
            }
          ],
          "package": "click",
          "version_installed": null,
          "version_specified": ">=2.0"
        },
        {
          "already_satisfied": "/usr/lib64/python3.6/site-packages",
          "from": [
            {
              "package": "Jinja2",
              "version_specified": ">=2.4"
            },
            {
              "package": "flask",
              "version_specified": null
            }
          ],
          "package": "MarkupSafe",
          "version_installed": null,
          "version_specified": ">=0.23"
        }
      ]
    }
  ]

Or you can also use this tool to extract information about packages that were installed during docker build:

.. code-block:: console

 $ docker build . | thoth-pkgdeps extract -i -
  [
    {
      "handler": "yum",
      "result": [
        {
          "arch": "x86_64",
          "dependency": false,
          "epoch": null,
          "name": "gcc",
          "repository": "updates",
          "size": "16M",
          "upgrading": false,
          "version": "4.8.5-16.el7_4.1"
        },
        {
          "arch": "x86_64",
          "dependency": true,
          "epoch": null,
          "name": "cpp",
          "repository": "updates",
          "size": "5.9M",
          "upgrading": false,
          "version": "4.8.5-16.el7_4.1"
        },
        {
          "arch": "x86_64",
          "dependency": true,
          "epoch": null,
          "name": "glibc-devel",
          "repository": "updates",
          "size": "1.1M",
          "upgrading": false,
          "version": "2.17-196.el7_4.2"
        },
        {
          "arch": "x86_64",
          "dependency": true,
          "epoch": null,
          "name": "glibc-headers",
          "repository": "updates",
          "size": "676k",
          "upgrading": false,
          "version": "2.17-196.el7_4.2"
        },
        {
          "arch": "x86_64",
          "dependency": true,
          "epoch": null,
          "name": "kernel-headers",
          "repository": "updates",
          "size": "6.0M",
          "upgrading": false,
          "version": "3.10.0-693.11.6.el7"
        },
        {
          "arch": "x86_64",
          "dependency": true,
          "epoch": null,
          "name": "libgomp",
          "repository": "updates",
          "size": "154k",
          "upgrading": false,
          "version": "4.8.5-16.el7_4.1"
        },
        {
          "arch": "x86_64",
          "dependency": true,
          "epoch": null,
          "name": "libmpc",
          "repository": "base",
          "size": "51k",
          "upgrading": false,
          "version": "1.0.1-3.el7"
        },
        {
          "arch": "x86_64",
          "dependency": true,
          "epoch": null,
          "name": "mpfr",
          "repository": "base",
          "size": "203k",
          "upgrading": false,
          "version": "3.1.1-4.el7"
        }
      ]
    },
    {
      "handler": "pip3",
      "result": []
    }
  ]