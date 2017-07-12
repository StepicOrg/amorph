# Amorph
Package for Python source code transformation.

## Installation
```bash
python setup.py install
```

## Patch search
Amorph provides two methods of getting patches for transforming source - diff-based approach and [AST](https://en.wikipedia.org/wiki/Abstract_syntax_tree) matching. Currently first is ready to use and matching is in a state of active development.

## Diff
```python
from amorph.diff import get_patches

source = '''
def f(a, b):
    return a + b
'''

target = '''
def f(a, b):
    return a + b + 5
'''

for patch in get_patches(source, target):
    print(patch)
```

### Patch types
Can be found under `amorph/diff/models.py`
