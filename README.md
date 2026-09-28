# Reproducer for oracle/python-oracledb issue 607

This is a self-contained reproducer for a SIGSEGV in thin-mode
`AsyncConnection.fetch_df_batches()`. It was extracted from the application
query that exposed [oracle/python-oracledb#607](https://github.com/oracle/python-oracledb/issues/607).
Names and values are synthetic; the source object's 10-column order and Oracle
data types are preserved.

## Observed environment

- python-oracledb 26.0.1, thin mode (`init_oracle_client()` is not called)
- Python 3.14.7, 64 bit
- PyArrow 25.0.1
- Linux x86_64, glibc 2.41

The application query reads all ten source columns. `A01` is the repeated,
non-null `VARCHAR2(30)` key and `A10` is `TIMESTAMP(6)`. The crash occurs while
awaiting the first async dataframe batch, before `pyarrow.table()` is called.
The equivalent synchronous dataframe fetch and ordinary async cursor fetch are
controls and complete successfully in the affected environment.

## Run

Use a disposable Oracle schema. Run `setup.sql` with SQL*Plus or SQLcl, then:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt

export ORACLE_USER='user'
export ORACLE_PASSWORD='password'
export ORACLE_DSN='host:1521/service'

python -X faulthandler reproduce.py async-dataframe
echo $?
```

On the affected setup, output stops after
`before first async dataframe batch`; the interpreter receives SIGSEGV and the
shell normally reports status 139. No Python exception is raised.

Run the controls in separate processes:

```sh
python reproduce.py sync-dataframe
python reproduce.py async-cursor
```

Expected control output reports 50,000 rows in each case. Expected driver
behavior is for the async dataframe fetch to return the same values as the
synchronous fetch, or to raise a Python exception; it must not terminate the
interpreter.

## Cleanup

```sql
DROP TABLE A00 PURGE;
```
