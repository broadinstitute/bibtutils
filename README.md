# 2023-12-11: THIS LIBRARY IS DEPRECATED. PLEASE USE THE FOLLOWING LIBRARIES INSTEAD.

- [bibt-gcp-bq](https://github.com/broadinstitute/bibt-gcp-bq)
- [bibt-gcp-iam](https://github.com/broadinstitute/bibt-gcp-iam)
- [bibt-gcp-pubsub](https://github.com/broadinstitute/bibt-gcp-pubsub)
- [bibt-gcp-secrets](https://github.com/broadinstitute/bibt-gcp-secrets)
- [bibt-gcp-storage](https://github.com/broadinstitute/bibt-gcp-storage)
- [bibt-slack](https://github.com/broadinstitute/bibt-slack)
- [Complete list of libraries](https://broadinstitute.github.io/bibt-libraries/)

---

# bibtutils: BITS Blue Team Utilities

- **Developer**: Matthew OBrien
- **Email**: mobrien@broadinstitute.org
- **Project URL**: https://pypi.org/project/bibtutils/
- **Project Repo**: https://github.com/broadinstitute/bibtutils
- **Project Documentation**: https://bibtutils.readthedocs.io/en/latest/

## Installing

```bash
$ pip install --upgrade bibtutils
```

## Testing

- Requires Docker to be installed on your system.
- Clone this repo and create & run the test container:

```
$ docker build -f ./Dockerfile -t bibtutils-test . && docker run bibtutils-test
```

## Usage

- See documentation here: https://bibtutils.readthedocs.io/en/latest/
