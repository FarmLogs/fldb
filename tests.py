import os
import unittest
import pprint

from fldb import FLDB

class TestBasicCases(unittest.TestCase):
  def setUp(self):
    self.conn = FLDB.from_name('TEST_DATABASE_URL')
    self.people = ['Ashley', 'Frank', 'Mason']

  def test_same_db(self):
    """
    Test that two calls to FLDB (from different entrypoints) results in the same
    underlying database pool being returned.

    """
    other_conn = FLDB.from_url(os.environ.get('TEST_DATABASE_URL'))
    assert self.conn is other_conn

  def test_cache_parameter(self):
    """
    Test that setting `cached` to False forces a new connection to be made.

    """
    other_conn = FLDB.from_url(os.environ.get('TEST_DATABASE_URL'), cached=False)
    assert self.conn is not other_conn

  def test_table_create_and_insert(self):
    """
    Create a table and insert some records for basic tests.

    """
    query = """
    CREATE TABLE IF NOT EXISTS test (
      id serial primary key not null,
      name varchar not null
    );
    -- Empty the table
    TRUNCATE TABLE test RESTART IDENTITY;
    """

    with self.conn.cursor(commit_on_close=True) as c:
      c.execute(query)
      for name in self.people:
        c.execute("""INSERT INTO test (name) VALUES (%s)""", (name, ))

  def test_table_query(self):
    """
    Read from the table that we created earlier to ensure that we can grab the same results.

    """
    query = """SELECT name FROM test;"""

    with self.conn.cursor() as c:
      c.execute(query)
      results = c.fetchall()

    self.assertItemsEqual([r.get('name') for r in results], self.people)

if __name__ == '__main__':
  unittest.main()
