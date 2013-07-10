def _type(name, package='org.apache.cassandra.db.marshal'):
    return '{0}.{1}'.format(package, name)


native_types = {
    'ASCII': _type('AsciiType'),
    'BIGINT': _type('LongType'),
    'BLOB': _type('BytesType'),
    'BOOLEAN': _type('BooleanType'),
    'COUNTER': _type('CounterColumnType'),
    'DECIMAL': _type('DecimalType'),
    'DOUBLE': _type('DoubleType'),
    'FLOAT': _type('FloatType'),
    'INET': _type('InetAddressType'),
    'INT': _type('Int32Type'),
    'TEXT': _type('UTF8Type'),
    'TIMESTAMP': _type('DateType'),
    'UUID': _type('UUIDType'),
    'VARCHAR': _type('UTF8Type'),
    'VARINT': _type('IntegerType'),
    'TIMEUUID': _type('TimeUUIDType')
}
