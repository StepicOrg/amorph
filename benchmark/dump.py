import json
from argparse import ArgumentParser
from operator import methodcaller

import pandas as pd
from tqdm import tqdm

from amorph import patch_with_sample, Method
from amorph.utils import find_closest
from benchmark.utils import cut_data
from benchmark.validators import csv_file, existing_place, method, positive_int

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('data', help='Path to CSV data file', type=csv_file)
    parser.add_argument('save', help='Path to save dump in', type=existing_place)
    parser.add_argument('--method', help='Method for patching', type=method, default=Method.DIFF)
    parser.add_argument('--limit', help='Number of samples to process', type=positive_int, default=10)
    parser.add_argument('--format', help='Dump format', type=str, choices=['csv', 'json'], default='csv')
    args = parser.parse_args()

    correct = cut_data(args.data, status='correct')
    wrong = cut_data(args.data, status='wrong', limit=args.limit)

    result = []
    for source in tqdm(wrong):
        matched = find_closest(source, correct)
        patches = patch_with_sample(source, matched, args.method)

        patches_data = None
        if args.format == 'csv':
            patches_data = '\n'.join(map(str, patches))
        elif args.format == 'json':
            patches_data = list(map(methodcaller('to_dict'), patches))

        result.append({
            'code': source,
            'matched': matched,
            'feedback': patches_data
        })

    if args.format == 'csv':
        pd.DataFrame(result).to_csv(args.save)
    elif args.format == 'json':
        with open(args.save, 'w') as f:
            f.write(json.dumps(result))
