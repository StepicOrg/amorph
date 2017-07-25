import os
from argparse import ArgumentError

import pandas as pd

from amorph import Method


def csv_file(path):
    try:
        return pd.read_csv(path)
    except Exception as e:
        raise ArgumentError(str(e))


def positive_int(x):
    try:
        x = int(x)
    except ValueError:
        raise ArgumentError('non-numeric value passed')

    if x <= 0:
        raise ArgumentError('positive int needed')
    return x


def method(type):
    try:
        return Method(type)
    except ValueError as e:
        raise ArgumentError(str(e))


def existing_dir(path):
    if not os.path.isdir(path):
        raise ArgumentError('directory does not exist')
    return path


def existing_place(path):
    existing_dir(os.path.split(path)[0])
    return path
