def metric_with_key(metric):
    def new_metric(source, sample, key=None):
        if key:
            source = key(source)
            sample = key(sample)
        return metric(source, sample)
    return new_metric
