import os
from argparse import ArgumentParser
from timeit import default_timer as timer

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from tqdm import tqdm

from amorph import patch_with_sample, Method
from amorph.utils import find_closest
from benchmark.metrics import (AddOpsPerSubmission, DeleteOpsPerSubmission, TotalOpsPerSubmission,
                               PatchesPerSubmission, AddOpsPerPatch, DeleteOpsPerPatch, TotalOpsPerPatch,
                               TotalRatioPerSubmission, SearchTimeMetric, PatchTimeMetric, TotalTimeMetric,
                               TimeMetric, RelativeMetric)
from benchmark.utils import cut_data, format_lines, format_filename, float_zeros_width
from benchmark.validators import csv_file, existing_dir, positive_int


class Benchmarker(object):
    MAX_COL_LENGTH = 9
    MAX_NUM_LENGTH = 4

    def __init__(self, correct_batches, metrics):
        self.correct_batches = correct_batches
        self.metrics = metrics

    def report(self, wrong_batch, methods, save_path):
        chart = {}
        for metric in self.metrics:
            chart[metric.name] = {method: [] for method in methods}

        hmap = {}
        for method in methods:
            hmap[method] = {metric.name: [] for metric in self.metrics}

        for batch in tqdm(self.correct_batches):
            registry = {}
            for method in methods:
                registry[method] = [metric() for metric in self.metrics]

            for source in wrong_batch:
                start = timer()
                matched = find_closest(source, batch)
                search_time = timer() - start

                for method in methods:
                    start = timer()
                    patches = list(patch_with_sample(source, matched, method))
                    patch_time = timer() - start

                    for metric in registry[method]:
                        if isinstance(metric, TimeMetric):
                            metric.update_search(search_time)
                            metric.update_patch(patch_time)
                        elif isinstance(metric, RelativeMetric):
                            metric.update_relative(source, matched, patches)
                        else:
                            metric.update(patches)

            for method, records in registry.items():
                for record in records:
                    chart[record.name][method].append((len(batch), record.value))
                    hmap[method][record.name].append((len(batch), record.value))

        for metric_type, data in chart.items():
            fig = plt.figure()
            fig.suptitle('{}\n({} wrong samples)'.format(metric_type, len(wrong_batch)))

            for method, mapping in data.items():
                ordered = sorted(mapping)
                x, y = zip(*ordered)

                plt.plot(x, y, '-o', label=method.value)
                plt.xscale('log')
                plt.xlabel('count of correct submissions used')
                plt.ylabel(metric_type)
                plt.legend()

            plt.grid()
            filename = format_filename('{}.png'.format(metric_type))
            file_path = os.path.join(save_path, filename)
            plt.savefig(file_path, bbox_inches='tight')

        for method, data in hmap.items():
            length = len(data)

            fig_width = int(1.3 * len(self.metrics))
            fig_height = max(5, len(self.correct_batches))
            fig = plt.figure(figsize=(fig_width, fig_height))
            fig.suptitle('{}\n({} wrong samples)'.format(method.value, len(wrong_batch)))
            grid = gridspec.GridSpec(1, length)
            grid.update(wspace=0)

            for idx, metric in enumerate(self.metrics):
                plt.subplot(grid[idx])
                ordered = sorted(data[metric.name], reverse=True)
                x, y = zip(*ordered)

                widths = list(map(float_zeros_width, y))
                covering_width = max(widths)
                if min(widths) > Benchmarker.MAX_NUM_LENGTH:
                    fmt_width = 0
                else:
                    fmt_width = min(Benchmarker.MAX_NUM_LENGTH, covering_width)

                ax = sns.heatmap(np.array(y).reshape((-1, 1)),
                                 xticklabels=[format_lines(metric.name, Benchmarker.MAX_COL_LENGTH)],
                                 yticklabels=x if idx == 0 else False,
                                 annot=True,
                                 cbar=(idx == length-1),
                                 fmt='.{}f'.format(fmt_width),
                                 linewidths=0.5,
                                 center=np.mean(y))
                if idx == 0:
                    plt.ylabel('count of correct submissions used')
                    plt.yticks(va='center')

                if idx == length-1:
                    cbar = ax.collections[0].colorbar
                    cbar.set_ticks([np.min(y), np.max(y)])
                    cbar.set_ticklabels(['low', 'high'])

            filename = format_filename('{}.png'.format(method.value))
            file_path = os.path.join(save_path, filename)
            plt.savefig(file_path, bbox_inches='tight')

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('data', help='Path to CSV data file', type=csv_file)
    parser.add_argument('save', help='Path to save reports into', type=existing_dir)
    parser.add_argument('--limit', help='Number of samples to process', type=positive_int, default=10)
    args = parser.parse_args()

    bench = Benchmarker([
        cut_data(args.data, status='correct', limit=0.001),
        cut_data(args.data, status='correct', limit=0.01),
        cut_data(args.data, status='correct', limit=0.1),
        cut_data(args.data, status='correct', limit=0.25),
        cut_data(args.data, status='correct', limit=0.5),
        cut_data(args.data, status='correct', limit=0.75),
        cut_data(args.data, status='correct')
    ], [
        AddOpsPerSubmission, DeleteOpsPerSubmission, TotalOpsPerSubmission,
        PatchesPerSubmission, TotalRatioPerSubmission,
        AddOpsPerPatch, DeleteOpsPerPatch, TotalOpsPerPatch,
        SearchTimeMetric, PatchTimeMetric, TotalTimeMetric
    ])
    bench.report(
        cut_data(args.data, status='wrong', limit=args.limit),
        list(Method),
        args.save
    )
