# FLDB

Postgres database connection manager, backed by a threaded connection pool.

Usage:

```python
from fldb import FLDB

url = 'postgres://user:password@host/database'
conn = FLDB.from_url(url)
```

Or, if you use environment variables for your database strings,

```python
conn = FLDB.from_name('SHAREPOINT_DATABASE_URL')
```

Then, interact with your [Psycopg cursor](http://initd.org/psycopg/docs/usage.html) like you normally would:

```python
query = """SELECT * FROM people WHERE email = %s"""
with conn.cursor() as c:
  c.execute(query, ('fred@example.com', ))
```

If you are performing writes, use the `commit_on_close=True` parameter to auto commit your queries:

```python
statement = 'insert into people (name, email) values (%s, 5s)'
with conn.cursor(commit_on_close=True) as c:
  c.execute(statement, ('Fred', 'fred@example.com', ))

```

### Testing

Feel free to take a look at [tests.py](tests.py) to see some of this library in action.

The test suite was developed using [Docker Compose](https://docs.docker.com/compose/) to ensure that a fresh database is created and linked automagically on each run.

Running tests (in an isolated container) is as easy as:

    docker-compose run tests
