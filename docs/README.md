# Benchmarking Portal

A Benchmarking Portal to provide comparative, de-identified analysis to Departments.

## Overview

* **One page project overview**
* **[Goals and Measures](/docs/GoalsAndMeasures.md)**
* **[Glossary](/docs/Glossary.md)**
* **[Supporting Documents](docs/references/references.md)**

## Business Requirements

The key user roles/personas together with the current state and future state user journey maps are;

* **[User Roles](/docs/UserRoles.md)**
* **[Current Journey Map](/docs/CurrentJourneyMap.md)**
* **[Future Journey Map](/docs/FutureJourneyMap.md)**
* **Epics ([All](https://github.com/gs-fin/benchmarking-portal/issues?q=is%3Aissue+label%3AEpic) / [Open](https://github.com/gs-fin/benchmarking-portal/issues?q=is%3Aopen+is%3Aissue+label%3AEpic))** - representing a high level feature set, used to categorise more detailed user stories.
* **Stories ([All](https://github.com/gs-fin/benchmarking-portal/issues?q=is%3Aissue+label%3AStory) / [Open](https://github.com/gs-fin/benchmarking-portal/issues?q=is%3Aopen+is%3Aissue+label%3AStory))** - representing a specific testable user or system requirement, delivered via a series of tasks.

## Solution Architecture

Four solution model pages provide a sufficient system overview for new designers, developers and testers to quickly understand the system and navigate the code and issues.

* **[System Context Model](/docs/SystemContextModel.md)**
* **[Wireframes and Mockups](/docs/WireframesAndMockups.md)**
* **[Logical Data Model](/docs/LogicalDataModel.md)**
* **[Security Model](/docs/SecurityModel.md)**
* **[Process and State Lifecycle Models](/docs/ProcessAndStateLifecycleModels.md)**
* **[MVP Definition](/docs/MVP.md)**

## Test Framework

A Behaviour Driven Develpment (BDD) model is at the heart of the testing frameork.

* **[Test Data Management](/docs/TestDataManagement.md)**
* **[BDD Test Cases](/docs/BDDTestCases.md)**

## System Operations

A highly automated continuous delivery pipeline based on the [Code On Tap](http://codeontap.io/) is used for confident deployment of new features.

* **[DevOps Framework](/docs/DevOpsFramework.md)**
* **[System Access](/docs/SystemAccess.md)**

## Project Management

Is all done with tickets;

* **[Raw List of Issues](https://github.com/gs-fin/benchmarking-portal/issues)**
* **[Kanban](https://github.com/orgs/gs-fin/projects/1)**
* **[Milestones](https://github.com/gs-fin/benchmarking-portal/milestones)**

## Contributors

Contributors to the project are expected to perform their feature submissions in the form of a pull request and follow the following guidelines for coding style.

### Code Style

- [code style](https://www.python.org/dev/peps/pep-0008/)
- [docstrings](https://www.python.org/dev/peps/pep-0257/)
- [comments](https://www.python.org/dev/peps/pep-0008/#comments)
- [GoSource Guidelines](https://github.com/gs-gs/methodology)


### Environment variable contract

Applications using codeontap should ensure that all their configuration is provided via environment variables.

To test locally, create a .env file in the src directory matching the variables you require set. You can cut and paste the
sections below to create this file, or use env.sample.
Note that this file is excluded from the repo via .gitignore, and will be explicitly deleted if the code in run via Docker in a shared environment.

Variables containing sensitive material can be protected using the AWS KMS encryption service, and the base64 encoded result stored in the variable.
If the value fails to decrypt, then the provided value is used. Note that this is applied to all environment values so anything can be protected.

If debug is true, then a value must be provided for DJANGO_SECRET_KEY.

```
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=
```

The same code can be run in different "Modes". For some modes, the number of worker processes can be configured.

```
# Run as a web application
APP_RUN_MODE="WEB"
APP_WORKER_COUNT="3"
#
# Use manage.py to run one or more run-to-completion tasks
APP_RUN_MODE="TASK"
#
# Run as a celery worker
#
APP_RUN_MODE="WORKER"
APP_WORKER_COUNT="3"
```

The actual action for each mode is defined by a script in the src directory of the form

```
entrypoint-{lower case mode}.sh
```

It is this possible to add or update the modes available, but this should only be done in consultation with the devops team.


If a SQL database if required, set the following

```
DATABASE_PORT=
DATABASE_HOST=
DATABASE_NAME=
DATABASE_USERNAME=
DATABASE_PASSWORD=
#
# This is optional - defaults to postgresql
DATABASE_ENGINE=
```


### Local development

You can start either docker-composed environment (with postgres and stuff) or start things locally. Shared deployments described in "Devops" section. All instructions assume you already in the repo root.

#### docker-compose way

It doesn't work yet.

#### Old-style way

If you prefer old-style way without docker overhead. Please ensure you have all requirements configured (currently it's just database, so you need some postgres installation).
`python3.6 -m venv .venv` shall create Python 3 virtualenv (expected python3.6). Virtualenv directory may have any name, just please don't commit it (env and .venv are gitignored already).

Please note that before first manage.py command you have to export some env variables, otherwise default will be used. In most cases you have to copy `local-classic.env.example` file to `.env` file and update it (database, debug etc.). Python code has some hook which tries to read this file every time (yet, may be we remove it).

    $ pyvenv .venv
    $ source .venv/bin/activate
    $ pip install pip --upgrade
    $ pip install -r requirements.txt
    $ ./manage.py check
    $ ./manage.py migrate
    $ ./manage.py createsuperuser
    $ ./manage.py runserver

Another approach is to keep virtualenv outside the working directory, so just create it somewhere else and use the same way.

After that navigate to the correct place (runserver shows where exactly, by default http://localhost:8000/ but you can change the port).