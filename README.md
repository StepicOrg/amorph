# Amorph
Package for Python source code transformation.

```python
>>> from amorph import patch_with_closest
>>> source = '''
... def f(a, b):
...    return a + b
... '''
>>> samples = [
... '''
... def f(a, b):
...    return a * b
... ''',
... '''
... def f(a, b):
...    return sum([a for i in range(b)])
... '''
... ]
>>> for patch in patch_with_closest(source, samples):
...     print(patch)
Replace char #26 with '*'
```

## Use cases

### Patch with given sample
```python
from amorph import patch_with_sample

patches = patch_with_sample(source, sample)
```

### Specify patch method
Currently `diff`, `tokens` and `ast` methods available.
To use `ast` patching you should run the [API server](https://github.com/laplab/amorph-java) first.
```python
from amorph import patch_with_closest, patch_with_sample, Method

patches = patch_with_sample(source, sample, method=Method.DIFF)
patches = patch_with_closest(source, samples, method=Method.DIFF)
```

### Find closest code
```python
from amorph.utils import find_closest

closest_sample = find_closest(source, sample)
```

### Custom metric
```python
from amorph import patch_with_closest
from amorph.utils import find_closest

def dummy_metric(source, sample):
    return source.count('def') - sample.count('def')

closest_sample = find_closest(source, samples, metric=dummy_metric)
patches = patch_with_closest(source, samples, metric=dummy_metric)
```

### Nested objects
```python
from amorph import patch_with_closest, patch_with_sample
from amorph.utils import find_closest
from operator import itemgetter

source = {'code': 'print(input())'}
samples = [{'code': 'print("Hello World!")'}, {'code': 'print("Bye Bye!")'}]
get_code = itemgetter('code')

closest = find_closest(source, samples, key=get_code)
patches = patch_with_sample(source, closest, key=get_code)
patches = patch_with_closest(source, samples, key=get_code)
```
