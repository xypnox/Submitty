"""SQLAlchemy Tables module."""

from pathlib import Path
from sqlalchemy import Column, create_engine
from sqlalchemy.engine import reflection
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import SmallInteger, String, TIMESTAMP
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func


class Database:
    """Database object which acts as a wrapper around sqlalchemy."""

    def __init__(self, params, environment):
        """
        Create database object, initializing DB engine and session.

        :param params: Object containing database connection details
        :type params: dict
        :param environment: Environment for database
        :type environment: str
        """
        self.DynamicBase = declarative_base(class_registry=dict())
        if 'driver' not in params:
            raise RuntimeError('Need to supply a driver')
        if params['driver'] == 'sqlite':
            connection_string = 'sqlite://'
        else:
            if params['driver'] == 'psql':
                connection_string = 'postgresql+psycopg2://'
            else:
                raise RuntimeError('Invalid driver')
            connection_string += '{}:{}@{}/{}'.format(
                params['user'],
                params['password'],
                params['host'] if not Path(params['host']).exists() else '',
                params['dbname']
            )

            if Path(params['host']).exists():
                connection_string += '?host={}'.format(params['host'])

        self.engine = create_engine(connection_string)
        self.engine.connect()
        self.inspector = reflection.Inspector.from_engine(self.engine)
        self.Session = sessionmaker()
        self.Session.configure(bind=self.engine)
        self.session = self.Session()

        self.migration_table = get_migration_table(environment, self.DynamicBase)

    def execute(self, query):
        """
        Run a raw query through the session.

        :param query: raw query string to execute
        :type query: str
        :rtype: sqlalchemy.engine.ResultProxy
        """
        return self.session.execute(query)

    def commit(self):
        """Run commit on the current session."""
        self.session.commit()

    def close(self):
        """Close the session and DB connnection."""
        self.session.close()
        self.engine.dispose()

    def has_table(self, table_name):
        """
        Check if engine has table.

        :param table_name: Name of table to check for
        :type table_name: str
        """
        return self.engine.has_table(table_name)

    def table_has_column(self, table, search_column):
        """
        Check if a table has a given column.

        :param table: Table to search in
        :type table: str
        :param search_column: column to search for
        :type search_column: str
        :rtype: bool
        """
        for column in self.inspector.get_columns(table):
            if search_column == column['name']:
                return True
        return False


def get_migration_table(environment, Base):
    """Get the migration table for a given environment."""
    class MigrationTable(Base):
        __tablename__ = "migrations_{}".format(environment)

        id = Column(String(100), primary_key=True)
        commit_time = Column(
            TIMESTAMP,
            onupdate=func.current_timestamp(),
            default=func.current_timestamp()
        )
        status = Column(SmallInteger, default=0)

    return MigrationTable
