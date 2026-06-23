#!/usr/bin/env python3
"""Apply OP-MOCK-P1-DB DDL to open_api MySQL if columns missing."""
import pymysql

HOST = "172.16.3.32"
USER = "secure"
PASSWORD = "8STRYXLCtn8"
DB = "open_api"

OPEN_TASK_COLS = [
    ("instances_ingested", "BOOLEAN DEFAULT FALSE COMMENT 'Mock instances ingested'"),
    ("ingest_error", "VARCHAR(512) NULL COMMENT 'Mock ingest error'"),
]

OPEN_VULN_COLS = [
    ("task_id", "VARCHAR(64) NULL"),
    ("ext_task_id", "VARCHAR(128) NULL"),
    ("scan_template_id", "INT NULL"),
    ("report_template_id", "INT NULL"),
    ("bundle_id", "VARCHAR(64) NULL"),
    ("ingest_status", "VARCHAR(16) NULL"),
    ("ingest_at", "DATETIME NULL"),
]


def column_exists(cur, table, col):
    cur.execute(
        "SELECT COUNT(*) FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND COLUMN_NAME=%s",
        (DB, table, col),
    )
    return cur.fetchone()[0] > 0


def index_exists(cur, table, index):
    cur.execute(
        "SELECT COUNT(*) FROM information_schema.STATISTICS "
        "WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND INDEX_NAME=%s",
        (DB, table, index),
    )
    return cur.fetchone()[0] > 0


def main():
    conn = pymysql.connect(
        host=HOST, user=USER, password=PASSWORD, database=DB, charset="utf8mb4"
    )
    cur = conn.cursor()
    for col, ddl in OPEN_TASK_COLS:
        if not column_exists(cur, "open_task", col):
            cur.execute(f"ALTER TABLE open_task ADD COLUMN {col} {ddl}")
            print(f"open_task + {col}")
    if not index_exists(cur, "open_task", "idx_open_task_engine_task_id"):
        cur.execute(
            "CREATE INDEX idx_open_task_engine_task_id ON open_task (engine_task_id)"
        )
        print("index idx_open_task_engine_task_id")
    for col, ddl in OPEN_VULN_COLS:
        if not column_exists(cur, "open_vuln_instance", col):
            cur.execute(f"ALTER TABLE open_vuln_instance ADD COLUMN {col} {ddl}")
            print(f"open_vuln_instance + {col}")
    if not index_exists(cur, "open_vuln_instance", "idx_open_vuln_instance_partner_task"):
        cur.execute(
            "CREATE INDEX idx_open_vuln_instance_partner_task "
            "ON open_vuln_instance (partner_id, task_id)"
        )
        print("index idx_open_vuln_instance_partner_task")
    if not index_exists(cur, "open_vuln_instance", "idx_open_vuln_instance_partner_ext"):
        cur.execute(
            "CREATE INDEX idx_open_vuln_instance_partner_ext "
            "ON open_vuln_instance (partner_id, ext_task_id)"
        )
        print("index idx_open_vuln_instance_partner_ext")
    conn.commit()
    conn.close()
    print("DDL apply done.")


if __name__ == "__main__":
    main()
