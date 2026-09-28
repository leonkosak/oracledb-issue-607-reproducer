#!/usr/bin/env python3
"""Minimal reproducer for oracle/python-oracledb issue 607."""

import argparse
import asyncio
import faulthandler
import os
import platform
import sys

import oracledb
import pyarrow as pa


faulthandler.enable()

SQL = """
    SELECT A01, A02, A03, A04, A05, A06, A07, A08, A09, A10
    FROM A00
    ORDER BY A02
"""


def connection_parameters() -> dict[str, str]:
    names = ("ORACLE_USER", "ORACLE_PASSWORD", "ORACLE_DSN")
    missing = [name for name in names if not os.environ.get(name)]
    if missing:
        raise SystemExit("Missing environment variable(s): " + ", ".join(missing))
    return {
        "user": os.environ["ORACLE_USER"],
        "password": os.environ["ORACLE_PASSWORD"],
        "dsn": os.environ["ORACLE_DSN"],
    }


def print_environment() -> None:
    print(f"python={sys.version}", flush=True)
    print(f"python-oracledb={oracledb.__version__}", flush=True)
    print(f"pyarrow={pa.__version__}", flush=True)
    print(f"platform={platform.platform()}", flush=True)
    print(f"thin_mode={oracledb.is_thin_mode()}", flush=True)


async def async_dataframe_fetch() -> None:
    async with oracledb.connect_async(**connection_parameters()) as connection:
        batches = connection.fetch_df_batches(
            statement=SQL,
            size=50_000,
            fetch_decimals=True,
        )
        print("before first async dataframe batch", flush=True)
        dataframe = await anext(aiter(batches))
        print("after first async dataframe batch", flush=True)
        table = pa.table(dataframe)
        print(f"rows={table.num_rows}\nschema={table.schema}", flush=True)


def synchronous_dataframe_fetch() -> None:
    with oracledb.connect(**connection_parameters()) as connection:
        count = 0
        for dataframe in connection.fetch_df_batches(
            statement=SQL,
            size=50_000,
            fetch_decimals=True,
        ):
            count += pa.table(dataframe).num_rows
        print(f"synchronous rows={count}", flush=True)


async def async_row_fetch() -> None:
    async with oracledb.connect_async(**connection_parameters()) as connection:
        async with connection.cursor() as cursor:
            cursor.arraysize = 50_000
            cursor.prefetchrows = 50_000
            await cursor.execute(SQL)
            rows = await cursor.fetchmany(50_000)
            print(f"async cursor rows={len(rows)}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode",
        choices=("async-dataframe", "sync-dataframe", "async-cursor"),
    )
    args = parser.parse_args()
    print_environment()

    if args.mode == "async-dataframe":
        asyncio.run(async_dataframe_fetch())
    elif args.mode == "sync-dataframe":
        synchronous_dataframe_fetch()
    else:
        asyncio.run(async_row_fetch())


if __name__ == "__main__":
    main()
