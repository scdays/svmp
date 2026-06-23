#!/usr/bin/env py -3
# -*- coding: utf-8 -*-
"""兼容入口：请使用 import-nsfocus-xml-to-mock-bundle.py。"""
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).with_name("import-nsfocus-xml-to-mock-bundle.py")
raise SystemExit(subprocess.call([sys.executable, str(SCRIPT)] + sys.argv[1:]))
