#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 Stéphane Caron

import glob
import logging
import os
from typing import Optional


def find_log_file(log_path: Optional[str]) -> str:
    """Find log file to open.

    Args:
        log_file: Path to a directory or a specific log file.
    """
    if os.path.exists(log_path):
        if os.path.isfile(log_path):
            return log_path
    mpack_files = glob.glob(os.path.join(log_path, "*.mpack"))
    log_file = max(mpack_files, key=os.path.getmtime)
    logging.info(
        "Opening the most recent log in %s: %s",
        log_path,
        os.path.basename(log_file),
    )
    return log_file
