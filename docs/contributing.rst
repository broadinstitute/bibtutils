Contributor's Guide
===================

Testing new code
----------------

-  Ensure you have Docker installed and running on your system.
-  Make any necessary changes to ``./tests/config.py``
-  In the root folder for bibtutils, run the command:

.. code:: bash

   $ docker build -f ./Dockerfile -t bibtutils-test . && docker run bibtutils-test

-  This will build a container and install whatever code you have in 
   ``bibtutils/`` as the bibtutils library before running any tests in ``tests/``
   using ``pytest``.

-  Note that you will need a service account credentials file with the requisite 
   permissions on all resources used for tests. This file should be located at: 
   ``./creds/service_account.json``

-  The account will need at least the following roles in the specified GCP project
   in order to attempt all tests:
   -  ``Storage Admin``
   -  ``BigQuery Job User``
   -  And the following roles on the below resources (values specified in ``./tests/config.py``):
      -  ``Storage Admin`` on ``TEST_BUCKET``
      -  ``BigQuery Admin`` on ``TEST_DATASET``
      -  ``Publisher`` on ``TEST_PUBSUB``
      -  ``Secret Version Accessor`` on ``TEST_SECRET``

Updating and publishing a new package
-------------------------------------

-  This project makes use of `GitHub
   Actions <https://github.com/features/actions>`__ and
   `bump2version <https://github.com/c4urself/bump2version>`__ to
   automate publishing updates to pypi. See the `Github Workflow
   file <./.github/workflows/publish-to-test-pypi.yaml>`__ and
   `bumpversion file <./.bumpversion.cfg>`__ for configuration details.
   See links below for more resources.

-  Please keep ``CHANGELOG.md`` up to date.

-  Please install the following packages:

.. code:: bash

    $ pip install --upgrade bump2version

-  **Note**: You cannot publish a package with the same version number
   as another already-published version! **You must use bump2version**
   to increment the current version for a publish to be successful.

.. code:: bash

   # test documentation build
   # Note: if stylesheets are not updating, do a `make clean` before building.
   $ cd docs
   $ make html
   # see any undocumented objects
   $ make html -b coverage

   # Handling an open issue
   # ...assign the issue to yourself in Github...
   $ git checkout -b issue-1
   # ...make fixes...
   $ git add .
   $ git commit -m "fixes issue-1"
   $ git push --set-upstream origin issue-1
   # ...open PR...
   # ...PR merged, issue closed automatically...
   $ git checkout main
   $ git pull
   $ git bumpversion
   $ git push --tags
   # Code packaged, documentation updated, and version released automatically!

   $ git add .
   $ git commit -m "msg"
   $ bumpversion major|minor|patch # with bump2version, bumpversion is an alias
   # and to update main branch
   $ git push
   # to trigger a package & release
   $ git push --tags

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
