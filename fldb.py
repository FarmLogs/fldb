import os
import logging
from contextlib import contextmanager

import psycopg2

from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool, PoolError

MAX_CONNECTION_ATTEMPTS = 10


class EnvironmentVariableNotFoundException(Exception):
    pass


class FLDB(object):
    """
    Provides convenience methods around creating DatabasePool objects, and
    attempts to cache those connections when possible.

    """
    _connections = {}

    @staticmethod
    def get_url_from_environment(name=None):
        """
        Try name as upper-cased and with _DATABASE_URL appended,
        accepting the first name that exists.

        """
        attempts = (name.upper(), '%s_DATABASE_URL' % name.upper(), )

        for env in attempts:
            if env in os.environ:
                return os.environ.get(env), env

        raise EnvironmentVariableNotFoundException(
            "The envrionment variables %s were not found." % ' or '.join(attempts))

    @classmethod
    def from_name(cls, name, **kwargs):
        """
        Return a pool instance by name (following our convention of NAME_DATABASE_URL)
        first checking to see if it's already been created and returning that instance.

        See the DatabasePool class below for more information on the additional
        arguments that can be passed to this method.

        """
        if not name:
            name = 'DATABASE_URL'

        url, env = cls.get_url_from_environment(name)

        return cls.from_url(url, **kwargs)

    @classmethod
    def from_url(cls, url, **kwargs):
        """
        Return a pool instance by Database URL.

        See the DatabasePool class below for more information on the additional
        arguments that can be passed to this method.

        """
        kwargs['connection_url'] = url

        # If cached=False is provided, return a fresh instance.
        if not kwargs.get('cached', True):
            return DatabasePool(**kwargs)

        # Generate a hashing key based on the keyword arguments.
        cache_key = hash(frozenset(kwargs.items()))

        if cache_key in cls._connections:
            return cls._connections.get(cache_key)

        new_conn = DatabasePool(**kwargs)
        cls._connections[cache_key] = new_conn
        return new_conn


class DatabasePool(object):
    """
    Creates and manages a pool of connections to a database.

    This wraps ThreadedConnectionPool, see http://initd.org/psycopg/docs/pool.html

    - connection_url is a postgresql://user@host/database style DSN
    - name is an optional nickname for the database connection
    - mincount is the minimum number of connections to keep open
    - maxcount is the maximum number of connections to have open
    - cursor_factory defines the factory used for inflating database rows

    """
    MINIMUM_CONNECTION_COUNT = 2
    MAXIMUM_CONNECTION_COUNT = 40
    DEFAULT_CURSOR_FACTORY = RealDictCursor

    def __init__(self, connection_url, name=None, mincount=None, maxcount=None, cursor_factory=None, **kwargs):
        self.connection_url = connection_url
        self.name = name or connection_url

        self.mincount = mincount
        self.maxcount = maxcount
        self.cursor_factory = cursor_factory

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.name)

    def __del__(self):
        if hasattr(self, '_pool'):
            self._pool.closeall()

    def make_pool(self):
        return ThreadedConnectionPool(self.mincount or self.MINIMUM_CONNECTION_COUNT,
                                      self.maxcount or self.MAXIMUM_CONNECTION_COUNT,
                                      self.connection_url,
                                      cursor_factory=self.cursor_factory or self.DEFAULT_CURSOR_FACTORY)

    @property
    def pool(self):
        """
        Lazy pool creation.

        """
        pool = getattr(self, '_pool', None)
        if not pool:
            self._pool = pool = self.make_pool()
        return pool

    @contextmanager
    def cursor(self, commit_on_close=False):
        """
        Fetches a cursor from the database connection pool.
        We run a dummy query because we have experienced stale connections that fail
        to correctly report that their connection has closed, and cause OperationalErrors.

        """
        for _ in range(MAX_CONNECTION_ATTEMPTS):
            try:
                con = self.pool.getconn()
                test_cur = con.cursor()
                test_cur.execute("SELECT 42 as fldb_test_query;")
                test_cur.close()
                break

            except (psycopg2.DatabaseError, psycopg2.OperationalError):
                pass

        else:
            raise RuntimeError('Could not get a connection to: %s' % self.name)

        try:
            yield con.cursor()
            if commit_on_close:
                con.commit()

        except PoolError as e:
            logging.log(logging.ERROR, e.message)

        finally:
            try:
                self._pool.putconn(con)
            except:
                pass
