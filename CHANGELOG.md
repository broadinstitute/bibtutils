# Changelog

[PyPI History](https://pypi.org/project/bibtutils/#history)

## [1.0.0](https://www.github.com/broadinstitute/bibtutils/compare/v0.5.1...v1.0.0`) (2022-07-02)

### Features

* [GCP] Added functionality to support service account impersonation via the IAM library.
* [GCP] Added support for specified credentials for existing GCP code.
* [GCP] Minor bug fixes and adjustments.
* [GCP] Added docstrings for 100% coverage.
* Updated documentation.
* Merged `dependabot` PRs.

## [0.5.1](https://www.github.com/broadinstitute/bibtutils/compare/v0.5.0...v0.5.1) (2021-06-09)

### Features

* Added some missing parameters to docstrings.
* Merged `dependabot` PRs.
* Fixed minor documentation errors.

## [0.5.0](https://www.github.com/broadinstitute/bibtutils/compare/v0.4.0...v0.5.0) (2021-06-08)

### Features

* Added `CHANGELOG.md`
* Clarified testing instructions on the "Contributing" page and in `README.md`.
* Split tests into different files for different submodules.
* Use `intersphinx` to link to GCP resource documentations.
* Removed `sanitycheck.py` (was used to test during initial packaging and deployment).

#### Storage

* Added `create_bucket` functionality.
* Added functionality to permit automatic bucket creation during data upload.

#### Bigquery

* Added `create_table` functionality. Supports TimePartioning by field and/or upload intervals on the default `_PARTITIONTIME` field.
* Added a `create_and_upload` function combining both table creation and GCS JSONNLD data upload into one call.
* Added support for specifying schemas during table creation and/or data upload.

## [0.4.0](https://www.github.com/broadinstitute/bibtutils/compare/v0.3.5...v0.4.0) (2021-06-04)

### Features

* Updated package dependencies to latest minor releases.
* Added a Dockerfile and relevant configuration files for pre-release testing.
