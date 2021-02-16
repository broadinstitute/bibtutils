# bibtutils: BITS Blue Team Utilities

- **Developer**: Matthew OBrien
- **Email**: mobrien@broadinstitute.org
- **Project URL**: https://test.pypi.org/project/bibtutils/
- **Project Repo**: https://github.com/broadinstitute/bibtutils
- **TEST Project URL**: https://test.pypi.org/project/bibtutils/
- **TEST Project Repo**: https://github.com/ob775/bibtutils-test

## Installing

```bash
$ pip install --upgrade bibtutils
```

## Installing from testpypi

```bash
$ pip install --upgrade -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple bibtutils
```

## Usage

- See documentation here: https://readthedocs.org/projects/bibtutils/

## Contributing

### Updating and publishing a new package

- This project makes use of [GitHub Actions](https://github.com/features/actions) and [bump2version](https://github.com/c4urself/bump2version) to automate publishing updates to pypi. See the [Github Workflow file](./.github/workflows/publish-to-test-pypi.yaml) and [bumpversion file](./.bumpversion.cfg) for configuration details. See links below for more resources.

- Please install the following packages:

```bash
$ pip install --upgrade bump2version pdoc3
```

- **Note**: You cannot publish a package with the same version number as another already-published version! **You must use bump2version** to increment the current version for a publish to be successful.

```bash
$ pdoc3 --html --output-dir docs/html --force .
$ git add .
$ git commit -m "msg"
$ bumpversion major|minor|patch # with bump2version, bumpversion is an alias
$ git push --tags
```

### Getting Comfortable: Tutorials and Resources

- [Python Packaging Tutorial](https://packaging.python.org/tutorials/packaging-projects/)
- [Python CICD Publishing with Github Actions](https://packaging.python.org/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
- [Python Packaging Reference](https://packaging.python.org/guides/distributing-packages-using-setuptools/)
- [GitHub Actions](https://github.com/features/actions)
- [bump2version](https://github.com/c4urself/bump2version)
