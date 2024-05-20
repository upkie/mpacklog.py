#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2024 Inria

"""Utility functions."""


def format_value(value) -> str:
    """Format incoming values for the Values column.

    Args:
        value: Value to format as a string.

    Returns:
        Value formatted as a string.
    """
    return f"{value:.2g}" if isinstance(value, float) else str(value)
