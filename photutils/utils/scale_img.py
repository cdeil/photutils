# Licensed under a 3-clause BSD style license - see LICENSE.rst
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
from astropy.stats import sigma_clip


def find_imgcuts(image, min_cut=None, max_cut=None, min_percent=None,
                 max_percent=None, percent=None):
    """
    Find minimum and maximum image cut levels from percentiles of the
    image values.

    Parameters
    ----------
    image : array_like
        The 2D array of the image.

    min_cut : float, optional
        The minimum cut level.  Data values less than ``min_cut`` will
        set to ``min_cut`` before scaling the image.

    max_cut : float, optional
        The maximum cut level.  Data values greater than ``max_cut``
        will set to ``max_cut`` before scaling the image.

    min_percent : float, optional
        The minimum cut level as a percentile of the values in the
        image.  If ``min_cut`` is input, then ``min_percent`` will be
        ignored.

    max_percent : float, optional
        The maximum cut level as a percentile of the values in the
        image.  If ``max_cut`` is input, then ``max_percent`` will be
        ignored.

    percent : float, optional
        The percentage of the image values to scale.  The lower cut
        level will set at the ``(100 - percent) / 2`` percentile, while
        the upper cut level will be set at the ``(100 + percent) / 2``
        percentile.  This value overrides the values of ``min_percent``
        and ``max_percent``, but is ignored if ``min_cut`` and
        ``max_cut`` are both input.

    Returns
    -------
    out : tuple
        Returns a tuple containing (``min_cut``, ``max_cut``) image cut
        levels.
    """

    if min_cut is not None and max_cut is not None:
        return min_cut, max_cut
    if percent:
        assert (percent >= 0) and (percent <= 100.0), 'percent must be >= 0 and <= 100.0'
        if not min_percent and not max_percent:
            min_percent = (100.0 - float(percent)) / 2.0
            max_percent = 100.0 - min_percent
    if min_cut is None:
        if min_percent is None:
            min_percent = 0.0
        assert min_percent >= 0, 'min_percent must be >= 0'
        min_cut = np.percentile(image, min_percent)
    if max_cut is None:
        if max_percent is None:
            max_percent = 100.0
        assert max_percent <= 100.0, 'max_percent must be <= 100.0'
        max_cut = np.percentile(image, max_percent)
    assert min_cut <= max_cut, 'min_cut must be <= max_cut'
    return min_cut, max_cut


def img_stats(image, image_mask=None, mask_val=None, sig=3.0, iters=None):
    """
    Perform sigma-clipped statistics on an image.

    Parameters
    ----------
    image : array_like
        The 2D array of the image.

    image_mask : array_like, bool, optional
        A boolean mask with the same shape as ``image``, where a `True`
        value indicates the corresponding element of ``image`` is
        invalid.  Masked pixels are ignored when computing the image
        statistics.

    mask_val : float, optional
        An image data value (e.g., ``0.0``) that is ignored when
        computing the image statistics.  ``mask_val`` will be ignored if
        ``image_mask`` is input.

    sig : float, optional
        The number of standard deviations to use as the clipping limit.

    iters : float, optional
       The number of iterations to perform clipping, or `None` to clip
       until convergence is achieved (i.e. continue until the last
       iteration clips nothing).

    Returns
    -------
    stats : tuple
        Returns a tuple of the (``mean``, ``median``, ``stddev``) of the
        sigma-clipped image.
    """

    if image_mask:
        image = image[~image_mask]
    if mask_val and not image_mask:
        idx = (image != mask_val).nonzero()
        image = image[idx]
    image_clip = sigma_clip(image, sig=sig, iters=iters)
    goodvals = image_clip.data[~image_clip.mask]
    return np.mean(goodvals), np.median(goodvals), np.std(goodvals)


def rescale_img(image, min_cut=None, max_cut=None, min_percent=None,
                max_percent=None, percent=None):
    """
    Rescale image values between minimum and maximum cut levels to
    values between 0 and 1, inclusive.

    Parameters
    ----------
    image : array_like
        The 2D array of the image.

    min_cut : float, optional
        The minimum cut level.  Data values less than ``min_cut`` will
        set to ``min_cut`` before scaling the image.

    max_cut : float, optional
        The maximum cut level.  Data values greater than ``max_cut``
        will set to ``max_cut`` before scaling the image.

    min_percent : float, optional
        The minimum cut level as a percentile of the values in the
        image.  If ``min_cut`` is input, then ``min_percent`` will be
        ignored.

    max_percent : float, optional
        The maximum cut level as a percentile of the values in the
        image.  If ``max_cut`` is input, then ``max_percent`` will be
        ignored.

    percent : float, optional
        The percentage of the image values to scale.  The lower cut
        level will set at the ``(100 - percent) / 2`` percentile, while
        the upper cut level will be set at the ``(100 + percent) / 2``
        percentile.  This value overrides the values of ``min_percent``
        and ``max_percent``, but is ignored if ``min_cut`` and
        ``max_cut`` are both input.

    Returns
    -------
    out : tuple
        Returns a tuple containing (``outimg``, ``min_cut``,
        ``max_cut``), which are the output scaled image and the minimum
        and maximum cut levels.
    """

    try:
        from skimage import exposure
    except (ImportError):
        raise ImportError('The image scaling functions require scikit-image.')
    image = image.astype(np.float64)
    min_cut, max_cut = find_imgcuts(image, min_cut=min_cut, max_cut=max_cut,
                                    min_percent=min_percent,
                                    max_percent=max_percent, percent=percent)
    outimg = exposure.rescale_intensity(image, in_range=(min_cut, max_cut),
                                        out_range=(0, 1))
    return outimg, min_cut, max_cut


def scale_linear(image, min_cut=None, max_cut=None, min_percent=None,
                 max_percent=None, percent=None):
    """
    Perform linear scaling of an image between minimum and maximum cut
    levels.

    Parameters
    ----------
    image : array_like
        The 2D array of the image.

    min_cut : float, optional
        The minimum cut level.  Data values less than ``min_cut`` will
        set to ``min_cut`` before scaling the image.

    max_cut : float, optional
        The maximum cut level.  Data values greater than ``max_cut``
        will set to ``max_cut`` before scaling the image.

    min_percent : float, optional
        The minimum cut level as a percentile of the values in the
        image.  If ``min_cut`` is input, then ``min_percent`` will be
        ignored.

    max_percent : float, optional
        The maximum cut level as a percentile of the values in the
        image.  If ``max_cut`` is input, then ``max_percent`` will be
        ignored.

    percent : float, optional
        The percentage of the image values to scale.  The lower cut
        level will set at the ``(100 - percent) / 2`` percentile, while
        the upper cut level will be set at the ``(100 + percent) / 2``
        percentile.  This value overrides the values of ``min_percent``
        and ``max_percent``, but is ignored if ``min_cut`` and
        ``max_cut`` are both input.

    Returns
    -------
    scaled_image : array_like
        The 2D array of the scaled/stretched image.
    """

    result = rescale_img(image, min_cut=min_cut, max_cut=max_cut,
                         min_percent=min_percent, max_percent=max_percent,
                         percent=percent)
    return result[0]


def scale_sqrt(image, min_cut=None, max_cut=None, min_percent=None,
               max_percent=None, percent=None):
    """
    Perform square-root scaling of an image between minimum and maximum
    cut levels.  This is equivalent to using `scale_power` with a
    ``power`` of ``0.5``.

    Parameters
    ----------
    image : array_like
        The 2D array of the image.

    min_cut : float, optional
        The minimum cut level.  Data values less than ``min_cut`` will
        set to ``min_cut`` before scaling the image.

    max_cut : float, optional
        The maximum cut level.  Data values greater than ``max_cut``
        will set to ``max_cut`` before scaling the image.

    min_percent : float, optional
        The minimum cut level as a percentile of the values in the
        image.  If ``min_cut`` is input, then ``min_percent`` will be
        ignored.

    max_percent : float, optional
        The maximum cut level as a percentile of the values in the
        image.  If ``max_cut`` is input, then ``max_percent`` will be
        ignored.

    percent : float, optional
        The percentage of the image values to scale.  The lower cut
        level will set at the ``(100 - percent) / 2`` percentile, while
        the upper cut level will be set at the ``(100 + percent) / 2``
        percentile.  This value overrides the values of ``min_percent``
        and ``max_percent``.

    Returns
    -------
    scaled_image : array_like
        The 2D array of the scaled/stretched image.
    """

    result = rescale_img(image, min_cut=min_cut, max_cut=max_cut,
                         min_percent=min_percent, max_percent=max_percent,
                         percent=percent)
    return np.sqrt(result[0])


def scale_power(image, power, min_cut=None, max_cut=None, min_percent=None,
                max_percent=None, percent=None):
    """
    Perform power scaling of an image between minimum and maximum cut
    levels.

    Parameters
    ----------
    image : array_like
        The 2D array of the image.

    power : float
        The power index for the image scaling.

    min_cut : float, optional
        The minimum cut level.  Data values less than ``min_cut`` will
        set to ``min_cut`` before scaling the image.

    max_cut : float, optional
        The maximum cut level.  Data values greater than ``max_cut``
        will set to ``max_cut`` before scaling the image.

    min_percent : float, optional
        The minimum cut level as a percentile of the values in the
        image.  If ``min_cut`` is input, then ``min_percent`` will be
        ignored.

    max_percent : float, optional
        The maximum cut level as a percentile of the values in the
        image.  If ``max_cut`` is input, then ``max_percent`` will be
        ignored.

    percent : float, optional
        The percentage of the image values to scale.  The lower cut
        level will set at the ``(100 - percent) / 2`` percentile, while
        the upper cut level will be set at the ``(100 + percent) / 2``
        percentile.  This value overrides the values of ``min_percent``
        and ``max_percent``, but is ignored if ``min_cut`` and
        ``max_cut`` are both input.

    Returns
    -------
    scaled_image : array_like
        The 2D array of the scaled/stretched image.
    """

    result = rescale_img(image, min_cut=min_cut, max_cut=max_cut,
                         min_percent=min_percent, max_percent=max_percent,
                         percent=percent)
    return (result[0])**power


def scale_log(image, min_cut=None, max_cut=None, min_percent=None,
              max_percent=None, percent=None):
    """
    Perform logarithmic (base 10) scaling of an image between minimum and
    maximum cut levels.

    Parameters
    ----------
    image : array_like
        The 2D array of the image.

    min_cut : float, optional
        The minimum cut level.  Data values less than ``min_cut`` will
        set to ``min_cut`` before scaling the image.

    max_cut : float, optional
        The maximum cut level.  Data values greater than ``max_cut``
        will set to ``max_cut`` before scaling the image.

    min_percent : float, optional
        The minimum cut level as a percentile of the values in the
        image.  If ``min_cut`` is input, then ``min_percent`` will be
        ignored.

    max_percent : float, optional
        The maximum cut level as a percentile of the values in the
        image.  If ``max_cut`` is input, then ``max_percent`` will be
        ignored.

    percent : float, optional
        The percentage of the image values to scale.  The lower cut
        level will set at the ``(100 - percent) / 2`` percentile, while
        the upper cut level will be set at the ``(100 + percent) / 2``
        percentile.  This value overrides the values of ``min_percent``
        and ``max_percent``, but is ignored if ``min_cut`` and
        ``max_cut`` are both input.

    Returns
    -------
    scaled_image : array_like
        The 2D array of the scaled/stretched image.
    """

    result = rescale_img(image, min_cut=min_cut, max_cut=max_cut,
                         min_percent=min_percent, max_percent=max_percent,
                         percent=percent)
    outimg = np.log10(result[0] + 1.0) / np.log10(2.0)
    return outimg


def scale_asinh(image, noise_level=None, sigma=2.0, min_cut=None,
                max_cut=None, min_percent=None, max_percent=None,
                percent=None):
    """
    Perform inverse hyperbolic sine (arcsinh) scaling of an image
    between minimum and maximum cut levels.

    Parameters
    ----------
    image : array_like
        The 2D array of the image.

    noise_level: float, optional
        The noise level of the image.  Levels less than noise_level will
        approximately be linearly scaled, while levels greater than
        noise_level will approximately be logarithmically scaled.

    sigma: float, optional
        The number of standard deviations of the background noise used
        to estimate the absolute noise level.  This value is ignored if
        ``noise_level`` is input.

    min_cut : float, optional
        The minimum cut level.  Data values less than ``min_cut`` will
        set to ``min_cut`` before scaling the image.

    max_cut : float, optional
        The maximum cut level.  Data values greater than ``max_cut``
        will set to ``max_cut`` before scaling the image.

    min_percent : float, optional
        The minimum cut level as a percentile of the values in the
        image.  If ``min_cut`` is input, then ``min_percent`` will be
        ignored.

    max_percent : float, optional
        The maximum cut level as a percentile of the values in the
        image.  If ``max_cut`` is input, then ``max_percent`` will be
        ignored.

    percent : float, optional
        The percentage of the image values to scale.  The lower cut
        level will set at the ``(100 - percent) / 2`` percentile, while
        the upper cut level will be set at the ``(100 + percent) / 2``
        percentile.  This value overrides the values of ``min_percent``
        and ``max_percent``, but is ignored if ``min_cut`` and
        ``max_cut`` are both input.

    Returns
    -------
    scaled_image : array_like
        The 2D array of the scaled/stretched image.
    """

    result = rescale_img(image, min_cut=min_cut, max_cut=max_cut,
                         min_percent=min_percent, max_percent=max_percent,
                         percent=percent)
    outimg, min_cut, max_cut = result
    if not noise_level:
        mean, median, stddev = img_stats(outimg)
        noise_level = mean + (sigma * stddev)
    z = (noise_level - min_cut) / (max_cut - min_cut)
    outimg = np.arcsinh(outimg / z) / np.arcsinh(1.0 / z)
    return outimg
