# -*- coding: utf-8 -*-
"""
BASE API
"""
import re


attr_ptn = re.compile("__.+__")


class APIMeta(type):
    """
    Metaclass
    """
    def __new__(cls, name, bases, attrs):
        """  """
        super_new = super(APIMeta, cls).__new__
        parents = [b for b in bases if isinstance(b, APIMeta)]
        if not parents:
            return super_new(cls, name, bases, attrs)

        # module = attrs.pop('__module__')
        # new_class = super_new(cls, name, bases, {'__module__': module})
        new_class = super_new(cls, name, bases, attrs)
        attr_meta = attrs.pop('Meta', None)

        meta = getattr(new_class, 'Meta', None) if not attr_meta else attr_meta
        base_meta = getattr(new_class, '_meta', None)

        new_class.inherit(meta, BaseAPI.Meta)
        new_class.inherit(meta, base_meta)
        return new_class

    def inherit(cls, meta, base_meta):
        """ override attribute """
        setattr(cls, "_meta", meta)
        if base_meta:
            old_set = set(cls.__get_attributes(base_meta))
            new_set = set(cls.__get_attributes(meta))
            for attr in old_set - new_set:
                setattr(cls._meta, attr, getattr(base_meta, attr))

    def __get_attributes(cls, meta):
        return [attr for attr in dir(meta) if not attr_ptn.match(attr)]


class BaseAPI(object):
    """ BASE API CLASS """

    __metaclass__ = APIMeta

    class Meta:
        """ base """
        pass

    def __init__(self, server, **kwargs):
        self.server = server

    def __repr__(self):
        return "<API {0}: {1}>".format(
                getattr(self._meta, "api_name", "base"), self.server)
