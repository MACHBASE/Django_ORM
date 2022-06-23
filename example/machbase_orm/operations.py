"""
Written by Yeony.kim at 2021-11
"""
from django.db.backends.base.operations import BaseDatabaseOperations
from django.db import NotSupportedError


class DatabaseOperations(BaseDatabaseOperations):
    """
        Encapsulate backend-specific differences, such as the way a backend
        performs ordering or calculates the ID of a recently-inserted row.
        """
    # Integer field safe ranges by `internal_type` as documented
    # in docs/ref/models/fields.txt.
    integer_field_ranges = {
        'SmallIntegerField': (-32767, 32767),
        'IntegerField': (-2147483647, 2147483647),
        'BigIntegerField': (-9223372036854775807, 9223372036854775807),
        'PositiveBigIntegerField': (0, 18446744073709551614),
        'PositiveSmallIntegerField': (0, 65534),
        'PositiveIntegerField': (0, 4294967294),
        'SmallAutoField': (-32767, 32767),
        'AutoField': (-2147483647, 2147483647),
        'BigAutoField': (-9223372036854775807, 9223372036854775807),
    }
    set_operators = {
        'union': '',
        'intersection': '',
        'difference': '',
    }
    # Mapping of Field.get_internal_type() (typically the model field's class
    # name) to the data type to use for the Cast() function, if different from
    # DatabaseWrapper.data_types.
    cast_data_types = {}
    # CharField data type if the max_length argument isn't provided.
    cast_char_field_without_max_length = 'text'

    # Start and end points for window expressions.
    PRECEDING = 'PRECEDING'
    FOLLOWING = 'FOLLOWING'
    UNBOUNDED_PRECEDING = 'UNBOUNDED ' + PRECEDING
    UNBOUNDED_FOLLOWING = 'UNBOUNDED ' + FOLLOWING
    CURRENT_ROW = 'CURRENT ROW'

    # Prefix for EXPLAIN queries, or None EXPLAIN isn't supported.
    explain_prefix = None

    def autoinc_sql(self, table, column):
        """
        Return any SQL needed to support auto-incrementing primary keys, or
        None if no SQL is necessary.

        This SQL is executed when a table is created.
        안되는 기능인데 다른 예제가 없어서 그냥 진행
        """
        return None

    def bulk_batch_size(self, fields, objs):
        """
        Return the maximum allowed batch size for the backend. The fields
        are the fields going to be inserted in the batch, the objs contains
        all the objects to be inserted.
        """
        return len(objs)

    def format_for_duration_arithmetic(self, sql):
        return sql

    def cache_key_culling_sql(self):
        """
        Return an SQL query that retrieves the first cache key greater than the
        n smallest.

        This is used by the 'db' cache backend to determine where to start
        culling.
        이것도 잘 모르겠음
        """
        return "SELECT cache_key FROM %s ORDER BY cache_key LIMIT 1 OFFSET %%s"

    def unification_cast_sql(self, output_field):
        """
        Given a field instance, return the SQL that casts the result of a union
        to that type. The resulting string should contain a '%s' placeholder
        for the expression being cast.
        """
        return '?'

    def binary_placeholder_sql(self, value):
        """
        Some backends require special syntax to insert binary content (MySQL
        for example uses '_binary %s').
        """
        return '?'

    def date_extract_sql(self, lookup_type, field_name):
        """
        Given a lookup_type of 'year', 'month', or 'day', return the SQL that
        extracts a value from the given date field field_name.
        실제 에러가 발생하면 그때 작성
        """
        raise NotImplementedError('subclasses of BaseDatabaseOperations may require a date_extract_sql() method')

    def date_trunc_sql(self, lookup_type, field_name, tzname=None):
        """
        Given a lookup_type of 'year', 'month', or 'day', return the SQL that
        truncates the given date or datetime field field_name to a date object
        with only the given specificity.

        If `tzname` is provided, the given value is truncated in a specific
        timezone.

        실제 에러가 발생하면 그때 작성
        """
        raise NotImplementedError('subclasses of BaseDatabaseOperations may require a date_trunc_sql() method.')

    def datetime_cast_date_sql(self, field_name, tzname):
        """
        Return the SQL to cast a datetime value to date value.
        """
        return field_name

    def datetime_cast_time_sql(self, field_name, tzname):
        """
        Return the SQL to cast a datetime value to time value.
        """
        return field_name

    def datetime_extract_sql(self, lookup_type, field_name, tzname):
        """
        Given a lookup_type of 'year', 'month', 'day', 'hour', 'minute', or
        'second', return the SQL that extracts a value from the given
        datetime field field_name.
        실제 에러가 발생하면 그때 작성
        """
        raise NotImplementedError('subclasses of BaseDatabaseOperations may require a datetime_extract_sql() method')

    def datetime_trunc_sql(self, lookup_type, field_name, tzname):
        """
        Given a lookup_type of 'year', 'month', 'day', 'hour', 'minute', or
        'second', return the SQL that truncates the given datetime field
        field_name to a datetime object with only the given specificity.
        실제 에러가 발생하면 그때 작성
        """
        raise NotImplementedError('subclasses of BaseDatabaseOperations may require a datetime_trunc_sql() method')

    def time_trunc_sql(self, lookup_type, field_name, tzname=None):
        """
        Given a lookup_type of 'hour', 'minute' or 'second', return the SQL
        that truncates the given time or datetime field field_name to a time
        object with only the given specificity.

        If `tzname` is provided, the given value is truncated in a specific
        timezone.
        실제 에러가 발생하면 그때 작성
        """
        raise NotImplementedError('subclasses of BaseDatabaseOperations may require a time_trunc_sql() method')

    def time_extract_sql(self, lookup_type, field_name):
        """
        Given a lookup_type of 'hour', 'minute', or 'second', return the SQL
        that extracts a value from the given time field field_name.
        정확하게 뭔지 모르겠음 그대로 두고 진행
        """
        return self.date_extract_sql(lookup_type, field_name)

    def deferrable_sql(self):
        """
        Return the SQL to make a constraint "initially deferred" during a
        CREATE TABLE statement.
        """
        return ''

    def distinct_sql(self, fields, params):
        """
        Return an SQL DISTINCT clause which removes duplicate rows from the
        result set. If any fields are given, only check the given fields for
        duplicates.
        """
        if fields:
            raise NotSupportedError('DISTINCT ON fields is not supported by this database backend')
        else:
            return ['DISTINCT'], []

    def fetch_returned_insert_columns(self, cursor, returning_params):
        """
        Given a cursor object that has just performed an INSERT...RETURNING
        statement into a table, return the newly created data.
        """
        return ()

    def field_cast_sql(self, db_type, internal_type):
        """
        Given a column type (e.g. 'BLOB', 'VARCHAR') and an internal type
        (e.g. 'GenericIPAddressField'), return the SQL to cast it before using
        it in a WHERE statement. The resulting string should contain a '%s'
        placeholder for the column being searched against.
        """
        return '%s'

    def force_no_ordering(self):
        """
        Return a list used in the "ORDER BY" clause to force no ordering at
        all. Return an empty list to include nothing in the ordering.
        """
        return []

    def for_update_sql(self, nowait=False, skip_locked=False, of=(), no_key=False):
        """
        Return the FOR UPDATE SQL clause to lock rows for an update operation.
        """
        return False

    def last_insert_id(self, cursor, table_name, pk_name):
        """
        Given a cursor object that has just performed an INSERT statement into
        a table that has an auto-incrementing ID, return the newly created ID.

        `pk_name` is the name of the primary-key column.
        """
        return cursor.execute(f"select _RID from {table_name} limit 1").fetchone()[0] + 1

    def lookup_cast(self, lookup_type, internal_type=None):
        """
        Return the string to use in a query when performing lookups
        ("contains", "like", etc.). It should contain a '%s' placeholder for
        the column being searched against.
        """
        return "%s"

    def max_in_list_size(self):
        """
        Return the maximum number of items that can be passed in a single 'IN'
        list condition, or None if the backend does not impose a limit.
        """
        return None

    def max_name_length(self):
        """
        Return the maximum length of table and column names, or None if there
        is no limit.
        """
        return None

    def no_limit_value(self):
        """
        Return the value to use for the LIMIT when we are wanting "LIMIT
        infinity". Return None if the limit clause can be omitted in this case.
        """
        return None

    def pk_default_value(self):
        """
        Return the value to use during an INSERT statement to specify that
        the field should use its default value.
        """
        return 'NULL'

    def process_clob(self, value):
        """
        Return the value of a CLOB column, for backends that return a locator
        object that requires additional processing.
        """
        return value

    def return_insert_columns(self, fields):
        """
        For backends that support returning columns as part of an insert query,
        return the SQL and params to append to the INSERT query. The returned
        fragment should contain a format string to hold the appropriate column.
        """
        pass

    def quote_name(self, name):
        """
        Return a quoted version of the given table, index, or column name. Do
        not quote the given name if it's already been quoted.
        """
        if name.startswith("'") and name.endswith("'"):
            return name  # Quoting once is enough.
        return "'%s'" % name

    def regex_lookup(self, lookup_type):
        """
        Return the string to use in a query when performing regular expression
        lookups (using "regex" or "iregex"). It should contain a '%s'
        placeholder for the column being searched against.

        If the feature is not supported (or part of it is not supported), raise
        NotImplementedError.
        """
        raise NotImplementedError('subclasses of BaseDatabaseOperations may require a regex_lookup() method')

    def savepoint_create_sql(self, sid):
        """
        Return the SQL for starting a new savepoint. Only required if the
        "uses_savepoints" feature is True. The "sid" parameter is a string
        for the savepoint id.
        지원하지 않아 그대로 둠
        """
        return "SAVEPOINT %s" % self.quote_name(sid)

    def savepoint_commit_sql(self, sid):
        """
        Return the SQL for committing the given savepoint.
        지원하지 않아 그대로 둠
        """
        return "RELEASE SAVEPOINT %s" % self.quote_name(sid)

    def savepoint_rollback_sql(self, sid):
        """
        Return the SQL for rolling back the given savepoint.
        지원하지 않아 그대로 둠
        """
        return "ROLLBACK TO SAVEPOINT %s" % self.quote_name(sid)

    def set_time_zone_sql(self):
        """
        Return the SQL that will set the connection's time zone.

        Return '' if the backend doesn't support time zones.
        지원하지 않아 그대로 둠
        """
        return ''

    def sql_flush(self, style, tables, *, reset_sequences=False, allow_cascade=False):
        """
        Return a list of SQL statements required to remove all data from
        the given database tables (without actually removing the tables
        themselves).

        The `style` argument is a Style object as returned by either
        color_style() or no_style() in django.core.management.color.

        If `reset_sequences` is True, the list includes SQL statements required
        to reset the sequences.

        The `allow_cascade` argument determines whether truncation may cascade
        to tables with foreign keys pointing the tables being truncated.
        PostgreSQL requires a cascade even if these tables are empty.

        transaction 기반 DB가 아니다 보니 flush가 필요하지 않음
        """
        raise NotImplementedError('subclasses of BaseDatabaseOperations must provide an sql_flush() method')

    def execute_sql_flush(self, sql_list):
        """Execute a list of SQL statements to flush the database."""
        pass

    def sequence_reset_by_name_sql(self, style, sequences):
        """
        Return a list of the SQL statements required to reset sequences
        passed in `sequences`.

        The `style` argument is a Style object as returned by either
        color_style() or no_style() in django.core.management.color.
        """
        return []

    def sequence_reset_sql(self, style, model_list):
        """
        Return a list of the SQL statements required to reset sequences for
        the given models.

        The `style` argument is a Style object as returned by either
        color_style() or no_style() in django.core.management.color.
        """
        return []  # No sequence reset required by default.

    def start_transaction_sql(self):
        """
        Return the SQL statement required to start a transaction.
        이 구문이 호출될 일은 없을 것 같긴 함
        """
        return "BEGIN;"

    def end_transaction_sql(self, success=True):
        """
        Return the SQL statement required to end a transaction.
        이 구문이 호출될 일은 없을 것 같긴 함
        """
        if not success:
            return "ROLLBACK;"
        return "COMMIT;"

    def explain_query_prefix(self, format=None, **options):
        raise NotSupportedError('This backend does not support explaining query execution.')
        # if not self.connection.features.supports_explaining_query_execution:
        #     raise NotSupportedError('This backend does not support explaining query execution.')
        # if format:
        #     supported_formats = self.connection.features.supported_explain_formats
        #     normalized_format = format.upper()
        #     if normalized_format not in supported_formats:
        #         msg = '%s is not a recognized format.' % normalized_format
        #         if supported_formats:
        #             msg += ' Allowed formats: %s' % ', '.join(sorted(supported_formats))
        #         raise ValueError(msg)
        # if options:
        #     raise ValueError('Unknown options: %s' % ', '.join(sorted(options.keys())))
        # return self.explain_prefix

    def insert_statement(self, ignore_conflicts=False):
        return 'INSERT INTO'

    def ignore_conflicts_suffix_sql(self, ignore_conflicts=None):
        return ''

    def bulk_insert_sql(self, fields, placeholder_rows):
        return "VALUES (" + ", ".join(['?' for _ in fields]) + ")"
