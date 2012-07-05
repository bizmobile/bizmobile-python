# -*- coding: utf-8 -*-
"""
Responsor

:ctime: 2012-06-27T01:16:14
"""


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


class PagerResponse(object):

    def __init__(self, client, responses, **kwargs):
        self._client = client
        self._responses = responses
        self._objects = dict(enumerate(responses["objects"]))
        self._meta = responses["meta"]
        self._response_class = kwargs.get("response_class", Response)

    def __repr__(self):
        return "<PagerResponse {0} ({1}/{2})>".format(
                    self._response_class, len(self._objects), self.__len__())

    def __len__(self):
        return self._meta["total_count"]

    def __iter__(self):
        """ イテレータを拡張して続けてnextを呼ぶようにするのも面白いかも """
        return self._iter()

    def _iter(self):
        for i in self._objects:
            yield self._wrap_dict(self._objects[i])

    def _wrap_dict(self, dic):
        return self._response_class(self._client, dic)

    def next(self):
        """ request next page """
        res = self._client.get(self._client.get_url(self._meta["next"]))
        return PagerResponse(self._client, res)

    def previous(self):
        """ request previous page """
        res = self._client.get(self._client.get_url(self._meta["previous"]))
        return PagerResponse(self._client, res)
