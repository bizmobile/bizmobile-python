# -*- coding: utf-8 -*-
import warnings

# external
import slumber
from requests.auth import HTTPBasicAuth

## base
from ..api import BaseAPI
from ..responsor import (
    Response,
    Responses
)
# from ..serialize import Serializer


# 以下を message 以外で使用するなら BaseAPIへ移動


__all__ = ["Message"]


class AuthenticationError(Exception):
    pass


class Message(BaseAPI):
    """ MessageAPI  """

    class Meta:
        secure = True
        api_name = "message"
        api_version = "v1"
        response = Response
        responses = Responses
        authenticate = HTTPBasicAuth
        client = slumber.API

    def __init__(self, *args, **kwargs):
        """

        :param bool secure: https=True or http=False
        :param str api_name:
        :param str api_version:
        :param str base_url:
        :param tuple auth: ("username", "password", ) or False
        """
        super(Message, self).__init__(*args, **kwargs)

        self._meta.secure = kwargs.get("secure", self._meta.secure)
        self._meta.api_name = kwargs.get("api_name", self._meta.api_name)
        self._meta.api_version = kwargs.get("api_version", self._meta.api_version)

        if kwargs.get("auth", None) is None:
            raise AuthenticationError("error: no auth")
        self._auth = kwargs.get("auth", None)
        self._base_url = kwargs.get("base_url", self.get_base_url())
        self._client = self._get_client()
        self._kw = kwargs

    def _get_client(self, base_url=None):
        """

        :param str base_url:
        """
        base_url = base_url or self.get_base_url()
        return self._meta.client(base_url, auth=self._get_authenticate())

    def _get_authenticate(self, auth=None):
        """

        :param tuple auth: ("key", "token")
        :rtype: HTTPDigestAuth, HTTPBasicAuth, HTTPProxyAuth
        :return: Authenticate object
        """
        auth = auth or self._auth
        return auth and self._meta.authenticate(*auth)

    def get_base_url(self):
        """ api url """
        schema = "https" if self._meta.secure else "http"
        return "{0}://{1}/{2}/{3}/".format(
            schema, self.server, self._meta.api_name, self._meta.api_version)

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

        :param str subject: mail subject
        :param str body: mail body
        :param str mailform: admin name
        :param list mailto: device ids
        :rtype: object
        :return: Response Object
        """
        assert isinstance(mailto, (list, tuple))
        data = [
            {"subject": subject, "body": body, "mailfrom": mailfrom, "mailto": to} for to in mailto]
        return self._push_message(data)

    def push_messages(self, messages):
        """
        Read the `Message Interface <https://developer.bizmo.in/display/API/Message+Interface>`_

        .. Note ::
            messages 変換Object

            1. QuerySet
            #. QuerySetValues
            #. QuerySetValuesList

        return値 生データ ::

        .. code-block:: python

            sample = {
                        u'opid': u'877280C4-89D6-49A7-B401-E3F27ED03144',
                        u'utime': u'2012-01-31T10:40:16',
                        u'ctime': u'2012-01-23T17:40:23',
                        u'id': 1
                     }

        :param values: [dict, dict, dict]
        :rtype: object
        :return: Response Object
        """
        data = self._to_values(messages)
        return self._push_message(data)

    def _push_message(self, data):
        push = self._client.operation.push
        return self._meta.response(push, push.post(data), self._meta.api_name)

    def status_message(self, opid, dids=None, **kwargs):
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

        :param str opid: opid is the return value from push_message.
        :param list did: did filtering
        :rtype: object
        :return: PagerResponse Object
        """
        query = dict()

        if dids:
            assert isinstance(dids, (list, tuple, set))
            query.update({"dids": dids})

        page = kwargs.get("page", {"offset": 0, "limit": 20})
        if "page" in kwargs:
            warnings.warn("'page' is a deprecated method & will be removed by next version.")

        status = self._client.operation.status
        query.update({"opid": opid}.items() + page.items())
        return self._meta.responses(status, status.post(query), query)

    def _to_values(self, values):
        """ valuesをlistに変更

        Change types ::

            1. QuerySet
            #. QuerySetValues
            #. QuerySetValuesList
            #. dict

        :param values:
        :rtype: list
        :return: [dict, dict, dict,, ]

        """
        if not isinstance(values, (list, set, tuple, )):
            from django.db.models.query import (
                QuerySet,
                ValuesQuerySet,
                ValuesListQuerySet
            )
            if isinstance(values, (ValuesQuerySet, )):
                values = list(values)
            elif isinstance(values, (QuerySet, ValuesListQuerySet)):
                values = list(values._clone(klass=ValuesQuerySet))
            # elif isinstance(values, (dict, )):
                # values = [values]  #  紛らわしいので削除
            else:
                raise ValueError("Allowed type in values - "
                    "(list, tuple, set, QuerySet, ValuesQuerySet and ValuesListQuerySet)")
        return values

    def _tester(self, **kwargs):
        """ test method """
        page = kwargs.get("page", {"offset": 0, "limit": 20})
        if "page" in kwargs:
            warnings.warn("'page' is a deprecated method & will be removed by next version.")
        message = self._client.message
        return self._meta.responses(message, message.get(**page))
