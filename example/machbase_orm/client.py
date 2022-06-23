"""
Written by Yeony.kim at 2021-11
Machbase는 실행 된 것으로 가정하고 기능을 사용하기 때문에, 하기 Client 관련 로직은 구현하지 않음

"""
from django.db.backends.base.client import BaseDatabaseClient


class DatabaseClient(BaseDatabaseClient):
    executable_name = 'machbase'

    @classmethod
    def settings_to_cmd_args_env(cls, settings_dict, parameters):
        pass

    def runshell(self, parameters):
        pass
        # super().runshell(parameters)
