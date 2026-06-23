#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Repair api_operation rows corrupted by invalid Liquibase update where syntax."""
import pymysql

HOST = "172.16.3.32"
USER = "secure"
PASSWORD = "8STRYXLCtn8"
DB = "open_api"

ROWS = [
    ("createTask", "DEPRECATED",
     "\u521b\u5efa\u626b\u63cf\u4efb\u52a1\uff08\u5df2\u5e9f\u5f03\uff0c\u8bf7\u7528 createTaskByJson/createTaskByFile\uff09", "tasks"),
    ("listTasks", "PUBLISHED", "\u5206\u9875\u67e5\u8be2\u4efb\u52a1\u5217\u8868", "tasks"),
    ("getTask", "PUBLISHED", "\u67e5\u8be2\u4efb\u52a1\u8fdb\u5ea6", "tasks"),
    ("issuePartnerToken", "PUBLISHED", "\u83b7\u53d6 Partner \u8bbf\u95ee\u4ee4\u724c", "auth"),
    ("searchInstances", "PUBLISHED", "\u5206\u9875\u641c\u7d22\u6f0f\u6d1e\u5b9e\u4f8b", "instances"),
    ("getInstance", "PUBLISHED", "\u83b7\u53d6\u6f0f\u6d1e\u5b9e\u4f8b\u8be6\u60c5", "instances"),
    ("verifyInstance", "PUBLISHED", "\u9a8c\u8bc1\u6f0f\u6d1e\u5b9e\u4f8b", "instances"),
    ("verifyInstanceBatch", "PUBLISHED", "\u6279\u91cf\u9a8c\u8bc1\u6f0f\u6d1e\u5b9e\u4f8b", "instances"),
    ("remediateInstance", "PUBLISHED", "\u5904\u7f6e\u00b7\u4fee\u590d\uff08\u53ef\u4fee\u590d\uff09", "instances"),
    ("archiveInstance", "PUBLISHED", "\u5904\u7f6e\u00b7\u5907\u6848\uff08\u4e0d\u53ef\u4fee\u590d\uff09", "instances"),
    ("verifyFixInstance", "PUBLISHED", "\u4fee\u590d\u6838\u9a8c\uff08\u5355\u6761\uff09", "instances"),
    ("verifyFixInstanceBatch", "PUBLISHED", "\u6279\u91cf\u4fee\u590d\u6838\u9a8c", "instances"),
    ("archiveInstanceLegacy", "DEPRECATED", "\u5904\u7f6e\u00b7\u5907\u6848\uff08\u517c\u5bb9\u522b\u540d\uff09", "instances"),
    ("getExport", "PUBLISHED", "\u67e5\u8be2\u5916\u53d1\u5305\u5143\u6570\u636e", "exports"),
    ("downloadExport", "PUBLISHED", "\u4e0b\u8f7d\u5916\u53d1\u6587\u4ef6", "exports"),
    ("listTaskExports", "PUBLISHED", "\u67e5\u8be2\u4efb\u52a1\u4e0b\u7684\u5916\u53d1\u8bb0\u5f55", "exports"),
    ("receivePlatformWebhook", "PUBLISHED", "\u5e73\u53f0\u4e8b\u4ef6\u56de\u8c03\uff08Partner \u5b9e\u73b0\uff09", "webhooks"),
    ("createTaskByJson", "PUBLISHED", "\u521b\u5efa\u626b\u63cf\u4efb\u52a1\uff08JSON \u53c2\u6570\uff09", "tasks"),
    ("createTaskByFile", "PUBLISHED", "\u521b\u5efa\u626b\u63cf\u4efb\u52a1\uff08XML \u914d\u7f6e\uff09", "tasks"),
    ("createTaskByUpload", "PUBLISHED", "\u521b\u5efa\u626b\u63cf\u4efb\u52a1\uff08\u4e0a\u4f20 XML \u6587\u4ef6\uff09", "tasks"),
]


def main():
    conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, database=DB, charset="utf8mb4")
    cur = conn.cursor()
    for op_id, status, summary, tag in ROWS:
        cur.execute(
            "UPDATE api_operation SET status=%s, summary=%s, openapi_tag=%s WHERE operation_id=%s",
            (status, summary, tag, op_id),
        )
        print(f"fixed {op_id} -> {status}")
    conn.commit()
    conn.close()
    print("repair done.")


if __name__ == "__main__":
    main()
