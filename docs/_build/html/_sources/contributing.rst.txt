Contributor's Guide
===================

Updating and publishing a new package
-------------------------------------

-  This project makes use of `GitHub
   Actions <https://github.com/features/actions>`__ and
   `bump2version <https://github.com/c4urself/bump2version>`__ to
   automate publishing updates to pypi. See the `Github Workflow
   file <./.github/workflows/publish-to-test-pypi.yaml>`__ and
   `bumpversion file <./.bumpversion.cfg>`__ for configuration details.
   See links below for more resources.

-  Please install the following packages:

.. code:: bash

    $ pip install --upgrade bump2version pdoc3

-  **Note**: You cannot publish a package with the same version number
   as another already-published version! **You must use bump2version**
   to increment the current version for a publish to be successful.

.. code:: bash

    $ pdoc3 --html --output-dir docs/html --force .
    $ git add .
    $ git commit -m "msg"
    $ bumpversion major|minor|patch # with bump2version, bumpversion is an alias
    # to trigger a package & release
    $ git push --tags
    # and to update main branch
    $ git push

Getting Comfortable: Tutorials and Resources
--------------------------------------------

-  `Python Packaging
   Tutorial <https://packaging.python.org/tutorials/packaging-projects/>`__
-  `Python CICD Publishing with Github
   Actions <https://packaging.python.org/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/>`__
-  `Python Packaging
   Reference <https://packaging.python.org/guides/distributing-packages-using-setuptools/>`__
-  `GitHub Actions <https://github.com/features/actions>`__
-  `bump2version <https://github.com/c4urself/bump2version>`__

