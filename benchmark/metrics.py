from amorph.models import DeletePatch, InsertPatch, ReplacePatch


class Metric(object):
    def update(self, patches):
        raise NotImplementedError

    @property
    def value(self):
        raise NotImplementedError


class PatchCountMetric(Metric):
    name = 'total count of patches'

    def __init__(self):
        self.total = 0

    def update(self, patches):
        self.total += len(patches)

    @property
    def value(self):
        return self.total


class SubmissionsCountMetric(Metric):
    name = 'count of submissions'

    def __init__(self):
        self.total = 0

    def update(self, patches):
        self.total += 1

    @property
    def value(self):
        return self.total


class AddOpsMetric(Metric):
    name = 'total count of additions'

    def __init__(self):
        self.total = 0

    def update(self, patches):
        for patch in patches:
            if isinstance(patch, (InsertPatch, ReplacePatch)):
                self.total += len(patch.piece)
    
    @property
    def value(self):
        return self.total


class DeleteOpsMetric(Metric):
    name = 'total count of deletions'

    def __init__(self):
        self.total = 0

    def update(self, patches):
        for patch in patches:
            if isinstance(patch, (DeletePatch, ReplacePatch)):
                self.total += patch.end - patch.start

    @property
    def value(self):
        return self.total


class TotalOpsMetric(Metric):
    name = 'total count of corrections'

    def __init__(self):
        self.add = AddOpsMetric()
        self.delete = DeleteOpsMetric()

    def update(self, patches):
        self.add.update(patches)
        self.delete.update(patches)

    @property
    def value(self):
        return self.add.value + self.delete.value


class AddOpsPerSubmission(Metric):
    name = 'count of additions per submission'

    def __init__(self):
        self.add = AddOpsMetric()
        self.total = SubmissionsCountMetric()

    def update(self, patches):
        self.add.update(patches)
        self.total.update(patches)

    @property
    def value(self):
        return self.add.value / self.total.value


class DeleteOpsPerSubmission(Metric):
    name = 'count of deletions per submission'

    def __init__(self):
        self.delete = DeleteOpsMetric()
        self.total = SubmissionsCountMetric()

    def update(self, patches):
        self.delete.update(patches)
        self.total.update(patches)

    @property
    def value(self):
        return self.delete.value / self.total.value


class TotalOpsPerSubmission(Metric):
    name = 'count of corrections per submission'

    def __init__(self):
        self.ops = TotalOpsMetric()
        self.total = SubmissionsCountMetric()

    def update(self, patches):
        self.ops.update(patches)
        self.total.update(patches)

    @property
    def value(self):
        return self.ops.value / self.total.value


class PatchesPerSubmission(Metric):
    name = 'count of patches per submission'

    def __init__(self):
        self.patches = PatchCountMetric()
        self.total = SubmissionsCountMetric()

    def update(self, patches):
        self.patches.update(patches)
        self.total.update(patches)

    @property
    def value(self):
        return self.patches.value / self.total.value


class AddOpsPerPatch(Metric):
    name = 'count of additions per patch'

    def __init__(self):
        self.add = AddOpsMetric()
        self.total = PatchCountMetric()

    def update(self, patches):
        self.add.update(patches)
        self.total.update(patches)

    @property
    def value(self):
        return self.add.value / self.total.value


class DeleteOpsPerPatch(Metric):
    name = 'count of deletions per patch'

    def __init__(self):
        self.delete = DeleteOpsMetric()
        self.total = PatchCountMetric()

    def update(self, patches):
        self.delete.update(patches)
        self.total.update(patches)

    @property
    def value(self):
        return self.delete.value / self.total.value


class TotalOpsPerPatch(Metric):
    name = 'count of corrections per patch'

    def __init__(self):
        self.ops = TotalOpsMetric()
        self.total = PatchCountMetric()

    def update(self, patches):
        self.ops.update(patches)
        self.total.update(patches)

    @property
    def value(self):
        return self.ops.value / self.total.value


class TimeMetric(object):
    def update_search(self, interval):
        raise NotImplementedError

    def update_patch(self, interval):
        raise NotImplementedError

    @property
    def value(self):
        raise NotImplementedError


class SearchTimeMetric(TimeMetric):
    name = 'search time in sec.'

    def __init__(self):
        self.time = 0
        self.total = 0

    def update_search(self, interval):
        self.time += interval
        self.total += 1

    def update_patch(self, interval):
        pass

    @property
    def value(self):
        return self.time / self.total


class PatchTimeMetric(TimeMetric):
    name = 'patches generation time in sec.'

    def __init__(self):
        self.time = 0
        self.total = 0

    def update_search(self, interval):
        pass

    def update_patch(self, interval):
        self.time += interval
        self.total += 1

    @property
    def value(self):
        return self.time / self.total


class TotalTimeMetric(TimeMetric):
    name = 'feedback generation time in sec.'

    def __init__(self):
        self.search = SearchTimeMetric()
        self.patch = PatchTimeMetric()

    def update_search(self, interval):
        self.search.update_search(interval)
        self.patch.update_search(interval)

    def update_patch(self, interval):
        self.search.update_patch(interval)
        self.patch.update_patch(interval)

    @property
    def value(self):
        return self.search.value + self.patch.value


class RelativeMetric(object):
    def update_relative(self, source, matched, patches):
        raise NotImplementedError

    @property
    def value(self):
        raise NotImplementedError


class TotalRatioPerSubmission(RelativeMetric):
    name = 'corrections ratio per submission'

    def __init__(self):
        self.total_ratio = 0
        self.total = SubmissionsCountMetric()

    def update_relative(self, source, matched, patches):
        tmp = TotalOpsMetric()
        tmp.update(patches)
        self.total_ratio += tmp.value / (len(source) + len(matched))
        self.total.update(patches)

    @property
    def value(self):
        return self.total_ratio / self.total.value
