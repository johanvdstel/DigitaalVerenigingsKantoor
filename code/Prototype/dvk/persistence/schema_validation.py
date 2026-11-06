"""Validate historical SQLite contracts without touching application records.

SQLite itself derives the version-specific reference from the immutable migration
sequence in a separate in-memory database. No repair SQL runs on the real database.
"""
from __future__ import annotations

from contextlib import closing
from functools import lru_cache
import re
import sqlite3


VERSION_TABLE_SQL = "CREATE TABLE schema_version (version INTEGER PRIMARY KEY)"


class SchemaValidationError(sqlite3.OperationalError):
    """A recorded DVK schema cannot safely be used or migrated."""


def _sql_tokens(sql):
    """Ignore formatting/identifier quoting, preserve literal values and SQL body."""
    if sql is None:
        return None
    tokens = re.findall(r"'(?:''|[^'])*'|\"(?:\"\"|[^\"])*\"|`(?:``|[^`])*`|\[[^\]]*\]|\w+|[^\s]", sql)
    return tuple(token if token.startswith("'") else
                 token[1:-1].replace(token[0] * 2, token[0]).casefold()
                 if token.startswith(('"', '`', '[')) else token.casefold()
                 for token in tokens if token != ';')


def _objects(connection):
    return {(kind, name): (table, _sql_tokens(sql)) for kind, name, table, sql in
            connection.execute("SELECT type, name, tbl_name, sql FROM main.sqlite_master")
            if not name.startswith("sqlite_")}


def _pragma(connection, pragma, name):
    # Names come from schema metadata, never SQL fragments. Quote even unexpected
    # names; no raw definition or record value is included in diagnostic messages.
    quoted = '"' + name.replace('"', '""') + '"'
    return tuple(tuple(row) for row in connection.execute(f"PRAGMA main.{pragma}({quoted})"))


def _table_signature(connection, name):
    columns = tuple((cid, column, kind.upper(), required, _sql_tokens(default), pk, hidden)
                    for cid, column, kind, required, default, pk, hidden in
                    _pragma(connection, "table_xinfo", name))
    indexes = {}
    for _, index, unique, origin, partial in _pragma(connection, "index_list", name):
        indexes[index] = (unique, origin, partial, _pragma(connection, "index_xinfo", index))
    return columns, _pragma(connection, "foreign_key_list", name), indexes


@lru_cache(maxsize=32)
def _reference(migrations, version):
    """Only immutable historical DDL produces a reference, never caller data."""
    with closing(sqlite3.connect(":memory:")) as reference:
        reference.execute("PRAGMA foreign_keys=ON")
        reference.execute("BEGIN")
        reference.execute(VERSION_TABLE_SQL)
        for step, migration in enumerate(migrations[:version], 1):
            migration(reference)
            reference.execute("INSERT INTO schema_version VALUES (?)", (step,))
        objects = _objects(reference)
        tables = {name: _table_signature(reference, name)
                  for kind, name in objects if kind == "table"}
        return objects, tables


def _validate_table(connection, name, expected, actual_objects, expected_objects):
    if ("table", name) not in actual_objects:
        # Preserve the existing UI's missing-schema error boundary, without
        # modifying that UI or pretending other schema errors are missing tables.
        raise SchemaValidationError(f"no such table: {name}; DVK-schema onvolledig, initialisatie gestopt")
    columns, foreign_keys, indexes = _table_signature(connection, name)
    if columns != expected[0]:
        actual_columns = {column[1]: column for column in columns}
        for column in expected[0]:
            if column[1] not in actual_columns:
                raise SchemaValidationError(f"no such column: {name}.{column[1]}; verplichte DVK-kolom ontbreekt, initialisatie gestopt")
        for column in expected[0]:
            if actual_columns[column[1]] != column:
                raise SchemaValidationError(f"DVK-schema: kolomdefinitie van {name}.{column[1]} wijkt af; initialisatie gestopt")
        raise SchemaValidationError(f"DVK-schema: kolommen of kolomdefinities van {name} wijken af; initialisatie gestopt")
    if foreign_keys != expected[1]:
        raise SchemaValidationError(f"DVK-schema: foreign-key-definities van {name} wijken af; initialisatie gestopt")
    for index, signature in expected[2].items():
        if indexes.get(index) != signature:
            raise SchemaValidationError(f"DVK-schema: vereiste index of uniciteitsbeperking {index} ontbreekt of wijkt af; initialisatie gestopt")
    if actual_objects[("table", name)] != expected_objects[("table", name)]:
        raise SchemaValidationError(f"DVK-schema: tabeldefinitie van {name} wijkt af; initialisatie gestopt")


def registered_version(connection, migrations, latest):
    objects = _objects(connection)
    if ("table", "schema_version") not in objects:
        # An empty schema after earlier DDL is not evidence of a new database:
        # its missing tables may have contained data. SQLite's own schema counter
        # is only used for this distinction, not as a DVK migration version.
        if objects or connection.execute("PRAGMA main.schema_version").fetchone()[0] != 0:
            raise SchemaValidationError("DVK-schema: schema_version ontbreekt bij een bestaande structuur; initialisatie gestopt")
        return 0
    expected_objects, expected_tables = _reference(migrations, 0)
    _validate_table(connection, "schema_version", expected_tables["schema_version"], objects, expected_objects)
    values = tuple(row[0] for row in connection.execute("SELECT version FROM main.schema_version ORDER BY version"))
    if not values:
        if set(objects) != {("table", "schema_version")}:
            raise SchemaValidationError("DVK-schema: lege versieadministratie bij een bestaande structuur; initialisatie gestopt")
        return 0
    if any(type(value) is not int or value < 1 for value in values):
        raise SchemaValidationError("DVK-schema: ongeldige schemaversieadministratie; initialisatie gestopt")
    if values[-1] > latest:
        raise SchemaValidationError(f"DVK-schema: toekomstige schemaversie {values[-1]}, maximaal ondersteund is {latest}; initialisatie gestopt")
    if values != tuple(range(1, values[-1] + 1)):
        raise SchemaValidationError("DVK-schema: schemaversieadministratie bevat ontbrekende stappen; initialisatie gestopt")
    return values[-1]


def validate_schema(connection, version, migrations):
    expected_objects, tables = _reference(migrations, version)
    actual_objects = _objects(connection)
    for name, signature in tables.items():
        _validate_table(connection, name, signature, actual_objects, expected_objects)
    for (kind, name), signature in expected_objects.items():
        if kind in {"index", "trigger"} and actual_objects.get((kind, name)) != signature:
            raise SchemaValidationError(f"DVK-schema: vereiste {kind} {name} ontbreekt of wijkt af; initialisatie gestopt")
    values = tuple(row[0] for row in connection.execute("SELECT version FROM main.schema_version ORDER BY version"))
    if values != tuple(range(1, version + 1)):
        raise SchemaValidationError("DVK-schema: versieadministratie past niet bij de migratiestap; initialisatie gestopt")
