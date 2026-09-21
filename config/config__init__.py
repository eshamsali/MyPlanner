import pymysql

# Django's MySQL backend expects the mysqlclient package (which needs a C
# compiler to build on Windows and often has no pre-built wheel for brand-new
# Python versions — the same wheel problem you hit before with Pillow/psycopg
# on 3.14). PyMySQL is pure Python and always installs cleanly, so this shim
# makes it masquerade as mysqlclient for Django's benefit.
pymysql.install_as_MySQLdb()
pymysql.version_info = (1, 4, 6, "final", 0)  # satisfies Django's version check