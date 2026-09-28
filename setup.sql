-- Run as the same Oracle user used by reproduce.py.
-- This object has the same column count, order, and Oracle data types as the
-- source object used by the application that exposed oracle/python-oracledb#607.

CREATE TABLE A00 (
    A01 VARCHAR2(30 BYTE) NOT NULL,
    A02 VARCHAR2(64 BYTE),
    A03 VARCHAR2(3 BYTE),
    A04 VARCHAR2(1 BYTE),
    A05 NUMBER(24, 4),
    A06 NUMBER(24, 4),
    A07 NUMBER(24, 4),
    A08 VARCHAR2(900 BYTE),
    A09 NUMBER(24, 4),
    A10 TIMESTAMP(6)
);

INSERT /*+ APPEND */ INTO A00
SELECT
    '000000000000000000000000000001',
    LPAD(TO_CHAR(LEVEL), 64, '0'),
    'EUR',
    'A',
    CAST(MOD(LEVEL, 100000) / 10000 AS NUMBER(24, 4)),
    CAST(MOD(LEVEL, 200000) / 10000 AS NUMBER(24, 4)),
    CAST(MOD(LEVEL, 300000) / 10000 AS NUMBER(24, 4)),
    RPAD('X', MOD(LEVEL, 900) + 1, 'X'),
    CAST(MOD(LEVEL, 400000) / 10000 AS NUMBER(24, 4)),
    TIMESTAMP '2026-01-01 00:00:00.000000'
        + NUMTODSINTERVAL(LEVEL, 'SECOND')
        + NUMTODSINTERVAL(MOD(LEVEL, 1000000) / 1000000, 'SECOND')
FROM DUAL
CONNECT BY LEVEL <= 50000;

COMMIT;

BEGIN
    DBMS_STATS.GATHER_TABLE_STATS(USER, 'A00');
END;
/

SELECT
    column_id,
    column_name,
    data_type,
    data_length,
    data_precision,
    data_scale,
    nullable
FROM user_tab_columns
WHERE table_name = 'A00'
ORDER BY column_id;
