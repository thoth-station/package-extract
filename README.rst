Thoth Package Extract
---------------------

A tool to extract dependencies from an image and image build logs.

Extracting installed packages from install logs
===============================================

You can use this tool to get information about installed packages from install logs. Currently, there is supported parsing of install logs from ``pip``, ``pip3``, ``dnf`` and ``yum`` output. The tool automatically detects based on the output which package manager was used and provides a structured output of installed packages.

.. warning::

  Tools ``dnf`` and ``yum`` suppress output of already installed dependencies. This means that already satisfied dependencies do not occur in the resulting JSON.

.. warning::

  When installing packages using ``pip`` (or ``pip3``) the package manager reports already satisfied dependencies but does not report version information. Thus the version information is not available in these cases in the resulting output.

It's completely fine to use install log extraction for docker build logs. Note however that the already installed packages in the base image will be missing in the output.

Extracting dependencies directly from an image
==============================================

Tool thoth-package-extract allows you to extract dependencies from an image directly by inspecting its content. As there is directly inspected the content of image, the output is accurate compared to the pure build log parsing.

To gather information about python packages installed, there is a need to execute python scripts of installed packages given the Python packaging design. In some cases this can be dangerous as there could be executed potentially malicious parts of code (see `this typo squashing <http://www.nbu.gov.sk/skcsirt-sa-20170909-pypi/>`_ as an example).


Installation
============

Use prepared Dockerfile:

.. code-block:: console

  git clone https://github.com/thoth-station/package-extract
  cd package-extract
  docker build . -t package-extract


Example of parsing install logs
===============================

An example of parsing installed packages during:

.. code-block:: console

  $ pip3 install --user flask | docker run -i package-extract extract-buildlog -i -

  {
    "metadata": {
      "analyzer": "thoth-package-extract",
      "analyzer_version": "1.0.0",
      "arguments": {
        "extract-buildlog": {
          "input_file": "<_io.TextIOWrapper name='<stdin>' mode='r' encoding='UTF-8'>",
          "no_pretty": false,
          "output": null
        },
        "thoth-package-extract": {
          "no_color": false,
          "verbose": false
        }
      },
      "datetime": "2018-06-18T15:53:23.129270",
      "distribution": {
        "codename": "Twenty Seven",
        "id": "fedora",
        "like": "",
        "version": "27",
        "version_parts": {
          "build_number": "",
          "major": "27",
          "minor": ""
        }
      },
      "hostname": "268f19027ea4",
      "python": {
        "api_version": 1013,
        "implementation_name": "cpython",
        "major": 3,
        "micro": 5,
        "minor": 6,
        "releaselevel": "final",
        "serial": 0
      }
    },
    "result": [
      {
        "handler": "yum",
        "result": []
      },
      {
        "handler": "pip3",
        "result": [
          {
            "already_satisfied": "/usr/lib/python3.6/site-packages/click-6.6-py3.6.egg",
            "from": [
              {
                "package": "flask",
                "version_specified": null
              }
            ],
            "package": "click",
            "version_installed": null,
            "version_specified": ">=5.1"
          },
          {
            "already_satisfied": null,
            "artifact": {
              "name": "https://files.pythonhosted.org/packages/7f/ff/ae64bacdfc95f27a016a7bed8e8686763ba4d277a78ca76f32659220a731/Jinja2-2.10-py2.py3-none-any.whl",
              "size": "126kB"
            },
            "from": [
              {
                "package": "flask",
                "version_specified": null
              }
            ],
            "package": "Jinja2",
            "version_installed": "2.10",
            "version_specified": ">=2.10"
          },
          {
            "already_satisfied": null,
            "artifact": {
              "name": "https://files.pythonhosted.org/packages/20/c4/12e3e56473e52375aa29c4764e70d1b8f3efa6682bef8d0aae04fe335243/Werkzeug-0.14.1-py2.py3-none-any.whl",
              "size": "322kB"
            },
            "from": [
              {
                "package": "flask",
                "version_specified": null
              }
            ],
            "package": "Werkzeug",
            "version_installed": "0.14.1",
            "version_specified": ">=0.14"
          },
          {
            "already_satisfied": "/home/fpokorny/.local/lib/python3.6/site-packages",
            "from": [
              {
                "package": "flask",
                "version_specified": null
              }
            ],
            "package": "itsdangerous",
            "version_installed": null,
            "version_specified": ">=0.24"
          },
          {
            "already_satisfied": "/home/fpokorny/.local/lib/python3.6/site-packages",
            "from": [
              {
                "package": "Jinja2",
                "version_specified": ">=2.10"
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
  }

Or you can also use this tool to extract information about packages that were installed during docker build:

.. code-block:: console

  $ docker build . -f Dockerfile.test --no-cache | docker run -i package-extract extract-buildlog -i -
  {
    "metadata": {
      "analyzer": "thoth-package-extract",
      "analyzer_version": "1.0.0",
      "arguments": {
        "extract-buildlog": {
          "input_file": "<_io.TextIOWrapper name='<stdin>' mode='r' encoding='UTF-8'>",
          "no_pretty": false,
          "output": null
        },
        "thoth-package-extract": {
          "no_color": false,
          "verbose": false
        }
      },
      "datetime": "2018-06-18T18:08:47.259811",
      "distribution": {
        "codename": "Twenty Seven",
        "id": "fedora",
        "like": "",
        "version": "27",
        "version_parts": {
          "build_number": "",
          "major": "27",
          "minor": ""
        }
      },
      "hostname": "b8c6f33cf757",
      "python": {
        "api_version": 1013,
        "implementation_name": "cpython",
        "major": 3,
        "micro": 5,
        "minor": 6,
        "releaselevel": "final",
        "serial": 0
      }
    },
    "result": [
      {
        "handler": "yum",
        "result": [
          {
            "arch": "noarch",
            "dependency": false,
            "epoch": null,
            "name": "ca-certificates",
            "repository": "updates",
            "size": "392k",
            "upgrading": true,
            "version": "2018.2.24-1.0.fc28"
          },
          {
            "arch": "x86_64",
            "dependency": false,
            "epoch": null,
            "name": "coreutils-single",
            "repository": "updates",
            "size": "623k",
            "upgrading": true,
            "version": "8.29-7.fc28"
          },
          {
            "arch": "noarch",
            "dependency": false,
            "epoch": null,
            "name": "crypto-policies",
            "repository": "updates",
            "size": "40k",
            "upgrading": true,
            "version": "20180425-5.git6ad4018.fc28"
          },
          {
            "arch": "x86_64",
            "dependency": false,
            "epoch": null,
            "name": "cryptsetup-libs",
            "repository": "updates",
            "size": "291k",
            "upgrading": true,
            "version": "2.0.3-4.fc28"
          },
          {
            "arch": "x86_64",
            "dependency": false,
            "epoch": null,
            "name": "curl",
            "repository": "updates",
            "size": "343k",
            "upgrading": true,
            "version": "7.59.0-4.fc28"
          },
          {
            "arch": "x86_64",
            "dependency": false,
            "epoch": null,
            "name": "cyrus-sasl-lib",
            "repository": "updates",
            "size": "114k",
            "upgrading": true,
            "version": "2.1.27-0.2rc7.fc28"
          },
  ...
          {
            "arch": "x86_64",
            "dependency": false,
            "epoch": 2,
            "name": "vim-enhanced",
            "repository": "updates",
            "size": "1.4M",
            "upgrading": false,
            "version": "8.1.042-1.fc28"
          },
          {
            "arch": "x86_64",
            "dependency": true,
            "epoch": null,
            "name": "gpm-libs",
            "repository": "fedora",
            "size": "38k",
            "upgrading": false,
            "version": "1.20.7-15.fc28"
          },
          {
            "arch": "x86_64",
            "dependency": true,
            "epoch": 2,
            "name": "vim-common",
            "repository": "updates",
            "size": "6.4M",
            "upgrading": false,
            "version": "8.1.042-1.fc28"
          },
          {
            "arch": "noarch",
            "dependency": true,
            "epoch": 2,
            "name": "vim-filesystem",
            "repository": "updates",
            "size": "47k",
            "upgrading": false,
            "version": "8.1.042-1.fc28"
          },
          {
            "arch": "x86_64",
            "dependency": true,
            "epoch": null,
            "name": "which",
            "repository": "fedora",
            "size": "47k",
            "upgrading": false,
            "version": "2.21-8.fc28"
          }
        ]
      },
      {
        "handler": "pip3",
        "result": [
          {
            "already_satisfied": null,
            "artifact": {
              "name": "https://files.pythonhosted.org/packages/7f/e7/08578774ed4536d3242b14dacb4696386634607af824ea997202cd0edb4b/Flask-1.0.2-py2.py3-none-any.whl",
              "size": "91kB"
            },
            "from": null,
            "package": "flask",
            "version_installed": "1.0.2",
            "version_specified": null
          },
          {
            "already_satisfied": null,
            "artifact": {
              "name": "https://files.pythonhosted.org/packages/7f/ff/ae64bacdfc95f27a016a7bed8e8686763ba4d277a78ca76f32659220a731/Jinja2-2.10-py2.py3-none-any.whl",
              "size": "126kB"
            },
            "from": [
              {
                "package": "flask",
                "version_specified": null
              }
            ],
            "package": "Jinja2",
            "version_installed": "2.10",
            "version_specified": ">=2.10"
          },
          {
            "already_satisfied": null,
            "artifact": {
              "name": "https://files.pythonhosted.org/packages/20/c4/12e3e56473e52375aa29c4764e70d1b8f3efa6682bef8d0aae04fe335243/Werkzeug-0.14.1-py2.py3-none-any.whl",
              "size": "322kB"
            },
            "from": [
              {
                "package": "flask",
                "version_specified": null
              }
            ],
            "package": "Werkzeug",
            "version_installed": "0.14.1",
            "version_specified": ">=0.14"
          },
          {
            "already_satisfied": null,
            "artifact": {
              "name": "https://files.pythonhosted.org/packages/dc/b4/a60bcdba945c00f6d608d8975131ab3f25b22f2bcfe1dab221165194b2d4/itsdangerous-0.24.tar.gz",
              "size": "46kB"
            },
            "from": [
              {
                "package": "flask",
                "version_specified": null
              }
            ],
            "package": "itsdangerous",
            "version_installed": "0.24",
            "version_specified": ">=0.24"
          },
          {
            "already_satisfied": null,
            "artifact": {
              "name": "https://files.pythonhosted.org/packages/34/c1/8806f99713ddb993c5366c362b2f908f18269f8d792aff1abfd700775a77/click-6.7-py2.py3-none-any.whl",
              "size": "71kB"
            },
            "from": [
              {
                "package": "flask",
                "version_specified": null
              }
            ],
            "package": "click",
            "version_installed": "6.7",
            "version_specified": ">=5.1"
          },
          {
            "already_satisfied": null,
            "artifact": {
              "name": "https://files.pythonhosted.org/packages/4d/de/32d741db316d8fdb7680822dd37001ef7a448255de9699ab4bfcbdf4172b/MarkupSafe-1.0.tar.gz",
              "size": null
            },
            "from": [
              {
                "package": "Jinja2",
                "version_specified": ">=2.10"
              },
              {
                "package": "flask",
                "version_specified": null
              }
            ],
            "package": "MarkupSafe",
            "version_installed": "1.0",
            "version_specified": ">=0.23"
          }
        ]
      }
    ]
  }

  $ cat Dockerfile.test
  FROM fedora:28
  RUN dnf install python3-pip && pip3 install flask && dnf update -y && dnf install -y vim


Example of extracting installed packages inside an image
========================================================

To extract packages present on the resulting image run:

.. code-block:: console

  $ docker run -i package-extract -v extract-image -i fedora:27
  2018-06-18 19:06:46,611 [1] DEBUG    thoth.package_extract.image: Downloading image 'fedora:27'
  2018-06-18 19:06:46,611 [1] DEBUG    thoth.analyzer.command: Running command 'skopeo copy docker://fedora:27 dir://tmp/tmp9jmeuw__'
  2018-06-18 19:06:51,669 [1] DEBUG    thoth.package_extract.image: skopeo stdout: Getting image source signatures
  Copying blob sha256:2176639d844bbe1386912e1d9952cebdb8249923a16691025cf693963f8aec53
  
   0 B / 77.54 MB 
   3.60 MB / 77.54 MB 
   9.65 MB / 77.54 MB 
   16.34 MB / 77.54 MB 
   22.86 MB / 77.54 MB 
   29.22 MB / 77.54 MB 
   35.59 MB / 77.54 MB 
   41.26 MB / 77.54 MB 
   47.86 MB / 77.54 MB 
   54.40 MB / 77.54 MB 
   61.01 MB / 77.54 MB 
   66.34 MB / 77.54 MB 
   72.99 MB / 77.54 MB 
   77.54 MB / 77.54 MB 
   77.54 MB / 77.54 MB  2s
  Copying config sha256:9110ae7f579f35ee0c3938696f23fe0f5fbe641738ea52eb83c2df7e9995fa17
  
   0 B / 2.29 KB 
   2.29 KB / 2.29 KB  0s
  Writing manifest to image destination
  Storing signatures
  
  2018-06-18 19:06:51,671 [1] DEBUG    thoth.package_extract.image: Layers found: [{'mediaType': 'application/vnd.docker.image.rootfs.diff.tar.gzip', 'size': 81308994, 'digest': 'sha256:2176639d844bbe1386912e1d9952cebdb8249923a16691025cf693963f8aec53'}]
  2018-06-18 19:06:51,671 [1] DEBUG    thoth.package_extract.image: Extracting layer '2176639d844bbe1386912e1d9952cebdb8249923a16691025cf693963f8aec53'
  2018-06-18 19:06:55,444 [1] DEBUG    thoth.analyzer.command: Running command 'mercator -config /usr/share/mercator/handlers.yml /tmp/tmp9jmeuw__/rootfs'
  2018-06-18 19:06:55,776 [1] DEBUG    thoth.analyzer.command: Running command "rpm -qa --root '/tmp/tmp9jmeuw__/rootfs'"
  2018-06-18 19:06:55,874 [1] DEBUG    thoth.analyzer.command: Running command "repoquery --deplist --installed --installroot '/tmp/tmp9jmeuw__/rootfs'"
  {
  "metadata": {
    "analyzer": "thoth-package-extract",
    "analyzer_version": "1.0.0",
    "arguments": {
      "extract-image": {
        "image": "fedora:27",
        "no_pretty": false,
        "no_tls_verify": false,
        "output": null,
        "registry_credentials": null,
        "timeout": null
      },
      "thoth-package-extract": {
        "no_color": false,
        "verbose": false
      }
    },
    "datetime": "2018-06-18T19:05:33.205504",
    "distribution": {
      "codename": "Twenty Seven",
      "id": "fedora",
      "like": "",
      "version": "27",
      "version_parts": {
        "build_number": "",
        "major": "27",
        "minor": ""
      }
    },
    "hostname": "bfd10ad99fd4",
    "python": {
      "api_version": 1013,
      "implementation_name": "cpython",
      "major": 3,
      "micro": 5,
      "minor": 6,
      "releaselevel": "final",
      "serial": 0
    }
  },
  "result": {
    "layers": [
      "2176639d844bbe1386912e1d9952cebdb8249923a16691025cf693963f8aec53"
    ],
    "mercator": [
      {
        "digests": {
          "manifest": "10460bb1fe6c167f6ef25f56cf940fab6fb40dd1"
        },
        "ecosystem": "Python-Dist",
        "path": "/usr/lib/python3.6/site-packages/iniparse-0.4-py3.6.egg-info/PKG-INFO",
        "result": {
          "author": "Paramjit Oberoi",
          "author-email": "param@cs.wisc.edu",
          "classifier": "Development Status :: 5 - Production/Stable\nIntended Audience :: Developers\nLicense :: OSI Approved :: MIT License\nLicense :: OSI Approved :: Python Software Foundation License\nOperating System :: OS Independent\nProgramming Language :: Python\nProgramming Language :: Python :: 2Programming Language :: Python :: 2.6\nProgramming Language :: Python :: 2.7\nProgramming Language :: Python :: 3\nProgramming Language :: Python :: 3.3\nProgramming Language :: Python :: 3.4Topic :: Software Development :: Libraries :: Python Modules",
          "description": "iniparse is an INI parser for  Python which is API compatible\nwith the standard library's ConfigParser, preserves structure of INI\nfiles (order of sections & options, indentation, comments, and blank\nlines are preserved when data is updated), and is more convenient to\nuse.",
          "home-page": "http://code.google.com/p/iniparse/",
          "license": "MIT",
          "name": "iniparse",
          "platform": "UNKNOWN",
          "summary": "Accessing and Modifying INI files",
          "version": "0.4"
        }
      },
      {
        "digests": {
          "manifest": "638db309ccb9ca512fc1c7c9ac207028038b8d5c"
        },
        "ecosystem": "Python-Dist",
        "path": "/usr/lib/python3.6/site-packages/pip-9.0.1.dist-info/metadata.json",
        "result": {
          "classifiers": [
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Topic :: Software Development :: Build Tools",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 2.6",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.3",
            "Programming Language :: Python :: 3.4",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: Implementation :: PyPy"
          ],
          "extensions": {
            "python.commands": {
              "wrap_console": {
                "pip": "pip:main",
                "pip3": "pip:main",
                "pip3.6": "pip:main"
              }
            },
            "python.details": {
              "contacts": [
                {
                  "email": "python-virtualenv@groups.google.com",
                  "name": "The pip developers",
                  "role": "author"
                }
              ],
              "document_names": {
                "description": "DESCRIPTION.rst"
              },
              "project_urls": {
                "Home": "https://pip.pypa.io/"
              }
            },
            "python.exports": {
              "console_scripts": {
                "pip": "pip:main",
                "pip3": "pip:main",
                "pip3.6": "pip:main"
              }
            }
          },
          "extras": [
            "testing"
          ],
          "generator": "bdist_wheel (0.30.0.a0)",
          "keywords": [
            "easy_install",
            "distutils",
            "setuptools",
            "egg",
            "virtualenv"
          ],
          "license": "MIT",
          "metadata_version": "2.0",
          "name": "pip",
          "requires_python": ">=2.6,!=3.0.*,!=3.1.*,!=3.2.*",
          "run_requires": [
            {
              "extra": "testing",
              "requires": [
                "mock",
                "pretend",
                "pytest",
                "scripttest (>=1.3)",
                "virtualenv (>=1.10)"
              ]
            }
          ],
          "summary": "The PyPA recommended tool for installing Python packages.",
          "test_requires": [
            {
              "requires": [
                "mock",
                "pretend",
                "pytest",
                "scripttest (>=1.3)",
                "virtualenv (>=1.10)"
              ]
            }
          ],
          "version": "9.0.1"
        }
      },
      {
        "digests": {
          "manifest": "17b684b084a699aac2d70e4ceb03ac69b652b493"
        },
        "ecosystem": "Python-Dist",
        "path": "/usr/lib/python3.6/site-packages/setuptools-37.0.0.dist-info/metadata.json",
        "result": {
          "classifiers": [
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.3",
            "Programming Language :: Python :: 3.4",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: System :: Archiving :: Packaging",
            "Topic :: System :: Systems Administration",
            "Topic :: Utilities"
          ],
          "description_content_type": "text/x-rst; charset=UTF-8",
          "extensions": {
            "python.commands": {
              "wrap_console": {
                "easy_install": "setuptools.command.easy_install:main",
                "easy_install-3.6": "setuptools.command.easy_install:main"
              }
            },
            "python.details": {
              "contacts": [
                {
                  "email": "distutils-sig@python.org",
                  "name": "Python Packaging Authority",
                  "role": "author"
                }
              ],
              "document_names": {
                "description": "DESCRIPTION.rst",
                "license": "LICENSE.txt"
              },
              "project_urls": {
                "Home": "https://github.com/pypa/setuptools"
              }
            },
            "python.exports": {
              "console_scripts": {
                "easy_install": "setuptools.command.easy_install:main",
                "easy_install-3.6": "setuptools.command.easy_install:main"
              },
              "distutils.commands": {
                "alias": "setuptools.command.alias:alias",
                "bdist_egg": "setuptools.command.bdist_egg:bdist_egg",
                "bdist_rpm": "setuptools.command.bdist_rpm:bdist_rpm",
                "bdist_wininst": "setuptools.command.bdist_wininst:bdist_wininst",
                "build_clib": "setuptools.command.build_clib:build_clib",
                "build_ext": "setuptools.command.build_ext:build_ext",
                "build_py": "setuptools.command.build_py:build_py",
                "develop": "setuptools.command.develop:develop",
                "dist_info": "setuptools.command.dist_info:dist_info",
                "easy_install": "setuptools.command.easy_install:easy_install",
                "egg_info": "setuptools.command.egg_info:egg_info",
                "install": "setuptools.command.install:install",
                "install_egg_info": "setuptools.command.install_egg_info:install_egg_info",
                "install_lib": "setuptools.command.install_lib:install_lib",
                "install_scripts": "setuptools.command.install_scripts:install_scripts",
                "register": "setuptools.command.register:register",
                "rotate": "setuptools.command.rotate:rotate",
                "saveopts": "setuptools.command.saveopts:saveopts",
                "sdist": "setuptools.command.sdist:sdist",
                "setopt": "setuptools.command.setopt:setopt",
                "test": "setuptools.command.test:test",
                "upload": "setuptools.command.upload:upload",
                "upload_docs": "setuptools.command.upload_docs:upload_docs"
              },
              "distutils.setup_keywords": {
                "convert_2to3_doctests": "setuptools.dist:assert_string_list",
                "dependency_links": "setuptools.dist:assert_string_list",
                "eager_resources": "setuptools.dist:assert_string_list",
                "entry_points": "setuptools.dist:check_entry_points",
                "exclude_package_data": "setuptools.dist:check_package_data",
                "extras_require": "setuptools.dist:check_extras",
                "include_package_data": "setuptools.dist:assert_bool",
                "install_requires": "setuptools.dist:check_requirements",
                "namespace_packages": "setuptools.dist:check_nsp",
                "package_data": "setuptools.dist:check_package_data",
                "packages": "setuptools.dist:check_packages",
                "python_requires": "setuptools.dist:check_specifier",
                "setup_requires": "setuptools.dist:check_requirements",
                "test_loader": "setuptools.dist:check_importable",
                "test_runner": "setuptools.dist:check_importable",
                "test_suite": "setuptools.dist:check_test_suite",
                "tests_require": "setuptools.dist:check_requirements",
                "use_2to3": "setuptools.dist:assert_bool",
                "use_2to3_exclude_fixers": "setuptools.dist:assert_string_list",
                "use_2to3_fixers": "setuptools.dist:assert_string_list",
                "zip_safe": "setuptools.dist:assert_bool"
              },
              "egg_info.writers": {
                "PKG-INFO": "setuptools.command.egg_info:write_pkg_info",
                "dependency_links.txt": "setuptools.command.egg_info:overwrite_arg",
                "depends.txt": "setuptools.command.egg_info:warn_depends_obsolete",
                "eager_resources.txt": "setuptools.command.egg_info:overwrite_arg",
                "entry_points.txt": "setuptools.command.egg_info:write_entries",
                "namespace_packages.txt": "setuptools.command.egg_info:overwrite_arg",
                "requires.txt": "setuptools.command.egg_info:write_requirements",
                "top_level.txt": "setuptools.command.egg_info:write_toplevel_names"
              },
              "setuptools.installation": {
                "eggsecutable": "setuptools.command.easy_install:bootstrap"
              }
            }
          },
          "extras": [
            "certs",
            "ssl"
          ],
          "generator": "bdist_wheel (0.30.0.a0)",
          "keywords": [
            "CPAN",
            "PyPI",
            "distutils",
            "eggs",
            "package",
            "management"
          ],
          "metadata_version": "2.0",
          "name": "setuptools",
          "requires_python": ">=2.7,!=3.0.*,!=3.1.*,!=3.2.*",
          "run_requires": [
            {
              "extra": "certs",
              "requires": [
                "certifi (==2016.9.26)"
              ]
            },
            {
              "environment": "sys_platform=='win32'",
              "extra": "ssl",
              "requires": [
                "wincertstore (==0.2)"
              ]
            }
          ],
          "summary": "Easily download, build, install, upgrade, and uninstall Python packages",
          "version": "37.0.0"
        }
      },
      {
        "digests": {
          "manifest": "1153f208db7328880763cf52bdcf940baf221071"
        },
        "ecosystem": "Python-Dist",
        "path": "/usr/lib/python3.6/site-packages/six-1.11.0.dist-info/metadata.json",
        "result": {
          "classifiers": [
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Topic :: Software Development :: Libraries",
            "Topic :: Utilities"
          ],
          "extensions": {
            "python.details": {
              "contacts": [
                {
                  "email": "benjamin@python.org",
                  "name": "Benjamin Peterson",
                  "role": "author"
                }
              ],
              "document_names": {
                "description": "DESCRIPTION.rst"
              },
              "project_urls": {
                "Home": "http://pypi.python.org/pypi/six/"
              }
            }
          },
          "generator": "bdist_wheel (0.30.0.a0)",
          "license": "MIT",
          "metadata_version": "2.0",
          "name": "six",
          "summary": "Python 2 and 3 compatibility utilities",
          "test_requires": [
            {
              "requires": [
                "pytest"
              ]
            }
          ],
          "version": "1.11.0"
        }
      }
    ],
    "rpm": [
      "xkeyboard-config-2.22-1.fc27.noarch",
      "emacs-filesystem-25.3-3.fc27.noarch",
      "fedora-repos-27-2.noarch",
      "setup-2.10.10-1.fc27.noarch",
      "basesystem-11-4.fc27.noarch",
      "libreport-filesystem-2.9.3-2.fc27.x86_64",
      "tzdata-2018c-1.fc27.noarch",
      "glibc-langpack-en-2.26-26.fc27.x86_64",
      "ncurses-libs-6.0-13.20170722.fc27.x86_64",
      "libsepol-2.7-2.fc27.x86_64",
      "libselinux-2.7-3.fc27.x86_64",
      "info-6.4-6.fc27.x86_64",
      "bzip2-libs-1.0.6-24.fc27.x86_64",
      "expat-2.2.5-1.fc27.x86_64",
      "nspr-4.18.0-1.fc27.x86_64",
      "elfutils-libelf-0.170-1.fc27.x86_64",
      "libgcrypt-1.8.2-1.fc27.x86_64",
      "libxml2-2.9.7-1.fc27.x86_64",
      "gmp-6.1.2-6.fc27.x86_64",
      "libzstd-1.3.3-1.fc27.x86_64",
      "chkconfig-1.10-3.fc27.x86_64",
      "libcom_err-1.43.5-2.fc27.x86_64",
      "libattr-2.4.47-21.fc27.x86_64",
      "sed-4.4-4.fc27.x86_64",
      "libunistring-0.9.7-3.fc27.x86_64",
      "lz4-libs-1.8.0-1.fc27.x86_64",
      "libcap-ng-0.7.8-5.fc27.x86_64",
      "nss-softokn-freebl-3.35.0-1.0.fc27.x86_64",
      "nss-softokn-3.35.0-1.0.fc27.x86_64",
      "keyutils-libs-1.5.10-3.fc27.x86_64",
      "grep-3.1-3.fc27.x86_64",
      "dbus-libs-1.12.0-1.fc27.x86_64",
      "p11-kit-trust-0.23.9-2.fc27.x86_64",
      "libusbx-1.0.21-4.fc27.x86_64",
      "libpsl-0.18.0-1.fc27.x86_64",
      "mpfr-3.1.6-1.fc27.x86_64",
      "gdbm-1.13-6.fc27.x86_64",
      "libdb-utils-5.3.28-27.fc27.x86_64",
      "kmod-libs-25-1.fc27.x86_64",
      "coreutils-common-8.27-20.fc27.x86_64",
      "elfutils-default-yama-scope-0.170-1.fc27.noarch",
      "ncurses-6.0-13.20170722.fc27.x86_64",
      "coreutils-8.27-20.fc27.x86_64",
      "python3-pip-9.0.1-14.fc27.noarch",
      "python3-3.6.4-8.fc27.x86_64",
      "libblkid-2.30.2-1.fc27.x86_64",
      "libmount-2.30.2-1.fc27.x86_64",
      "dbus-glib-0.108-4.fc27.x86_64",
      "libutempter-1.1.6-11.fc27.x86_64",
      "python3-libcomps-0.1.8-6.fc27.x86_64",
      "python3-iniparse-0.4-26.fc27.noarch",
      "gzip-1.8-4.fc27.x86_64",
      "libpwquality-1.4.0-3.fc27.x86_64",
      "nss-pem-1.0.3-6.fc27.x86_64",
      "nss-sysinit-3.35.0-1.1.fc27.x86_64",
      "libarchive-3.3.1-3.fc27.x86_64",
      "trousers-lib-0.3.13-9.fc27.x86_64",
      "libsss_nss_idmap-1.16.0-6.fc27.x86_64",
      "libsigsegv-2.11-3.fc27.x86_64",
      "krb5-libs-1.15.2-7.fc27.x86_64",
      "openldap-2.4.45-4.fc27.x86_64",
      "qrencode-libs-3.4.4-3.fc27.x86_64",
      "gnupg2-2.2.5-1.fc27.x86_64",
      "python3-gpg-1.9.0-6.fc27.x86_64",
      "util-linux-2.30.2-1.fc27.x86_64",
      "iptables-libs-1.6.1-4.fc27.x86_64",
      "device-mapper-libs-1.02.144-1.fc27.x86_64",
      "systemd-pam-234-10.git5f8984e.fc27.x86_64",
      "dbus-1.12.0-1.fc27.x86_64",
      "libcurl-7.55.1-9.fc27.x86_64",
      "python3-librepo-1.8.0-1.fc27.x86_64",
      "rpm-plugin-selinux-4.14.1-1.fc27.x86_64",
      "rpm-4.14.1-1.fc27.x86_64",
      "libdnf-0.11.1-1.fc27.x86_64",
      "deltarpm-3.6-24.fc27.x86_64",
      "python3-rpm-4.14.1-1.fc27.x86_64",
      "dnf-2.7.5-2.fc27.noarch",
      "rpm-plugin-systemd-inhibit-4.14.1-1.fc27.x86_64",
      "gnupg2-smime-2.2.5-1.fc27.x86_64",
      "nss-tools-3.35.0-1.1.fc27.x86_64",
      "pinentry-0.9.7-4.fc27.x86_64",
      "shared-mime-info-1.9-1.fc27.x86_64",
      "tar-1.29-7.fc27.x86_64",
      "libxkbcommon-0.7.1-5.fc27.x86_64",
      "rootfiles-8.1-21.fc27.noarch",
      "libgcc-7.3.1-5.fc27.x86_64",
      "publicsuffix-list-dafsa-20180223-1.fc27.noarch",
      "fedora-gpg-keys-27-2.noarch",
      "fedora-release-27-1.noarch",
      "filesystem-3.3-3.fc27.x86_64",
      "ncurses-base-6.0-13.20170722.fc27.noarch",
      "dnf-conf-2.7.5-2.fc27.noarch",
      "glibc-common-2.26-26.fc27.x86_64",
      "glibc-2.26-26.fc27.x86_64",
      "bash-4.4.19-1.fc27.x86_64",
      "pcre2-10.31-1.fc27.x86_64",
      "zlib-1.2.11-4.fc27.x86_64",
      "xz-libs-5.2.3-4.fc27.x86_64",
      "libgpg-error-1.27-3.fc27.x86_64",
      "libdb-5.3.28-27.fc27.x86_64",
      "nss-util-3.35.0-1.0.fc27.x86_64",
      "libcap-2.25-7.fc27.x86_64",
      "popt-1.16-12.fc27.x86_64",
      "readline-7.0-7.fc27.x86_64",
      "libuuid-2.30.2-1.fc27.x86_64",
      "lua-libs-5.3.4-7.fc27.x86_64",
      "libassuan-2.5.1-1.fc27.x86_64",
      "libffi-3.1-14.fc27.x86_64",
      "libacl-2.2.52-18.fc27.x86_64",
      "p11-kit-0.23.9-2.fc27.x86_64",
      "libidn2-2.0.4-3.fc27.x86_64",
      "sqlite-libs-3.20.1-1.fc27.x86_64",
      "audit-libs-2.8.2-1.fc27.x86_64",
      "libcrypt-nss-2.26-26.fc27.x86_64",
      "libksba-1.3.5-5.fc27.x86_64",
      "pcre-8.41-5.fc27.x86_64",
      "systemd-libs-234-10.git5f8984e.fc27.x86_64",
      "libtasn1-4.13-1.fc27.x86_64",
      "ca-certificates-2018.2.22-1.0.fc27.noarch",
      "libsemanage-2.7-2.fc27.x86_64",
      "acl-2.2.52-18.fc27.x86_64",
      "nettle-3.4-1.fc27.x86_64",
      "libcomps-0.1.8-6.fc27.x86_64",
      "libmetalink-0.1.3-4.fc27.x86_64",
      "libidn-1.33-4.fc27.x86_64",
      "file-libs-5.31-10.fc27.x86_64",
      "elfutils-libs-0.170-1.fc27.x86_64",
      "openssl-libs-1.1.0g-1.fc27.x86_64",
      "crypto-policies-20170816-2.gite0a4066.fc27.noarch",
      "python3-setuptools-37.0.0-1.fc27.noarch",
      "python3-libs-3.6.4-8.fc27.x86_64",
      "shadow-utils-4.5-4.fc27.x86_64",
      "glib2-2.54.3-2.fc27.x86_64",
      "libsecret-0.18.5-5.fc27.x86_64",
      "libfdisk-2.30.2-1.fc27.x86_64",
      "python3-six-1.11.0-1.fc27.noarch",
      "gnutls-3.5.18-2.fc27.x86_64",
      "cracklib-2.9.6-7.fc27.x86_64",
      "pam-1.3.0-6.fc27.x86_64",
      "nss-3.35.0-1.1.fc27.x86_64",
      "ima-evm-utils-1.1-2.fc27.x86_64",
      "libssh2-1.8.0-5.fc27.x86_64",
      "libsss_idmap-1.16.0-6.fc27.x86_64",
      "libverto-0.2.6-11.fc27.x86_64",
      "gawk-4.1.4-8.fc27.x86_64",
      "cyrus-sasl-lib-2.1.26-34.fc27.x86_64",
      "libseccomp-2.3.3-1.fc27.x86_64",
      "npth-1.5-3.fc27.x86_64",
      "gpgme-1.9.0-6.fc27.x86_64",
      "libsmartcols-2.30.2-1.fc27.x86_64",
      "libpcap-1.8.1-6.fc27.x86_64",
      "device-mapper-1.02.144-1.fc27.x86_64",
      "cryptsetup-libs-1.7.5-3.fc27.x86_64",
      "systemd-234-10.git5f8984e.fc27.x86_64",
      "libnghttp2-1.25.0-1.fc27.x86_64",
      "librepo-1.8.0-1.fc27.x86_64",
      "curl-7.55.1-9.fc27.x86_64",
      "rpm-libs-4.14.1-1.fc27.x86_64",
      "libsolv-0.6.33-1.fc27.x86_64",
      "python3-hawkey-0.11.1-1.fc27.x86_64",
      "rpm-build-libs-4.14.1-1.fc27.x86_64",
      "python3-dnf-2.7.5-2.fc27.noarch",
      "dnf-yum-2.7.5-2.fc27.noarch",
      "trousers-0.3.13-9.fc27.x86_64",
      "sssd-client-1.16.0-6.fc27.x86_64",
      "cracklib-dicts-2.9.6-7.fc27.x86_64",
      "python3-dbus-1.2.4-8.fc27.x86_64",
      "vim-minimal-8.0.1553-1.fc27.x86_64",
      "diffutils-3.6-3.fc27.x86_64",
      "langpacks-en-1.0-10.fc27.noarch",
      "gpg-pubkey-f5282ee4-58ac92a3"
    ],
    "rpm-dependencies": [
      {
        "arch": "x86_64",
        "dependencies": [
          "libacl = 2.2.52-18.fc27",
          "libacl.so.1()(64bit)",
          "libacl.so.1(ACL_1.0)(64bit)",
          "libattr.so.1()(64bit)",
          "libc.so.6()(64bit)",
          "libc.so.6(GLIBC_2.14)(64bit)",
          "libc.so.6(GLIBC_2.2.5)(64bit)",
          "libc.so.6(GLIBC_2.3.4)(64bit)",
          "libc.so.6(GLIBC_2.4)(64bit)",
          "rpmlib(CompressedFileNames) <= 3.0.4-1",
          "rpmlib(FileDigests) <= 4.6.0-1",
          "rpmlib(PayloadFilesHavePrefix) <= 4.0-1",
          "rpmlib(PayloadIsXz) <= 5.2-1",
          "rtld(GNU_HASH)"
        ],
        "epoch": null,
        "name": "acl",
        "package_identifier": "acl-2.2.52-18.fc27.x86_64",
        "release": "18.fc27",
        "src": false,
        "version": "2.2.52"
      },
      {
        "arch": "x86_64",
        "dependencies": [
          "/sbin/ldconfig",
          "/sbin/ldconfig",
          "config(audit-libs) = 2.8.2-1.fc27",
          "libaudit.so.1()(64bit)",
          "libc.so.6()(64bit)",
          "libc.so.6(GLIBC_2.14)(64bit)",
          "libc.so.6(GLIBC_2.2.5)(64bit)",
          "libc.so.6(GLIBC_2.3)(64bit)",
          "libc.so.6(GLIBC_2.3.4)(64bit)",
          "libc.so.6(GLIBC_2.4)(64bit)",
          "libc.so.6(GLIBC_2.8)(64bit)",
          "libcap-ng.so.0()(64bit)",
          "rpmlib(CompressedFileNames) <= 3.0.4-1",
          "rpmlib(FileDigests) <= 4.6.0-1",
          "rpmlib(PayloadFilesHavePrefix) <= 4.0-1",
          "rpmlib(PayloadIsXz) <= 5.2-1",
          "rtld(GNU_HASH)"
        ],
        "epoch": null,
        "name": "audit-libs",
        "package_identifier": "audit-libs-2.8.2-1.fc27.x86_64",
        "release": "1.fc27",
        "src": false,
        "version": "2.8.2"
      },
      {
        "arch": "noarch",
        "dependencies": [
          "filesystem",
          "rpmlib(CompressedFileNames) <= 3.0.4-1",
          "rpmlib(FileDigests) <= 4.6.0-1",
          "rpmlib(PayloadFilesHavePrefix) <= 4.0-1",
          "rpmlib(PayloadIsXz) <= 5.2-1",
          "setup"
        ],
        "epoch": null,
        "name": "basesystem",
        "package_identifier": "basesystem-11-4.fc27.noarch",
        "release": "4.fc27",
        "src": false,
        "version": "11"
      },
      {
        "arch": "x86_64",
        "dependencies": [
          "/bin/sh",
          "config(bash) = 4.4.19-1.fc27",
          "filesystem >= 3",
          "libc.so.6()(64bit)",
          "libc.so.6(GLIBC_2.11)(64bit)",
          "libc.so.6(GLIBC_2.14)(64bit)",
          "libc.so.6(GLIBC_2.15)(64bit)",
          "libc.so.6(GLIBC_2.2.5)(64bit)",
          "libc.so.6(GLIBC_2.3)(64bit)",
          "libc.so.6(GLIBC_2.3.4)(64bit)",
          "libc.so.6(GLIBC_2.4)(64bit)",
          "libc.so.6(GLIBC_2.8)(64bit)",
          "libdl.so.2()(64bit)",
          "libdl.so.2(GLIBC_2.2.5)(64bit)",
          "libtinfo.so.6()(64bit)",
          "rpmlib(BuiltinLuaScripts) <= 4.2.2-1",
          "rpmlib(CompressedFileNames) <= 3.0.4-1",
          "rpmlib(FileDigests) <= 4.6.0-1",
          "rpmlib(PayloadFilesHavePrefix) <= 4.0-1",
          "rpmlib(PayloadIsXz) <= 5.2-1",
          "rtld(GNU_HASH)"
        ],
        "epoch": null,
        "name": "bash",
        "package_identifier": "bash-4.4.19-1.fc27.x86_64",
        "release": "1.fc27",
        "src": false,
        "version": "4.4.19"
      },
      {
        "arch": "x86_64",
        "dependencies": [
          "/sbin/ldconfig",
          "/sbin/ldconfig",
          "libc.so.6()(64bit)",
          "libc.so.6(GLIBC_2.2.5)(64bit)",
          "libc.so.6(GLIBC_2.3)(64bit)",
          "libc.so.6(GLIBC_2.3.4)(64bit)",
          "libc.so.6(GLIBC_2.4)(64bit)",
          "rpmlib(CompressedFileNames) <= 3.0.4-1",
          "rpmlib(FileDigests) <= 4.6.0-1",
          "rpmlib(PayloadFilesHavePrefix) <= 4.0-1",
          "rpmlib(PayloadIsXz) <= 5.2-1",
          "rtld(GNU_HASH)"
        ],
        "epoch": null,
        "name": "bzip2-libs",
        "package_identifier": "bzip2-libs-1.0.6-24.fc27.x86_64",
        "release": "24.fc27",
        "src": false,
        "version": "1.0.6"
      },
      {
        "arch": "noarch",
        "dependencies": [
          "/bin/sh",
          "/bin/sh",
          "/bin/sh",
          "config(ca-certificates) = 2018.2.22-1.0.fc27",
          "p11-kit >= 0.23.4",
          "p11-kit-trust >= 0.23.4",
          "rpmlib(CompressedFileNames) <= 3.0.4-1",
          "rpmlib(FileDigests) <= 4.6.0-1",
          "rpmlib(PayloadFilesHavePrefix) <= 4.0-1",
          "rpmlib(PayloadIsXz) <= 5.2-1"
        ],
        "epoch": null,
        "name": "ca-certificates",
        "package_identifier": "ca-certificates-2018.2.22-1.0.fc27.noarch",
        "release": "1.0.fc27",
        "src": false,
        "version": "2018.2.22"
      },
      {
        "arch": "x86_64",
        "dependencies": [
          "libc.so.6()(64bit)",
          "libc.so.6(GLIBC_2.14)(64bit)",
          "libc.so.6(GLIBC_2.2.5)(64bit)",
          "libc.so.6(GLIBC_2.3)(64bit)",
          "libc.so.6(GLIBC_2.3.4)(64bit)",
          "libc.so.6(GLIBC_2.4)(64bit)",
          "libc.so.6(GLIBC_2.8)(64bit)",
          "libpopt.so.0()(64bit)",
          "libpopt.so.0(LIBPOPT_0)(64bit)",
          "libselinux.so.1()(64bit)",
          "libsepol.so.1()(64bit)",
          "rpmlib(CompressedFileNames) <= 3.0.4-1",
          "rpmlib(FileDigests) <= 4.6.0-1",
          "rpmlib(PayloadFilesHavePrefix) <= 4.0-1",
          "rpmlib(PayloadIsXz) <= 5.2-1",
          "rtld(GNU_HASH)"
        ],
        "epoch": null,
        "name": "chkconfig",
        "package_identifier": "chkconfig-1.10-3.fc27.x86_64",
        "release": "3.fc27",
        "src": false,
        "version": "1.10"
      },
      {
        "arch": "x86_64",
        "dependencies": [
          "coreutils-common = 8.27-20.fc27",
          "libacl.so.1()(64bit)",
          "libacl.so.1(ACL_1.0)(64bit)",
          "libattr.so.1()(64bit)",
          "libattr.so.1(ATTR_1.1)(64bit)",
          "libc.so.6()(64bit)",
          "libc.so.6(GLIBC_2.10)(64bit)",
          "libc.so.6(GLIBC_2.14)(64bit)",
          "libc.so.6(GLIBC_2.15)(64bit)",
          "libc.so.6(GLIBC_2.17)(64bit)",
          "libc.so.6(GLIBC_2.2.5)(64bit)",
          "libc.so.6(GLIBC_2.3)(64bit)",
          "libc.so.6(GLIBC_2.3.4)(64bit)",
          "libc.so.6(GLIBC_2.4)(64bit)",
          "libc.so.6(GLIBC_2.6)(64bit)",
          "libc.so.6(GLIBC_2.7)(64bit)",
          "libcap.so.2()(64bit)",
          "libcrypto.so.1.1()(64bit)",
          "libcrypto.so.1.1(OPENSSL_1_1_0)(64bit)",
          "libgmp.so.10()(64bit)",
          "libpthread.so.0()(64bit)",
          "libpthread.so.0(GLIBC_2.2.5)(64bit)",
          "libpthread.so.0(GLIBC_2.3.2)(64bit)",
          "librt.so.1()(64bit)",
          "librt.so.1(GLIBC_2.3.3)(64bit)",
          "libselinux.so.1()(64bit)",
          "ncurses",
          "rpmlib(CompressedFileNames) <= 3.0.4-1",
          "rpmlib(FileDigests) <= 4.6.0-1",
          "rpmlib(PayloadFilesHavePrefix) <= 4.0-1",
          "rpmlib(PayloadIsXz) <= 5.2-1",
          "rtld(GNU_HASH)"
        ],
        "epoch": null,
        "name": "coreutils",
        "package_identifier": "coreutils-8.27-20.fc27.x86_64",
        "release": "20.fc27",
        "src": false,
        "version": "8.27"
      },

      ...
  }
