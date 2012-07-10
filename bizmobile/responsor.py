# -*- coding: utf-8 -*-
"""
Responsor

:ctime: 2012-06-27T01:16:14
"""
import copy


def parse_id(resouce_uri):
    """ url parsing

    :param resource_uri:
    :rtype: str
    :return: primary id
    """
    return resouce_uri.split("/")[::-1][1]


class Response(object):

    def __init__(self, client, response, name=""):
        self._client = client
        self._response = response
        self._name = name

    def __repr__(self):
        return "<Response {0}: {1}>".format(self._name, self._response)

    def __getattr__(self, attr):
        if attr in self._response:
            return self._response[attr]
        else:
            raise AttributeError(attr)

    def __getitem__(self, item):
        if item in self._response:
            return self._response[item]
        else:
            raise KeyError(item)

    def __contains__(self, attr):
        return attr in self._response

    def save(self):
        pass


class Responses(object):

    def __init__(self, client, responses={}, query={}, **kwargs):
        self._client = client
        self._query = query
        self._response_class = kwargs.get("response_class", Response)
        self._set_objects(responses)  # set _responses, _meta, _objects
        self._iteration_num = None

    def __repr__(self):
        return "<Responses {0} ({1}/{2})>".format(
                    self._response_class, self._objects_count, len(self))

    def __len__(self):
        """ total count """
        return self.count()

    def __iter__(self):
        if len(self) < 1:
            raise StopIteration()
        index = 0
        length = 0
        klass = copy.deepcopy(self)
        while 1:
            try:
                yield klass._wrap_response(klass._objects[index])
                index += 1
                length += 1
            except KeyError:
                if self._iteration_num <= length and self._iteration_num is not None:
                    raise StopIteration()
                klass = klass._next()
                index = 0

    def __getitem__(self, index):
        try:
            if isinstance(index, slice):
                start = index.start or 0
                stop = index.stop
                # step = index.step

                limit = stop - start
                self._iteration_num = limit
                query = {"limit": limit, "offset": start}
                responses = self._get_responses(**query)

                clone = self._clone(
                    responses, _iteration_num=self._iteration_num)
                try:
                    #  XXX: resource uri がない場合
                    clone._query.update({"id__in": clone._get_ids()})
                except IndexError:
                    pass
                return clone

            if not self._responses:
                self._fill_objects()
            return self._wrap_response(self._objects[index])
        except KeyError as err:
            raise IndexError(err)

    def _clone(self, responses={}, klass=None, **kwargs):
        responses = responses or self._responses
        klass = klass or self.__class__

        clone = klass(client=self._client, responses=responses, query=self._query)
        clone.__dict__.update(kwargs)
        return clone

    def _get_responses(self, **kwargs):
        """ base client response """
        return self._client.get(**kwargs)

    def _get_ids(self):
        """ parse primary id """
        return [parse_id(self._objects[i]["resource_uri"]) for i in self._objects]

    def _wrap_response(self, dic):
        return self._response_class(self._client, dic)

    def _request(self, path):
        """ base request """
        return self._client("{0}&".format(path)).get()

    def _next(self):
        """ request next page """
        if not self._meta["next"]:
            raise StopIteration()
        return self._clone(self._request(self._meta["next"]))

    def _previous(self):
        """ request previous page """
        if not self._meta["previous"]:
            raise StopIteration()
        return self._clone(self._request(self._meta["previous"]))

    def _fill_objects(self):
        """ set cache object """
        self._set_objects(self._get_responses())

    def _set_objects(self, responses={}):
        """ set cache object """
        self._responses = responses
        self._meta = responses and responses["meta"]
        self._objects = dict(enumerate(responses["objects"])) if responses else []
        self._objects_count = len(self._objects)

    def count(self):
        if self._responses:
            return self._meta["total_count"]
        self._fill_objects()
        return self._meta["total_count"]
