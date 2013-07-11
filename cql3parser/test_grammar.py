import uuid

import pytest

from parsley import ParseError, termMaker as t

from cql3parser import CQL3, grammar, types


@pytest.mark.parametrize(
    ("input", "expected"),
    [(k, k.upper()) for k in grammar.keywords])
def test_keywords(input, expected):
    """
    All defined keywords in the grammar are case insensitive and return their
    uppercase canonical representation.

    Example: k('SELECT') -> 'SELECT'
    """
    assert CQL3(input).k(input) == expected
    assert CQL3(input.title()).k(input) == expected
    assert CQL3(input.lower()).k(input) == expected


def test_undefined_keyword():
    """
    Keywords not defined in CQL3 raise a ParseError.
    """
    with pytest.raises(ParseError):
        assert CQL3('foobar').k('foobar')


def test_keywords_consume_leading_whitespace():
    """
    Matching a keyword should consume leading whitespace, this makes
    rules which are large combinations of keywords easier to read.
    """
    assert CQL3('    SELECT').k('SELECT') == 'SELECT'


def test_alias_keywords():
    """
    Some keywords are aliases for others, those get special rules a_<canonical>
    where canonical is the version I arbitrarily like best.
    """
    assert CQL3('KEYSPACE').a_keyspace() == 'KEYSPACE'
    assert CQL3('SCHEMA').a_keyspace() == 'KEYSPACE'
    assert CQL3('COLUMNFAMILY').a_table() == 'TABLE'
    assert CQL3('TABLE').a_table() == 'TABLE'


@pytest.mark.parametrize(
    ("keyword", "expected"),
    [(uk, uk.upper()) for uk in grammar.unreserved_keywords])
def test_unreserved_keywords(keyword, expected):
    """
    Some keywords aren't reserved.
    """
    assert CQL3(keyword).unreserved_keyword() == expected
    assert CQL3(keyword.title()).unreserved_keyword() == expected
    assert CQL3(keyword.lower()).unreserved_keyword() == expected


def test_unreserved_keywords_consume_leading_whitespace():
    assert CQL3('    KEY').unreserved_keyword() == 'KEY'


@pytest.mark.parametrize(
    ('keyword', 'native_type'),
    types.native_types.items())
def test_native_type(keyword, native_type):
    assert CQL3(keyword).native_type() == t.NativeType(keyword, native_type)


def test_identifiers():
    assert CQL3('foo').identifier() == t.Identifier('foo')
    assert CQL3('FoO').identifier() == t.Identifier('foo')
    assert CQL3('foo_b4r').identifier() == t.Identifier('foo_b4r')


def test_quoted_name():
    assert CQL3('""""').quoted_name() == t.QuotedName('"')
    assert CQL3('"foo"').quoted_name() == t.QuotedName('foo')
    assert CQL3('"fOo"').quoted_name() == t.QuotedName('fOo')
    assert CQL3('"foo bar"').quoted_name() == t.QuotedName('foo bar')
    assert CQL3(
        '"foo ""bar"" baz"').quoted_name() == t.QuotedName('foo "bar" baz')


def test_string():
    assert CQL3("''''").string() == "'"
    assert CQL3("'foo bar baz bax'").string() == 'foo bar baz bax'
    assert CQL3("'foo''s'").string() == "foo's"


def test_integer():
    assert CQL3("-10").integer() == -10
    assert CQL3("-00012345").integer() == -12345
    assert CQL3("10").integer() == 10
    assert CQL3("0000012345").integer() == 12345


def test_float():
    assert CQL3("1.0").float() == 1.0
    assert CQL3("-1.0").float() == -1.0
    assert CQL3("000123.45").float() == 123.45
    assert CQL3("-000123.45").float() == -123.45
    assert CQL3("1.0e9").float() == 1.0e9
    assert CQL3("1.0e-9").float() == 1.0e-9
    assert CQL3("1.4453E+3").float() == 1.4453e3
    assert CQL3("1e10").float() == 1e10


def test_uuid():
    u = uuid.uuid4()
    assert CQL3(str(u)).uuid() == u

    u = uuid.uuid1()
    assert CQL3(str(u)).timeuuid() == u


def test_boolean():
    assert CQL3('true').boolean() is True
    assert CQL3('False').boolean() is False


def test_map():
    assert CQL3("{}").map() == {}
    assert CQL3("{'foo': 1}").map() == {'foo': 1}
    assert CQL3("{ 'foo' : 'bar', 'baz': 1.0 }").map() == {
        'foo': 'bar',
        'baz': 1.0
    }


def test_terms():
    assert CQL3("1.0").term() == 1.0
    assert CQL3("1").term() == 1
    assert CQL3("'foo bar'").term() == 'foo bar'
    assert CQL3('True').term() is True
    assert CQL3("?").term() == t.Binding()

    u = uuid.uuid4()
    assert CQL3(str(u)).term() == u


def test_keyspace():
    assert CQL3(
        "anKeyspace").keyspace() == t.Keyspace(t.Identifier('ankeyspace'))
    assert CQL3(
        '"anKeyspace"').keyspace() == t.Keyspace(t.QuotedName('anKeyspace'))
    assert CQL3(
        '   an_keyspace').keyspace() == t.Keyspace(t.Identifier('an_keyspace'))


def test_table():
    assert CQL3("table").table() == t.Table(t.Identifier('table'), None)
    assert CQL3("keyspace.table").table() == t.Table(
        t.Identifier('table'),
        t.Keyspace(t.Identifier('keyspace')))

    assert CQL3("    table").table() == t.Table(t.Identifier('table'), None)


def test_index():
    assert CQL3("index").index() == t.Index(t.Identifier('index'))
    assert CQL3("    index").index() == t.Index(t.Identifier('index'))


def test_username():
    assert CQL3("username").user() == t.User(t.Identifier("username"))
    assert CQL3("'username'").user() == t.User('username')
    assert CQL3("   username").user() == t.User(t.Identifier('username'))


def test_properties():
    assert CQL3(
        "gc_grace_seconds = 10 "
        "AND comment = 'foo bar'"
    ).properties() == t.Properties([
        t.Property(t.Identifier('gc_grace_seconds'), 10),
        t.Property(t.Identifier('comment'), 'foo bar')])

    assert CQL3(
        "foo = "
        "'org.apache.cassandra.db.marshal.AsciiType'"
    ).properties() == t.Properties([
        t.Property(t.Identifier('foo'),
                   'org.apache.cassandra.db.marshal.AsciiType')])

    assert CQL3("foo = True").properties() == t.Properties([
        t.Property(t.Identifier('foo'), True)])
    assert CQL3("foo = 1.0").properties() == t.Properties([
        t.Property(t.Identifier('foo'), 1.0)])
    assert CQL3("foo = bar").properties() == t.Properties([
        t.Property(t.Identifier('foo'), t.Identifier('bar'))])


def test_USE():
    assert CQL3(
        "USE anKeyspace").use() == t.Use(
        t.Keyspace(t.Identifier("ankeyspace")))


def test_DROP():
    assert CQL3(
        "DROP KEYSPACE k").drop() == t.Drop(t.Keyspace(t.Identifier("k")))
    assert CQL3(
        "DROP SCHEMA k").drop() == t.Drop(t.Keyspace(t.Identifier("k")))
    assert CQL3(
        "DROP TABLE t").drop() == t.Drop(t.Table(t.Identifier("t"), None))
    assert CQL3(
        "DROP COLUMNFAMILY t").drop() == t.Drop(
        t.Table(t.Identifier("t"), None))
    assert CQL3(
        "DROP INDEX index").drop() == t.Drop(t.Index(t.Identifier('index')))
    assert CQL3(
        "DROP USER username").drop() == t.Drop(
        t.User(t.Identifier("username")))


def test_TRUNCATE():
    assert CQL3("TRUNCATE table").truncate() == t.Truncate(
        t.Table(t.Identifier('table'), None))


def test_LIST_USERS():
    assert CQL3('LIST USERS').list_users() == t.List(t.Users())


def test_REVOKE():
    assert CQL3('REVOKE ALL ON ALL KEYSPACES FROM user').revoke() == t.Revoke(
        t.AllPermissions(), t.AllKeyspaces(), t.User(t.Identifier('user')))

    assert CQL3(
        'REVOKE ALL PERMISSIONS ON KEYSPACE keyspace FROM user'
    ).revoke() == t.Revoke(
        t.AllPermissions(),
        t.Keyspace(t.Identifier('keyspace')),
        t.User(t.Identifier('user')))

    assert CQL3(
        'REVOKE ALL PERMISSIONS ON TABLE keyspace.table FROM user'
    ).revoke() == t.Revoke(
        t.AllPermissions(),
        t.Table(t.Identifier('table'),
                t.Keyspace(t.Identifier('keyspace'))),
        t.User(t.Identifier('user')))


@pytest.mark.parametrize(
    ('permission',),
    [('CREATE',), ('ALTER',), ('DROP',),
     ('SELECT',), ('MODIFY',), ('AUTHORIZE',)])
def test_REVOKE_PERMISSION(permission):
    assert CQL3(
        'REVOKE {0} ON TABLE keyspace.table FROM user'.format(permission)
    ).revoke() == t.Revoke(
        t.Permission(permission),
        t.Table(t.Identifier('table'),
                t.Keyspace(t.Identifier('keyspace'))),
        t.User(t.Identifier('user')))

    assert CQL3(
        'REVOKE {0} PERMISSION ON TABLE '
        'keyspace.table FROM user'.format(permission)
    ).revoke() == t.Revoke(
        t.Permission(permission),
        t.Table(t.Identifier('table'), t.Keyspace(t.Identifier('keyspace'))),
        t.User(t.Identifier('user')))


def test_GRANT():
    assert CQL3('GRANT ALL ON ALL KEYSPACES TO user').grant() == t.Grant(
        t.AllPermissions(), t.AllKeyspaces(), t.User(t.Identifier('user')))

    assert CQL3(
        'GRANT ALL PERMISSIONS ON KEYSPACE keyspace TO user'
    ).grant() == t.Grant(
        t.AllPermissions(),
        t.Keyspace(t.Identifier('keyspace')),
        t.User(t.Identifier('user')))

    assert CQL3(
        'GRANT ALL PERMISSIONS ON TABLE keyspace.table TO user'
    ).grant() == t.Grant(
        t.AllPermissions(),
        t.Table(t.Identifier('table'),
                t.Keyspace(t.Identifier('keyspace'))),
        t.User(t.Identifier('user')))


@pytest.mark.parametrize(
    ('permission',),
    [('CREATE',), ('ALTER',), ('DROP',),
     ('SELECT',), ('MODIFY',), ('AUTHORIZE',)])
def test_GRANT_PERMISSION(permission):
    assert CQL3(
        'GRANT {0} ON TABLE keyspace.table TO user'.format(permission)
    ).grant() == t.Grant(
        t.Permission(permission),
        t.Table(t.Identifier('table'),
                t.Keyspace(t.Identifier('keyspace'))),
        t.User(t.Identifier('user')))

    assert CQL3(
        'GRANT {0} PERMISSION ON TABLE '
        'keyspace.table TO user'.format(permission)
    ).grant() == t.Grant(
        t.Permission(permission),
        t.Table(t.Identifier('table'), t.Keyspace(t.Identifier('keyspace'))),
        t.User(t.Identifier('user')))


def test_CREATE_USER():
    assert CQL3('CREATE USER username').create_user() == t.CreateUser(
        t.User(t.Identifier('username')), None, None)

    assert CQL3(
        'CREATE USER username SUPERUSER'
    ).create_user() == t.CreateUser(
        t.User(t.Identifier('username')), None, True)

    assert CQL3(
        'CREATE USER username NOSUPERUSER'
    ).create_user() == t.CreateUser(
        t.User(t.Identifier('username')), None, False)

    assert CQL3(
        "CREATE USER username WITH PASSWORD 'foo'"
    ).create_user() == t.CreateUser(
        t.User(t.Identifier('username')), 'foo', None)

    assert CQL3(
        "CREATE USER username WITH PASSWORD 'foo' SUPERUSER"
    ).create_user() == t.CreateUser(
        t.User(t.Identifier('username')), 'foo', True)

    assert CQL3(
        "CREATE USER username WITH PASSWORD 'foo' NOSUPERUSER"
    ).create_user() == t.CreateUser(
        t.User(t.Identifier('username')), 'foo', False)


def test_ALTER_USER():
    assert CQL3('ALTER USER username').alter_user() == t.AlterUser(
        t.User(t.Identifier('username')), None, None)

    assert CQL3('ALTER USER username SUPERUSER').alter_user() == t.AlterUser(
        t.User(t.Identifier('username')), None, True)

    assert CQL3('ALTER USER username NOSUPERUSER').alter_user() == t.AlterUser(
        t.User(t.Identifier('username')), None, False)

    assert CQL3(
        "ALTER USER username WITH PASSWORD 'foo'"
    ).alter_user() == t.AlterUser(
        t.User(t.Identifier('username')), 'foo', None)

    assert CQL3(
        "ALTER USER username WITH PASSWORD 'foo' SUPERUSER"
    ).alter_user() == t.AlterUser(
        t.User(t.Identifier('username')), 'foo', True)

    assert CQL3(
        "ALTER USER username WITH PASSWORD 'foo' NOSUPERUSER"
    ).alter_user() == t.AlterUser(
        t.User(t.Identifier('username')), 'foo', False)


def test_CREATE_INDEX():
    assert CQL3(
        'CREATE INDEX ON table (column)'
    ).create_index() == t.CreateIndex(
        None,
        t.Table(t.Identifier('table'), None),
        t.Column(t.Identifier('column')))

    assert CQL3(
        'CREATE INDEX column_index ON table (column)'
    ).create_index() == t.CreateIndex(
        t.Index(t.Identifier('column_index')),
        t.Table(t.Identifier('table'), None),
        t.Column(t.Identifier('column')))


def test_CREATE_KEYSPACE():
    assert CQL3(
        "CREATE KEYSPACE ks "
        "WITH REPLICATION = { 'class' : 'SimpleStrategy', "
        "'replication_factor': '1' }"
    ).create_keyspace() == t.CreateKeyspace(
        t.Keyspace(t.Identifier('ks')),
        t.Properties([
            t.Property(t.Identifier('replication'),
                       {'class': 'SimpleStrategy',
                        'replication_factor': '1'})]))


def test_ALTER_KEYSPACE():
    assert CQL3(
        "ALTER KEYSPACE ks "
        "WITH REPLICATION = { 'class' : 'SimpleStrategy', "
        "'replication_factor': '1' }"
    ).alter_keyspace() == t.AlterKeyspace(
        t.Keyspace(t.Identifier('ks')),
        t.Properties([
            t.Property(t.Identifier('replication'),
                       {'class': 'SimpleStrategy',
                        'replication_factor': '1'})]))


def test_INSERT():
    assert CQL3(
        "INSERT INTO foo (bar, baz) VALUES (?, 'foo')"
    ).insert() == t.Insert(
        t.Table(t.Identifier('foo'), None),
        [t.Column(t.Identifier('bar')), t.Column(t.Identifier('baz'))],
        [t.Binding(), 'foo'],
        [])

    assert CQL3(
        "INSERT INTO foo (bar, baz) VALUES (?, 'foo') "
        "USING TIMESTAMP 100000000"
    ).insert() == t.Insert(
        t.Table(t.Identifier('foo'), None),
        [t.Column(t.Identifier('bar')), t.Column(t.Identifier('baz'))],
        [t.Binding(), 'foo'],
        [t.Timestamp(100000000)])
