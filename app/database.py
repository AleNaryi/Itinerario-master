import pymysql
from pymysql.cursors import DictCursor
from contextlib import contextmanager
from flask import g
from app.config import DATABASE_CONFIG


class Database:

    @staticmethod
    def init_app(app):
        @app.teardown_appcontext
        def close(exception=None):
            conns = g.pop('_db_connections', {})
            for db_name, conn in conns.items():
                try:
                    conn.close()
                except Exception:
                    pass

    @staticmethod
    def get_connection(db_name='estadio_db'):
        if '_db_connections' not in g:
            g._db_connections = {}
        if db_name not in g._db_connections:
            cfg = DATABASE_CONFIG[db_name].copy()
            cfg['cursorclass'] = DictCursor
            g._db_connections[db_name] = pymysql.connect(**cfg)
            g._db_connections[db_name].autocommit(True)
        return g._db_connections[db_name]


@contextmanager
def transaction(db_name='estadio_db'):
    conn = Database.get_connection(db_name)
    conn.autocommit(False)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.autocommit(True)
