"""
Machbase database backend for Django.

Requires pyodbc : https://github.com/mkleehammer/pyodbc
Requires Machbase ODBC Library

Written by Yeony.kim at 2021-11

"""
from django.core.exceptions import ImproperlyConfigured
from django.db import DatabaseError as WrappedDatabaseError, connections
from django.db.backends.base.base import BaseDatabaseWrapper

try:
    import pyodbc as Database
    if 'MachbaseODBC' not in Database.drivers():
        raise ImportError
except ImportError as e:
    raise ImproperlyConfigured("Error loading psycopg2 module: %s" % e)

from .client import DatabaseClient  # NOQA
from .creation import DatabaseCreation  # NOQA
from .features import DatabaseFeatures  # NOQA
from .introspection import DatabaseIntrospection  # NOQA
from .operations import DatabaseOperations  # NOQA
from .schema import DatabaseSchemaEditor  # NOQA
import re
import requests
import base64
import json


class MachbaseConnectionWrapper:

    def __init__(self, connection, setting_dict=None):
        self.connection = connection
        self._setting_dict = setting_dict
        [setattr(self, key, getattr(connection, key)) for key in dir(connection) if key not in ['__class__', 'autocommit', 'maxwrite', 'searchescape', 'timeout']]

    def cursor(self):
        return MachbaseCursorWrapper(self.connection, self.connection.cursor(), self._setting_dict)

    @property
    def autocommit(self):
        return self.connection.autocommit

    @autocommit.setter
    def autocommit(self, value):
        self.connection.autocommit = value

    @property
    def maxwrite(self):
        return self.connection.maxwrite

    @maxwrite.setter
    def maxwrite(self, value):
        self.connection.maxwrite = value

    @property
    def searchescape(self):
        return self.connection.searchescape

    @searchescape.setter
    def searchescape(self, value):
        self.connection.searchescape = value

    @property
    def timeout(self):
        return self.connection.timeout

    @timeout.setter
    def timeout(self, value):
        self.connection.timeout = value

class MachbaseCursorWrapper:

    def __init__(self, connection, cursor, setting_dict):
        self._connection = connection
        self._cursor = cursor
        self._setting_dict = setting_dict
        # self.cancel = self._cursor.cancel
        # self.close = self._cursor.close
        # self.columns = self._cursor.columns
        # self.commit = self._cursor.commit
        # self.fetchall = self._cursor.fetchall
        self.fetchmany = self._cursor.fetchmany
        # self.fetchone = self._cursor.fetchone
        # self.fetchval = self._cursor.fetchval
        # self.foreignKeys = self._cursor.foreignKeys
        # self.getTypeInfo = self._cursor.getTypeInfo
        # self.nextset = self._cursor.nextset
        # self.primaryKeys = self._cursor.primaryKeys
        # self.procedureColumns = self._cursor.procedureColumns
        # self.rowVerColumns = self._cursor.rowVerColumns
        # self.setinputsizes = self._cursor.setinputsizes
        # self.setoutputsize = self._cursor.setoutputsize
        # self.skip = self._cursor.skip
        # self.statistics = self._cursor.statistics
        # self.tables = self._cursor.tables
        self.__url = f'http://{self._setting_dict.get("HOST", "127.0.0.1")}:{self._setting_dict.get("HTTP_PORT", 5657)}/machbase'
        self.__headers = {
            'Authorization': base64.b64encode(
                f'{self._setting_dict.get("USER", "sys").lower()}@localhost:{self._setting_dict.get("PASSWORD", "manager").lower()}'.encode(
                    'utf-8')).decode('utf-8'),
            "Content-Type": "application/json"
        }
        self.limit = self._setting_dict.get('LIMIT', -1)

    def cancel(self, *args, **kwargs):
        return self._cursor.cancel(*args, **kwargs)

    def close(self, *args, **kwargs):
        try:
            return self._cursor.close(*args, **kwargs)
        except Database.ProgrammingError as e:
            return None


    def columns(self, *args, **kwargs):
        return self._cursor.columns(*args, **kwargs)

    def commit(self, *args, **kwargs):
        return self._cursor.commit(*args, **kwargs)

    def fetchall(self, *args, **kwargs):
        return self._cursor.fetchall(*args, **kwargs)

    def fetchmany(self, *args, **kwargs):
        return self._cursor.fetchmany(*args, **kwargs)

    def fetchone(self, *args, **kwargs):
        return self._cursor.fetchone(*args, **kwargs)

    def fetchval(self, *args, **kwargs):
        return self._cursor.fetchval(*args, **kwargs)

    def foreignKeys(self, *args, **kwargs):
        return self._cursor.foreignKeys(*args, **kwargs)

    def getTypeInfo(self, *args, **kwargs):
        return self._cursor.getTypeInfo(*args, **kwargs)

    def nextset(self, *args, **kwargs):
        return self._cursor.nextset(*args, **kwargs)

    def primaryKeys(self, *args, **kwargs):
        return self._cursor.primaryKeys(*args, **kwargs)

    def procedureColumns(self, *args, **kwargs):
        return self._cursor.procedureColumns(*args, **kwargs)

    def rowVerColumns(self, *args, **kwargs):
        return self._cursor.rowVerColumns(*args, **kwargs)

    def setinputsizes(self, *args, **kwargs):
        return self._cursor.setinputsizes(*args, **kwargs)

    def setoutputsize(self, *args, **kwargs):
        return self._cursor.setoutputsize(*args, **kwargs)

    def skip(self, *args, **kwargs):
        return self._cursor.skip(*args, **kwargs)

    def statistics(self, *args, **kwargs):
        return self._cursor.statistics(*args, **kwargs)

    def tables(self, *args, **kwargs):
        return self._cursor.tables(*args, **kwargs)

    def __enter__(self, *args, **kwargs):
        # return self._cursor.__enter__(*args, **kwargs)
        return self

    def __exit__(self, *args, **kwargs):
        return self._cursor.__exit__(*args, **kwargs)

    def __iter__(self, *args, **kwargs):
        return self._cursor.__iter__(*args, **kwargs)

    def __next__(self, *args, **kwargs):
        return self._cursor.__next__(*args, **kwargs)

    def execute(self, sql, params=None):
        sql = self.replace_format_to_question(sql)
        if self.limit > 0:
            if sql.lower().find('limit') == -1:
                sql += f" limit {self.limit}"
        # sql = sql.replace(f"{sql.split(' ')[sql.split(' ').index('FROM') + 1]}.\'id\',", '')
        if params is None:
            return self._cursor.execute(sql)
        else:

            try:
                if 'INSERT INTO' in sql:
                    # 마크베이스 이슈로 인해서 insert into table_name values (?, ?) 형태의 query에 대해서
                    # execute(query, value)로 진행하는 경우, machbase가 재시작 되는 이슈가 있어서,
                    # cursor 자체를 close하고 새롭게 할당하는 것으로 하기와 같이 임시적으로 조치를 취해두었음, 추후 Machbase가 업데이트 모두 되는 경우 제거 가능
                    # self._cursor.close()
                    # self._cursor = self._connection.cursor()

                    # 추가 사항
                    # ORM에서 Append를 요청(insert into 에 많은 value를 요청) 하는 경우 다시말해서 insert into를 요청하는 경우
                    # http request를 통해서 machbase의 rest api를 call하여서 데이터를 insert 하도록 변경

                    # params 의 경우 각 record별로 column이 2개인 경우 하기와 같이 1차원 벡터로 데이터가 전달된다.
                    # 해당 데이터를 [[record_1_col_1_value, record_1_col_2_value], [record_2_col_1_value, record_2_col_2_value], ...] 형태로 변환해서 data의 values에 넘겨주어야 한다.
                    # params : [record_1_col_1_value, record_1_col_2_value, record_2_col_1_value, record_2_col_2_value, ...]
                    col_num = sum([x == '?' for x in list(sql.split('VALUES')[-1])])
                    values = list(zip(*[[param for param_idx, param in enumerate(params) if param_idx % col_num == col_idx] for col_idx in range(col_num)]))
                    data = {
                        "name": sql.split(' ')[2].replace("'", ""),
                        "values": values
                    }
                    self.__request_append_api(data)
                    result = self._cursor
                else:
                    result = self._cursor.execute(sql, params)

                return result
            except UnicodeDecodeError:
                print('DB Internal Error')
                return None
            except Database.ProgrammingError:
                print('DB Internal Error')
                return None

    def executemany(self, sql, param_list):
        if 'INSERT INTO' in sql:
            # 마크베이스 이슈로 인해서 insert into table_name values (?, ?) 형태의 query에 대해서
            # execute(query, value)로 진행하는 경우, machbase가 재시작 되는 이슈가 있어서,
            # cursor 자체를 close하고 새롭게 할당하는 것으로 임시적으로 조치를 취해두었음, 추후 Machbase가 업데이트 모두 되는 경우 제거 가능
            # ORM에서 Append가 이해는 안되나 왜 필요한지, append를 요청(insert into 에 많은 value를 요청) 하는 경우 다시말해서 insert into를 요청하는 경우 http request를 통해서 machbase의 rest api를 call하여서 데이터를 insert 하도록 변경
            # self._cursor.close()
            # self._cursor = self._connection.cursor()
            data = {
                "name": sql.split(' ')[2].replace("'", ""),
                "values": param_list
            }
            self.__request_append_api(data)
            return self._cursor
        else:
            sql = self.replace_format_to_question(sql)
            return self._cursor.executemany(sql, param_list)

    def __request_append_api(self, data):
        data.update({'date_format': data.get('date_format', "YYYY-MM-DD")})

        requests.post(self.__url, json.dumps(data), headers=self.__headers)

    @staticmethod
    def replace_format_to_question(input_str):
        return re.sub('%[a-z]', '?', input_str)

    @property
    def arraysize(self):
        return self._cursor.arraysize

    @property
    def connection(self):
        return self._cursor.connection

    @property
    def description(self):
        return self._cursor.description

    @property
    def fast_executemany(self):
        return self._cursor.fast_executemany

    @property
    def noscan(self):
        return self._cursor.noscan

    @property
    def rowcount(self):
        return self._cursor.rowcount


class DatabaseWrapper(BaseDatabaseWrapper):
    vendor = 'machbase'
    display_name = 'Machbase'
    data_types = {
        'AutoField': 'integer',
        'BigAutoField': 'long',
        'BinaryField': 'binary',
        'BooleanField': 'short',
        'CharField': 'varchar(%(max_length)s)',
        'DateField': 'datetime',
        'DateTimeField': 'datetime',
        # 'DecimalField': NotImplementedError,
        'DurationField': 'long',
        'FileField': 'varchar(%(max_length)s)',
        'FilePathField': 'varchar(%(max_length)s)',
        'FloatField': 'double',
        'IntegerField': 'integer',
        'BigIntegerField': 'long',
        'IPAddressField': 'ipv4',
        'GenericIPAddressField': 'ipv6',
        'JSONField': 'text',
        'OneToOneField': 'integer',
        'PositiveBigIntegerField': 'ulong',
        'PositiveIntegerField': 'uinteger',
        'PositiveSmallIntegerField': 'ushort',
        'SlugField': 'varchar(%(max_length)s)',
        'SmallAutoField': 'integer',
        'SmallIntegerField': 'short',
        'TextField': 'text',
        'TimeField': 'datetime',
        'UUIDField': 'varchar(32)',
    }

    # _limited_data_types = (
    #     'tinyblob', 'blob', 'mediumblob', 'longblob', 'tinytext', 'text',
    #     'mediumtext', 'longtext', 'json',
    # )

    # data_type_check_constraints = {
    #     'PositiveBigIntegerField': '"%(column)s" >= 0',
    #     'PositiveIntegerField': '"%(column)s" >= 0',
    #     'PositiveSmallIntegerField': '"%(column)s" >= 0',
    # }
    operators = {
        'exact': '= %s',
        'iexact': 'LIKE %s',
        'contains': 'REGEXP %s',
        'icontains': "LIKE '%%' || %s || '%%'",
        'regex': 'REGEXP %s',
        'iregex': "REGEXP '(?i)' || %s",
        'gt': '> %s',
        'gte': '>= %s',
        'lt': '< %s',
        'lte': '<= %s',
        'startswith': "REGEXP '^' || %s",
        'endswith': "REGEXP %s || '$'",
        'istartswith': "LIKE %s || '%%'",
        'iendswith': "LIKE '%%' || %s",
    }

    pattern_esc = r""

    pattern_ops = {
        'contains': "REGEXP {}",
        'icontains': "LIKE '%%' || {} || '%%'",
        'startswith': "REGEXP '^' || {}",
        'istartswith': "LIKE {} || '%%'",
        'endswith': "REGEXP {} || '$'",
        'iendswith': "LIKE '%%' || {}",
    }
    Database = Database

    SchemaEditorClass = DatabaseSchemaEditor
    # Classes instantiated in __init__().
    client_class = DatabaseClient
    creation_class = DatabaseCreation
    features_class = DatabaseFeatures
    introspection_class = DatabaseIntrospection
    ops_class = DatabaseOperations
    # PostgreSQL backend-specific attributes.
    _named_cursor_idx = 0

    def get_connection_params(self):
        settings_dict = self.settings_dict
        if settings_dict['NAME'].upper() != "MACHBASE":
            raise ImproperlyConfigured(
                "settings.DATABASES is improperly configured. "
                "Please supply the NAME value."
            )
        conn_params = {
            'driver': 'MachbaseODBC',
            'server': settings_dict.get('HOST', '127.0.0.1'),
            'uid': settings_dict.get('USER', 'SYS'),
            'pwd': settings_dict.get('PASSWORD', 'MANAGER'),
            'port': settings_dict.get('PORT', '5656'),
            'conntype': settings_dict.get('CONNTYPE', 1),
            'compress': settings_dict.get('COMPRESS', 512),
            'os': settings_dict.get('OS', 'linux')
        }
        return conn_params

    @staticmethod
    def handler_text(aValue):
        # print(aValue)
        return aValue

    @staticmethod
    def handler_positiveInteger(aValue):
        # print(aValue)
        return aValue
        # return struct.unpack('>L', aValue)

    def get_new_connection(self, conn_params):

        connection = Database.connect(self.buildConnectionStr(conn_params))
        encoding = 'utf8'
        if 'win' in conn_params.get('os', 'linux').lower():
            encoding = 'cp949'
        # connection.add_output_converter(2100, self.handler_text)  # text
        # connection.add_output_converter(2202, self.handler_positiveInteger)  # positive integer
        connection.setdecoding(Database.SQL_CHAR, encoding=encoding)
        connection.setdecoding(Database.SQL_WCHAR, encoding=encoding)
        connection.setencoding(encoding=encoding)
        return MachbaseConnectionWrapper(connection, self.settings_dict)
        # return connection

    def init_connection_state(self):
        pass

    def create_cursor(self, name=None):
        return MachbaseCursorWrapper(self.connection, self.connection.cursor(), self.settings_dict)

    def _set_autocommit(self, autocommit):
        with self.wrap_database_errors:
            self.connection.autocommit = autocommit

    def is_usable(self):
        try:
            # Use a psycopg cursor directly, bypassing Django's utilities.
            with self.connection.cursor() as cursor:
                cursor.execute('SELECT * from m$sys_tables limit 1')
        except Database.Error:
            return False
        else:
            return True

    @staticmethod
    def buildConnectionStr(conn_params):
        return "DRIVER={" + f"{conn_params['driver']}" + "};SERVER=" + f"{conn_params['server']};UID={conn_params['uid']};PWD={conn_params['pwd']};PORT_NO={conn_params['port']};CONNTYPE={conn_params['conntype']};COMPRESS={conn_params['compress']};"

    def _nodb_cursor(self):
        """
        다른 DB의 경우 Inmemory를 위한 connection을 따로 진행하나, Machbase의 경우 해당 인메모리 DB로서의 역할을 volatile로 수행이 가능할 것으로 판단됨
        """
        return self.cursor()

    def make_debug_cursor(self, cursor):
        """Create a cursor that logs all queries in self.queries_log."""
        return cursor

    def make_cursor(self, cursor):
        """Create a cursor without debug logging."""
        return cursor

