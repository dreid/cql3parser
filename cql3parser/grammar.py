import os
import uuid

from parsley import makeGrammar, termMaker

from cql3parser.types import native_types

keywords = [
    'SELECT',
    'FROM',
    'WHERE',
    'AND',
    'KEY',
    'INSERT',
    'UPDATE',
    'WITH',
    'LIMIT',
    'USING',
    'USE',
    'COUNT',
    'SET',
    'BEGIN',
    'UNLOGGED',
    'BATCH',
    'APPLY',
    'TRUNCATE',
    'DELETE',
    'IN',
    'CREATE',
    'KEYSPACE',
    'SCHEMA',
    'KEYSPACES',
    'COLUMNFAMILY',
    'TABLE',
    'INDEX',
    'ON',
    'TO',
    'DROP',
    'PRIMARY',
    'INTO',
    'VALUES',
    'TIMESTAMP',
    'TTL',
    'ALTER',
    'RENAME',
    'ADD',
    'TYPE',
    'COMPACT',
    'STORAGE',
    'ORDER',
    'BY',
    'ASC',
    'DESC',
    'ALLOW',
    'FILTERING',

    'GRANT',
    'ALL',
    'PERMISSION',
    'PERMISSIONS',
    'OF',
    'REVOKE',
    'MODIFY',
    'AUTHORIZE',
    'NORECURSIVE',

    'USER',
    'USERS',
    'SUPERUSER',
    'NOSUPERUSER',
    'PASSWORD',

    'CLUSTERING',
    'ASCII',
    'BIGINT',
    'BLOB',
    'BOOLEAN',
    'COUNTER',
    'DECIMAL',
    'FLOAT',
    'INET',
    'INT',
    'TEXT',
    'UUID',
    'VARCHAR',
    'VARINT',
    'TIMEUUID',
    'TOKEN',
    'WRITETIME',

    'MAP',
    'LIST',

    'TRUE',
    'FALSE',
]

unreserved_keywords = [
    'KEY',
    'CLUSTERING',
    'COUNT',
    'TTL',
    'COMPACT',
    'STORAGE',
    'TYPE',
    'VALUES',
    'WRITETIME',
    'MAP',
    'LIST',
    'FILTERING',
    'PERMISSION',
    'PERMISSIONS',
    'KEYSPACES',
    'ALL',
    'USER',
    'USERS',
    'SUPERUSER',
    'NOSUPERUSER',
    'PASSWORD'
]

bindings = {
    'UUID': uuid.UUID,
    'keywords': keywords,
    'unreserved_keywords': unreserved_keywords,
    'native_types': native_types,
    't': termMaker
}


def trace(*a):
    print 'TRACE:', a


def _load():
    grammar = os.path.join(os.path.dirname(__file__), 'cql3.parsley')
    with open(grammar, 'r') as g:
        return makeGrammar(g.read(), bindings, 'cql3', tracefunc=trace)


CQL3 = _load()
