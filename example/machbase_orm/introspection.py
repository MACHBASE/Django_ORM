"""
Written by Yeony.kim at 2021-11
"""
from django.db.backends.base.introspection import BaseDatabaseIntrospection, FieldInfo, TableInfo


class DatabaseIntrospection(BaseDatabaseIntrospection):
    """Encapsulate backend-specific introspection utilities."""

    data_types_reverse = {
        'short': 'SmallIntegerField',
        'ushort': 'PositiveSmallIntegerField',
        'integer': 'IntegerField',
        'uinteger': 'PositiveIntegerField',
        'long': 'BigIntegerField',
        'ulong': 'PositiveBigIntegerField',
        'float': 'FloatField',
        'double': 'FloatField',
        'datetime': 'DateTimeField',
        'varchar': 'CharField',
        'ipv4': 'IPAddressField',
        'ipv6': 'GenericIPAddressField',
        'text': 'TextField',
        'binary': 'BinaryField'
    }

    def get_table_list(self, cursor):
        """
        Return an unsorted list of TableInfo named tuples of all tables and
        views that exist in the database.
        """
        return [TableInfo(row[0], 't') for row in cursor.execute("SELECT name, type FROM m$sys_tables WHERE type=0 ORDER BY name").fetchall()]

    def get_table_description(self, cursor, table_name):
        """
        Return a description of the table with the DB-API cursor.description
        interface.
        """

        columns = cursor.execute(
            f"select * from m$sys_columns join (select name, id from m$sys_tables where name='{table_name.upper()}') as tables on m$sys_columns.table_id=tables.id;").fetchall()

        return [FieldInfo(row[0], row[1], row[4], row[4], None, None, True, None, None) for row in columns if not row[0] in ['_RID', '_ARRIVAL_TIME']]

    def get_sequences(self, cursor, table_name, table_fields=()):
        """
        Return a list of introspected sequences for table_name. Each sequence
        is a dict: {'table': <table_name>, 'column': <column_name>}. An optional
        'name' key can be added if the backend supports named sequences.

        sequence가 되는지 않되는지 정확하게 모름
        """

        return []

    def get_relations(self, cursor, table_name):
        """
        Return a dictionary of
        {field_name: (field_name_other_table, other_table)} representing all
        relationships to the given table.

        relation 안됨
        """
        return {}

    def get_key_columns(self, cursor, table_name):
        """
        Backends can override this to return a list of:
            (column_name, referenced_table_name, referenced_column_name)
        for all key columns in given table.
        일단 key column이라는 것이 없기 때문에...
        """
        raise []

    def get_primary_key_column(self, cursor, table_name):
        """
        Return the name of the primary key column for the given table.
        """
        for constraint in self.get_constraints(cursor, table_name).values():
            if constraint['primary_key']:
                return constraint['columns'][0]
        return None

    def get_constraints(self, cursor, table_name):
        """
        Retrieve any constraints or keys (unique, pk, fk, check, index)
        across one or more columns.

        Return a dict mapping constraint names to their attributes,
        where attributes is a dict with keys:
         * columns: List of columns this covers
         * primary_key: True if primary key, False otherwise
         * unique: True if this is a unique constraint, False otherwise
         * foreign_key: (table, column) of target, or None
         * check: True if check constraint, False otherwise
         * index: True if index, False otherwise.
         * orders: The order (ASC/DESC) defined for the columns of indexes
         * type: The type of the index (btree, hash, etc.)

        Some backends may return special constraint names that don't exist
        if they don't name constraints of a certain type (e.g. SQLite)
        """
        return {
            'columns': cursor.execute(f"select * from m$sys_columns join (select name, id from m$sys_tables where name='{table_name.upper()}') as tables on m$sys_columns.table_id=tables.id;").fetchall(),
            'primary_key': False,
            'unique': False,
            'foreign_key': False,
            'check': False,
            'index': False,
            'orders': 'DESC',
            'type': 'etc'

        }

