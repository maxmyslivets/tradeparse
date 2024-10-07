import configparser
from pathlib import Path


class _ConfigSection:
    def __init__(self, config, section: str):
        self._config = config
        self._section = section

    def get(self, key, default=None):
        return self._config.get(self._section, key, fallback=default)

    def get_list(self, key, delimiter=', '):
        value = self.get(key)
        return value.split(delimiter) if value else []

    def get_int(self, key, default=None):
        return self._config.getint(self._section, key, fallback=default)

    def get_bool(self, key, default=None):
        return self._config.getboolean(self._section, key, fallback=default)


class _General(_ConfigSection):
    @property
    def url(self) -> str:
        return self.get('url')

    @property
    def interval(self) -> int:
        return self.get_int('interval')


class _Env(_ConfigSection):

    @property
    def env_token(self) -> str:
        return self.get('env_token')


class _DB(_ConfigSection):

    @property
    def json_db_path(self) -> Path:
        return Path(self.get('json_db_path'))

    @property
    def txt_users_db_path(self) -> Path:
        return Path(self.get('txt_users_db_path'))


class Config:
    def __init__(self, filepath: Path = Path('config.ini')):
        self._config = configparser.ConfigParser(interpolation=None)
        self._config.read(filepath, encoding='utf-8')

    @property
    def general(self):
        return _General(self._config, 'GENERAL')

    @property
    def env(self):
        return _Env(self._config, 'ENV')

    @property
    def db(self):
        return _DB(self._config, 'DB')
