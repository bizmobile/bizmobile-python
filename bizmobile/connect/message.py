# -*- coding: utf-8 -*-
# external
# import urlparse
import slumber

## base
from ..api import BaseAPI
# from ..serialize import Serializer
from ..responsor import (
    Response,
    PagerResponse
)


# 以下を message 以外で使用するなら BaseAPIへ移動


__all__ = ["Message"]


class Message(BaseAPI):

    class Meta:
        api_name = "message"
        api_version = "v1"
        secure = False
        response = Response
        responses = PagerResponse
        client = slumber.API

    def __init__(self, *args, **kwargs):
        """ MessageAPI  """
        super(Message, self).__init__(*args, **kwargs)
        self._client = self._meta.client(self.get_base_url(), auth=kwargs.pop("auth", None))

    def get_base_url(self):
        schema = "https" if self._meta.secure else "http"
        return "{0}://{1}/{2}/{3}/".format(schema, self.server,
                                           self._meta.api_name, self._meta.api_version)

    def push_message(self, subject, body, mailfrom, mailto):
        """
        Read the `Message Interface <https://developer.bizmo.in/display/API/Message+Interface>`_

        return値 生データ ::

        .. code-block:: python

            sample = {
                        u'opid': u'877280C4-89D6-49A7-B401-E3F27ED03144',
                        u'utime': u'2012-01-31T10:40:16',
                        u'ctime': u'2012-01-23T17:40:23',
                        u'id': 1
                     }

        :param subject: mail subject
        :param body: mail body
        :param mailform: admin name
        :param mailto: device ids
        :rtype: object
        :return: Response Object
        """
        assert isinstance(mailto, (list, tuple))
        data = [
            {"subject": subject, "body": body, "mailfrom": mailfrom, "mailto": to} for to in mailto]
        push = self._client.operation.push
        serializer = push.get_serializer()
        # sample = {
            # u'opid': u'877280C4-89D6-49A7-B401-E3F27ED03144',
            # u'utime': u'2012-01-31T10:40:16',
            # u'ctime': u'2012-01-23T17:40:23',
            # u'id': 1
        # }
        # # return self._meta.response(push, sample, self._meta.api_name)
        return self._meta.response(push, serializer.loads(push.post(data)), self._meta.api_name)

    def status_message(self, opid, page={"offset": 0, "limit": 20}):
        """

        Read the `Message Interface <https://developer.bizmo.in/display/API/Message+Interface>`_


        return値 生データ ::

        .. code-block:: python

            sample = {u'meta': {u'limit': 20,
              u'next': u'/message/v1/message/?limit=20&offset=20',
              u'offset': 0,
              u'previous': None,
              u'total_count': 3},
             u'objects': [{
                u'id': u"1",
                u"did": u"d-12345670",
                u"read": True,
                u"read_date": u'2012-01-30T15:29:41',
                u'status': u'success',
                u"reason": "",
                u'ctime': u'2012-01-24T13:41:16',
                u'utime': u'2012-01-30T15:29:44'
              }, {
                u'id': u"2",
                u"did": u"d-12345671",
                u"read": True,
                u"read_date": u'2012-01-30T15:29:43',
                u'status': u'success',
                u"reason": "",
                u'ctime': u'2012-01-24T13:41:16',
                u'utime': u'2012-01-30T15:29:44'
              }]
            }

        :param opid: opid is the return value from push_message.
        :rtype: object
        :return: PagerResponse Object
        """
        status = self._client.operation.status
        # return self._meta.responses(status,
            # {u'meta': {
                # u'limit': 20,
                # u'next': None,
                # u'offset': 0,
                # u'previous': None,
                # u'total_count': 10
            # },
            # u'objects': [
                # {u'id': u"{0}".format(num),
                 # u"did": u"d-1234567{0}".format(num),
                 # u"read": True,
                 # u"read_date": u'2012-01-30T15:29:4{0}'.format(num),
                 # u'status': u'success',
                 # u"reason": "",
                 # u'ctime': u'2012-01-24T13:41:16',
                 # u'utime': u'2012-01-30T15:29:44'
            # } for num in range(0, 10)]})
        return self._meta.responses(status, status.get(**page))
