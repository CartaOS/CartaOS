# -*- coding: utf-8 -*-
# backend/tests/test_config.py

import pathlib

import pytest

from cartaos import config


def test_root_dir_is_pathlib_path():
    """Test that ROOT_DIR is a pathlib.Path object."""
    assert isinstance(config.ROOT_DIR, pathlib.Path)


def test_all_paths_are_pathlib_paths():
    """Test that all top-level path constants are pathlib.Path objects."""
    for name in dir(config):
        if name.endswith("_DIR"):
            path = getattr(config, name)
            assert isinstance(path, pathlib.Path)


def test_pipeline_dirs_class():
    """Test that the PipelineDirs class initializes directories correctly."""
    pipeline_dirs = config.PIPELINE_DIRS.pipeline_dirs
    assert isinstance(pipeline_dirs, dict)
    # Check that all defined stages are present
    for stage in config.PIPELINE_STAGES:
        assert stage in pipeline_dirs
        assert isinstance(pipeline_dirs[stage], pathlib.Path)


def test_pipeline_dirs_paths_are_correct():
    """Test that pipeline directory paths are constructed correctly."""
    pipeline_dirs = config.PIPELINE_DIRS.pipeline_dirs
    for stage_name, stage_path in pipeline_dirs.items():
        assert stage_path == config.ROOT_DIR / stage_name
