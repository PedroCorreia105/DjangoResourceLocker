<p align="center">
  <a href="http://nestjs.com/" target="blank"><img src="https://1000logos.net/wp-content/uploads/2020/08/Django-Logo.png" width="320" alt="NestJs Logo" /></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.12-blue" alt="Python Version" />
  <img src="https://img.shields.io/badge/pip-24.3-green" alt="Pip Version" />
  <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code_style-black-000000.svg?" alt="code style: black"></a>
  <a href="https://www.codefactor.io/repository/github/pedrocorreia105/DjangoResourceLocker/overview/master"><img src="https://www.codefactor.io/repository/github/pedrocorreia105/DjangoResourceLocker/badge/master" alt="CodeFactor" /></a>
  <a href="https://codecov.io/gh/PedroCorreia105/DjangoResourceLocker/branch/master"><img src="https://codecov.io/gh/PedroCorreia105/DjangoResourceLocker/branch/master/graph/badge.svg" alt="Code Coverage"></a>
  <a href="https://ci.appveyor.com/project/PedroCorreia105/djangoresourcelocker"><img src="https://ci.appveyor.com/api/projects/status/myfc1ol1j1c0omx7?svg=true" alt="Build"></a>
  <a href="https://github.com/PedroCorreia105/DjangoResourceLocker/blob/master/LICENSE"><img src="https://img.shields.io/github/license/PedroCorreia105/DjangoResourceLocker" alt="License"></a>
</p>

<p align="center">
  <sub><sup>
    <a href="#description">Description</a> •
    <a href="#stack">Stack</a> •
    <a href="#installation">Installation</a> •
    <a href="#database">Database</a> •
    <a href="#running-the-app">Running the app</a> •
    <a href="#endpoints">Endpoints</a> •
    <a href="#test">Test</a> •
    <a href="#video-tutorials">Video Tutorials</a> •
    <a href="#helpful-repos">Helpful repos</a> •
    <a href="#license">License</a>
  </sub></sup>
</p>

## Description

A dockerized Django API for locking resources preventing multiple users from making changes. Authentication, input validation, API versioning and testing included.

## Stack

<table align="center">
  <tr>
    <td align="right">
      <b>Language</b>
    </td>
    <td align="left">
      <a href="https://www.python.org/">Python</a>
    </td>
  </tr>
  <tr>
    <td align="right">
      <b>Framework</b>
    </td>
    <td align="left">
      <a href="https://www.djangoproject.com/">Django</a>
    </td>
  </tr> 
  <tr>
    <td align="right">
      <b>Database</b>
    </td>
    <td align="left">
      <a href="https://www.sqlite.org/">SQLite3</a>
    </td>
  </tr>
  <tr>
    <td align="right">
      <b>Cache</b>
    </td>
    <td align="left">
      <a href="https://redis.io/">Redis</a>
    </td>
  </tr>
  <tr>
    <td align="right">
      <b>Linter</b>
    </td>
    <td align="left">
      <a href="https://github.com/psf/black">Black</a>
    </td>
  </tr>
  <tr>
    <td align="right">
      <b>CI</b>
    </td>
    <td align="left">
      <a href="https://www.appveyor.com/">AppVeyor</a>
    </td>
  </tr>
 </table>

## Installation

```bash
# Create virtual environment
$ python -m venv .venv

# Activate virtual environment
$ source .venv/bin/activate

# Install dependecies
$ pip install -r requirements.txt
```

## Database

```bash
# Generate migrations
$ python manage.py makemigrations

# Apply migrations
$ python manage.py migrate

# Create admin user
$ python manage.py createsuperuser

# Launch redis
$ docker-compose up redis -d

# Redis cli
$ docker-compose exec redis redis-cli -a pass -n 1
```

## Running the app

```bash
# Launch server
$ python manage.py runserver
```

## Endpoints

```bash
# API
http://localhost:8000/api

# Swagger UI
http://localhost:8000/docs

# Administration UI
http://localhost:8000/admin
```

## Test

```bash
# Run tests
$ python manage.py test

# Run tests with code coverage
$ python run_tests_with_coverage.py
```

## Video Tutorials

-   [freeCodeCamp.org - Django REST Framework Coursen](https://www.youtube.com/watch?v=tujhGdn1EMI)
-   [Dave Gray - Python Django Full Course](https://www.youtube.com/watch?v=Rp5vd34d-z4)
-   [Tech with Tim - Learn Django](https://www.youtube.com/watch?v=nGIg40xs9e4)
-   [PedroTech - Python Django REST API](https://www.youtube.com/watch?v=NoLF7Dlu5mc)

## Helpful repos

-   https://github.com/bobby-didcoding/drf_course/tree/main
-   https://github.com/gitdagray/django-course/tree/main
-   https://github.com/techwithtim/django-rest-api/tree/main
-   https://github.com/machadop1407/react-django-tutorial/tree/main
-   https://github.com/ArchTaqi/django-rest-api/tree/master

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/PedroCorreia105/DjangoResourceLocker/blob/master/LICENSE) file for details.
