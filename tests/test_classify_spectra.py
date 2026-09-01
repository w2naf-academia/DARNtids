"""
Tests for the spectral resampling that defines the MSTID index (issue #6).

The property under test is that a window's integrated spectrum belongs to that window
alone. It must not move when unrelated windows join or leave the list being processed,
because that is what lets the index be recomputed over a different date range from the
same MUSIC HDF5 files and still be comparable, window for window.

The defect these guard against was a silent one: ``DataFrame.interpolate()`` defaults to
``method='linear'``, documented as "Ignore the index and treat the values as equally
spaced", and it was being applied to the outer join of every window's native ``freqVec``,
which is not equally spaced. Nothing failed; the numbers just quietly depended on the list.
"""
import numpy as np
import pandas as pd
import pytest

from darntids.classify import FREQ_GRID_STEP_HZ, common_freq_grid, resample_spectra


F_MIN, F_MAX = -0.0083333333, 0.0083333333   # set by the 2 h window and 60 s interpolation


def spectrum_on(n_bins, seed=0):
    """A window's spectrum sampled on its own native grid of ``n_bins`` points.

    Native grid lengths genuinely vary across the archive (366 for most windows, about 10%
    at 363, with occasional 354, 204 and 183), which is what makes mixed lists the normal
    case rather than an edge case.
    """
    rng  = np.random.default_rng(seed)
    fvec = np.linspace(F_MIN, F_MAX, n_bins)
    # A smooth, positive spectrum plus a little structure, so interpolation error is
    # visible rather than washed out by noise.
    vals = 10.0 + np.exp(-(fvec / 0.002) ** 2) * 50.0 + rng.normal(0, 0.05, n_bins)
    return pd.Series(vals, fvec)


def joined(spectra):
    """Reproduce the outer join over native grids that load_data_dict() builds up."""
    df = None
    for name, s in spectra.items():
        s = s.rename(name)
        df = s.to_frame() if df is None else df.join(s, how='outer')
    return df


def int_spect(spect_df, fvec_new):
    """The integrated spectrum, as this_actually_does_the_sorting() computes it."""
    sd = resample_spectra(spect_df, fvec_new)
    return np.sum(sd[sd.index >= 0], axis=0)


class TestCommonFreqGrid:

    def test_grid_spans_the_requested_extent(self):
        g = common_freq_grid(F_MIN, F_MAX)
        assert g[0] == pytest.approx(round(F_MIN, 4))
        assert g[-1] == pytest.approx(round(F_MAX, 4))

    def test_step_is_the_named_constant(self):
        g = common_freq_grid(F_MIN, F_MAX)
        assert np.diff(g).mean() == pytest.approx(FREQ_GRID_STEP_HZ, rel=1e-2)

    def test_grid_does_not_depend_on_which_windows_span_the_extent(self):
        """f_min/f_max are fixed by the run parameters, so the grid must be too."""
        assert np.array_equal(common_freq_grid(F_MIN, F_MAX),
                              common_freq_grid(F_MIN, F_MAX))


class TestListIndependence:
    """The regression that matters. Each of these fails on the pre-#6 implementation."""

    def test_adding_a_window_on_another_grid_leaves_the_others_untouched(self):
        grid   = common_freq_grid(F_MIN, F_MAX)
        alone  = {f'w{i}': spectrum_on(366, seed=i) for i in range(6)}
        withal = dict(alone, odd=spectrum_on(354, seed=99))

        a = int_spect(joined(alone), grid)
        b = int_spect(joined(withal), grid).reindex(a.index)
        assert np.allclose(a.values, b.values, rtol=0, atol=0)

    def test_result_is_independent_of_list_size(self):
        """The lists must differ in which native grids they contain, not merely in length.

        Two lists drawn from the same set of grids share a union index and so agree even
        under the positional fill; only a list that widens the union discriminates.
        """
        grid    = common_freq_grid(F_MIN, F_MAX)
        targets = {f't{i}': spectrum_on(366, seed=100 + i) for i in range(3)}
        small   = dict(targets, **{f'w{i}': spectrum_on(366, seed=i) for i in range(2)})
        large   = dict(targets, **{f'w{i}': spectrum_on([366, 363, 354, 204][i % 4], seed=i)
                                   for i in range(40)})

        a = int_spect(joined(small), grid).reindex(list(targets))
        b = int_spect(joined(large), grid).reindex(list(targets))
        assert np.allclose(a.values, b.values, rtol=0, atol=0)

    def test_a_window_matches_being_resampled_entirely_on_its_own(self):
        """The strongest form: the list may as well not exist."""
        grid  = common_freq_grid(F_MIN, F_MAX)
        solo  = spectrum_on(366, seed=7)
        crowd = {'solo': solo}
        crowd.update({f'w{i}': spectrum_on(183, seed=i) for i in range(5)})

        one  = int_spect(joined({'solo': solo}), grid)['solo']
        many = int_spect(joined(crowd), grid)['solo']
        assert one == many

    def test_column_order_does_not_matter(self):
        grid = common_freq_grid(F_MIN, F_MAX)
        spectra = {'a': spectrum_on(366, seed=1), 'b': spectrum_on(363, seed=2),
                   'c': spectrum_on(204, seed=3)}
        fwd = int_spect(joined(spectra), grid)
        rev = int_spect(joined(dict(reversed(list(spectra.items())))), grid)
        assert np.allclose(fwd.reindex(['a', 'b', 'c']).values,
                           rev.reindex(['a', 'b', 'c']).values, rtol=0, atol=0)


class TestResampleFidelity:

    def test_interpolation_is_in_frequency_not_position(self):
        """A linear ramp must come back linear in f. The positional default did not.

        The expectation is evaluated against the ramp's own definition rather than against
        the grid endpoints, because common_freq_grid() rounds the extent to four decimals
        and so lands just inside the native span: the ramp is 0.002 at the first grid point,
        not 0.
        """
        grid = common_freq_grid(F_MIN, F_MAX)
        ramp = pd.Series(np.linspace(0.0, 1.0, 366), np.linspace(F_MIN, F_MAX, 366))
        odd  = spectrum_on(183, seed=5)
        out  = resample_spectra(joined({'ramp': ramp, 'odd': odd}), grid)['ramp']
        want = (grid - F_MIN) / (F_MAX - F_MIN)          # the ramp evaluated at the grid
        assert np.allclose(out.values, want, atol=1e-6)

    def test_output_is_on_the_requested_grid(self):
        grid = common_freq_grid(F_MIN, F_MAX)
        out  = resample_spectra(joined({'a': spectrum_on(366)}), grid)
        assert np.array_equal(out.index.values, grid)

    def test_an_all_nan_column_yields_nan_rather_than_raising(self):
        grid = common_freq_grid(F_MIN, F_MAX)
        good = spectrum_on(366, seed=1)
        df   = joined({'good': good})
        df['empty'] = np.nan
        out  = resample_spectra(df, grid)
        assert out['empty'].isna().all()
        assert out['good'].notna().all()

    def test_columns_are_preserved_in_order(self):
        grid = common_freq_grid(F_MIN, F_MAX)
        spectra = {'a': spectrum_on(366, seed=1), 'b': spectrum_on(363, seed=2)}
        out = resample_spectra(joined(spectra), grid)
        assert list(out.columns) == ['a', 'b']
