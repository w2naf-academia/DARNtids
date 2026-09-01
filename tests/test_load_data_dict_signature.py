"""
The classification cache was removed (issue #8), so the parameters that drove it are gone.

The reason this has a test at all: the cache never wrote anything, because
``saveMusicArrayToHDF5()`` iterates ``dir(obj)`` and keeps only attributes that are dicts,
lists, or named ``DS*``/``active*``, and ``data_dict`` is a plain dict whose ``dir()``
returns methods. A cache hit would therefore have loaded ``None``, which the caller reports
as "no data for given time period" and exits successfully on. A caller left passing
``use_cache=True`` must now fail immediately instead of being quietly ignored.
"""
import inspect

import pytest

from darntids import classify


REMOVED = ['use_cache', 'cache_dir', 'read_only']


@pytest.mark.parametrize('param', REMOVED)
def test_removed_cache_parameters_are_gone_from_the_signature(param):
    assert param not in inspect.signature(classify.load_data_dict).parameters


def test_load_data_dict_has_no_kwargs_catch_all():
    """Without this, the removed parameters would be silently swallowed (issue #2)."""
    kinds = [p.kind for p in inspect.signature(classify.load_data_dict).parameters.values()]
    assert inspect.Parameter.VAR_KEYWORD not in kinds


@pytest.mark.parametrize('param', REMOVED)
def test_passing_a_removed_cache_parameter_raises(param):
    with pytest.raises(TypeError):
        classify.load_data_dict('some_list', 'some/path', **{param: True})


def test_classify_module_no_longer_imports_the_hdf5_writers():
    """Both were used only by the cache; leaving them imported invites the cache back."""
    src = inspect.getsource(classify)
    assert 'saveMusicArrayToHDF5' not in src
    assert 'loadMusicArrayFromHDF5' not in src
