# -*- coding: utf-8 -*-
"""
Responsor

:ctime: 2012-06-27T01:16:14
"""
import copy
import urlparse
import urllib


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
        self._name = name
        if isinstance(response, (str, unicode)):
            self._response = self._client.get_serializer().loads(response)
        else:
            self._response = response

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

    def __init__(self, client, responses=None, query=None, **kwargs):
        self._client = client
        self._kwargs = kwargs
        self._query = query or dict()
        self._serializer = False
        self._iteration_num = None
        self._responses = None
        self._meta = None
        self._objects = []
        self._response_class = kwargs.get("response_class", Response)
        self._set_objects(responses)  # set _responses, _meta, _objects

    def __repr__(self):
        return "<Responses {0} ({1}/{2})>".format(
                    self._response_class, len(self._objects), len(self))

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
                # step = index.step
                start = index.start or 0
                stop = index.stop
                limit = stop - start

                self._iteration_num = limit
                query = {"limit": limit, "offset": start}
                parse = urlparse.urlparse(self._client._store["base_url"])

                responses = self._request("{0}/?{1}".format(parse.path, urllib.urlencode(query)))
                clone = self._clone(
                    responses, _iteration_num=self._iteration_num, _serializer=self._serializer)
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

    def _clone(self, responses=None, klass=None, **kwargs):
        responses = responses or self._responses
        klass = klass or self.__class__

        clone = klass(client=self._client, responses=responses, query=self._query)
        clone.__dict__.update(kwargs)
        return clone

    def _get_responses(self, **kwargs):
        """ base client response """
        if self._serializer:
            return self._client.post(kwargs)
        else:
            return self._client.get(**kwargs)

    def _get_ids(self):
        """ parse primary id """
        return [parse_id(self._objects[i]["resource_uri"]) for i in self._objects]

    def _wrap_response(self, dic):
        return self._response_class(self._client, dic)

    def _request(self, path):
        """ base request
        """
        base_url = "{0}&".format(path)

        if self._serializer:
            data = self._query
            parse = urlparse.urlparse(path)
            data.update(urlparse.parse_qsl(parse.query))
            return self._client(base_url).post(data)
        else:
            return self._client(base_url).get()

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

    def _set_objects(self, responses):
        """ set cache object """
        if isinstance(responses, (str, unicode)):
            self._serializer = True
            responses = self._client.get_serializer().loads(responses)
        self._responses = responses
        self._meta = responses and responses["meta"]
        self._objects = dict(enumerate(responses["objects"])) if responses else []

    def count(self):
        if self._responses:
            return self._meta["total_count"]
        self._fill_objects()
        return self._meta["total_count"]
