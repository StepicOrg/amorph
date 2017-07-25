from argparse import ArgumentParser
from benchmark.validators import existing_dir
from os.path import join, split
from glob import glob
import pandas as pd
import ast
import logging as log

log.basicConfig(level=log.INFO)


def runnable(row):
    try:
        ast.parse(row['code'])
        return True
    except Exception:
        return False

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('source',
                        help='Directory containing dumps of submissions',
                        type=existing_dir)
    parser.add_argument('result',
                        help='Directory to store results',
                        type=existing_dir)
    args = parser.parse_args()

    mask = join(args.source, '*.csv')
    for file_path in glob(mask):
        _, filename = split(file_path)

        df = pd.read_csv(file_path).loc[:, ['status', 'code']]
        valid = df.apply(runnable, axis=1)
        cleaned = df[valid]

        log.info('file "{}"... filtered {} item(s)'.format(filename,
                                                           df.shape[0]-cleaned.shape[0]))

        cleaned.to_csv(join(args.result, filename))
