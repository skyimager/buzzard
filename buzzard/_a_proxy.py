from osgeo import osr

class AProxy(object):

    def __init__(self, ds, back):
        self._ds = _ds
        self._back = _back

    @property
    def wkt_stored(self):
        """The spatial reference that can be found in the metadata of a proxy, in wkt format.

        string or None
        """
        return self._back.wkt_stored

    @property
    def proj4_stored(self):
        """The spatial reference that can be found in the metadata of a proxy, in proj4 format.

        string or None
        """
        return self._back.proj4_stored

    @property
    def wkt_virtual(self):
        """The spatial reference considered to be written in the metadata of a proxy, in wkt
        format.

        string or None
        """
        return self._back.wkt_virtual

    @property
    def proj4_virtual(self):
        """The spatial reference considered to be written in the metadata of a proxy, in proj4
        format.

        string or None
        """
        return self._back.proj4_virtual

    @property
    def close(self):
        """Close a proxy with a call or a context management.

        Examples
        --------
        >>> ds.dem.close()
        >>> with ds.dem.close:
                # code...
        >>> with ds.acreate_raster('result.tif', fp, float, 1).close as result:
                # code...
        >>> with ds.acreate_vector('results.shp', 'linestring').close as roofs:
                # code...
        """
        return _RasterCloseRoutine(self, self._back.close)

    def __del__(self):
        self.close()

class ABackProxy(object):

    def __init__(self, back_ds, wkt_stored, rect):
        wkt_virtual = wkt_stored

        # If `ds` mode overrides file's stored
        if back_ds.wkt_forced:
            wkt_virtual = back_ds.wkt_forced

        # If stored missing and `ds` provides a fallback stored
        if wkt_virtual is None and back_ds.wkt_fallback:
            wkt_virtual = back_ds.wkt_fallback

        # Whether or not `ds` enforces a work projection
        if wkt_virtual:
            sr_virtual = osr.SpatialReference(wkt_virtual)
        else:
            sr_virtual = None

        to_work, to_virtual = back_ds.get_transforms(sr_virtual, rect)

        self.back_ds = back_ds
        self.wkt_stored = wkt_stored
        self.wkt_virtual = wkt_virtual
        self.to_work = to_work
        self.to_virtual = to_virtual

    def close(self):
        self._back_ds.unregister(self)

    @property
    def proj4_virtual(self):
        if self.wkt_virtual is None:
            return None # pragma: no cover
        return osr.SpatialReference(self.wkt_virtual).ExportToProj4()

    @property
    def proj4_stored(self):
        if self.wkt_stored is None:
            return None # pragma: no cover
        return osr.SpatialReference(self.wkt_stored).ExportToProj4()
