rhok-hive
=========

==git usage

add these entries to your .gitignore file

```
venv
*.pyc
*.db
```

==Heroku deployment

App is currently set up to use wsgi, should be upgraded to gunicorn

See here for general notes on deploying Django to heroku:

https://devcenter.heroku.com/articles/django

Install the heroku ruby gem or toolbelt.

Add the following entry to the repository's .git/config

```
[remote "heroku"]
        url = git@heroku.com:beelogger.git
        fetch = +refs/heads/*:refs/remotes/heroku/*
```

Deploy to heroku using git:

```bash
git subtree push --prefix hive heroku master
```

Use the heroku command to sync the database and carry out other commands:

```bash
heroku logs                        # view logs
heroku logs -t                     # tail logs
heroku run python manage.py syncdb # sync database
heroku run python manage.py shell  # launch production shell
```

=== Running cron tasks in heroku

See: https://devcenter.heroku.com/articles/scheduler

=== Heroku specific settings

heroku supports persistent config vars like this:

```bash
heroku config
heroku config:set DJANGO_ENVIRONMENT=heroku
```

Heroku environment-specific overrides are currently in the main settings.py file and activated by environemnt variable DJANGO_ENVIRONMENT=heroku
