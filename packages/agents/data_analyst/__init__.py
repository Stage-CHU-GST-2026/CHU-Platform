"""Data Analyst agent — configuration only.

This is NOT a framework. It only configures the generic AI framework
with a prompt, a tool list, and model settings.
"""

from .agent import create_data_analyst

__all__ = ["create_data_analyst"]
