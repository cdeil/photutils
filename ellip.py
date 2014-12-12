import numpy as np
from numpy.testing import assert_allclose
from photutils import EllipticalAperture, aperture_photometry


def test_ellipse_exact_grid():
    """
    Test elliptical exact aperture photometry on a grid of pixel positions.

    This is a regression test for the bug discovered in this issue:
    https://github.com/astropy/photutils/issues/198
    """
    data = np.ones((10, 10))
    x = 3.469906
    y = 3.923861394
    r = 3.

    aperture = EllipticalAperture((x, y), r, r, 0.)
    t = aperture_photometry(data, aperture, method='exact')
    actual = t['aperture_sum'][0] / (np.pi * r ** 2)
    expected = 1
    print('actual: {}'.format(actual))
    #assert_allclose(actual, expected)

test_ellipse_exact_grid()
