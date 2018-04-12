# From: https://github.com/eteq/astropysics

from math import pi


def get_SFD_dust(long, lat, dustmap='ebv', interpolate=True):
    """
    Gets map values from Schlegel, Finkbeiner, and Davis 1998 extinction maps.
    `dustmap` can either be a filename (if '%s' appears in the string, it will be
    replaced with 'ngp' or 'sgp'), or one of:
    * 'i100'
        100-micron map in MJy/Sr
    * 'x'
        X-map, temperature-correction factor
    * 't'
        Temperature map in degrees Kelvin for n=2 emissivity
    * 'ebv'
        E(B-V) in magnitudes
    * 'mask'
        Mask values
    For these forms, the files are assumed to lie in the current directory.
    Input coordinates are in degrees of galactic latiude and logitude - they can
    be scalars or arrays.
    if `interpolate` is an integer, it can be used to specify the order of the
    interpolating polynomial
    .. todo::
        Check mask for SMC/LMC/M31, E(B-V)=0.075 mag for the LMC, 0.037 mag for
        the SMC, and 0.062 for M31. Also auto-download dust maps. Also add
        tests. Also allow for other bands.
    """
    from numpy import sin, cos, round, isscalar, array, ndarray, ones_like
    from astropy.io.fits import open

    if type(dustmap) is not str:
        raise ValueError('dustmap is not a string')
    dml = dustmap.lower()
    if dml == 'ebv' or dml == 'eb-v' or dml == 'e(b-v)':
        dustmapfn = 'SFD_dust_4096_%s.fits'
    elif dml == 'i100':
        dustmapfn = 'SFD_i100_4096_%s.fits'
    elif dml == 'x':
        dustmapfn = 'SFD_xmap_%s.fits'
    elif dml == 't':
        dustmapfn = 'SFD_temp_%s.fits'
    elif dml == 'mask':
        dustmapfn = 'SFD_mask_4096_%s.fits'
    else:
        dustmapfn = dustmap

    if isscalar(long):
        l = array([long]) * pi / 180
    else:
        l = array(long) * pi / 180
    if isscalar(lat):
        b = array([lat]) * pi / 180
    else:
        b = array(lat) * pi / 180

    if not len(l) == len(b):
        raise ValueError('input coordinate arrays are of different length')

    if '%s' not in dustmapfn:
        f = open(dustmapfn)
        try:
            mapds = [f[0].data]
        finally:
            f.close()
        assert mapds[-1].shape[0] == mapds[-1].shape[1], 'map dimensions not equal - incorrect map file?'

        polename = dustmapfn.split('.')[0].split('_')[-1].lower()
        if polename == 'ngp':
            n = [1]
            if sum(b > 0) > 0:
                print 'using ngp file when lat < 0 present... put %s wherever "ngp" or "sgp" should go in filename'
        elif polename == 'sgp':
            n = [-1]
            if sum(b < 0) > 0:
                print 'using sgp file when lat > 0 present... put %s wherever "ngp" or "sgp" should go in filename'
        else:
            raise ValueError("couldn't determine South/North from filename - should have 'sgp' or 'ngp in it somewhere")
        masks = [ones_like(b).astype(bool)]
    else:  # need to do things seperately for north and south files
        nmask = b >= 0
        smask = ~nmask

        masks = [nmask, smask]
        ns = [1, -1]

        mapds = []
        f = open(dustmapfn % 'ngp')
        try:
            mapds.append(f[0].data)
        finally:
            f.close()
        assert mapds[-1].shape[0] == mapds[-1].shape[1], 'map dimensions not equal - incorrect map file?'
        f = open(dustmapfn % 'sgp')
        try:
            mapds.append(f[0].data)
        finally:
            f.close()
        assert mapds[-1].shape[0] == mapds[-1].shape[1], 'map dimensions not equal - incorrect map file?'

    retvals = []
    for n, mapd, m in zip(ns, mapds, masks):
        # project from galactic longitude/latitude to lambert pixels (see SFD98)
        npix = mapd.shape[0]

        x = npix / 2 * cos(l[m]) * (1 - n * sin(b[m])) ** 0.5 + npix / 2 - 0.5
        y = -npix / 2 * n * sin(l[m]) * (1 - n * sin(b[m])) ** 0.5 + npix / 2 - 0.5
        # now remap indecies - numpy arrays have y and x convention switched from SFD98 appendix
        x, y = y, x

        if interpolate:
            from scipy.ndimage import map_coordinates
            if type(interpolate) is int:
                retvals.append(map_coordinates(mapd, [x, y], order=interpolate))
            else:
                retvals.append(map_coordinates(mapd, [x, y]))
        else:
            x = round(x).astype(int)
            y = round(y).astype(int)
            retvals.append(mapd[x, y])

    if isscalar(long) or isscalar(lat):
        for r in retvals:
            if len(r) > 0:
                return r[0]
        assert False, 'None of the return value arrays were populated - incorrect inputs?'
    else:
        # now recombine the possibly two arrays from above into one that looks like  the original
        retval = ndarray(l.shape)
        for m, val in zip(masks, retvals):
            retval[m] = val
        return retval
