Python Bizmobile
=================


Client for the [BizMobile API](https://github.com/bizmobile). 


Usage (下記は仮です)
=====================


Get
------
```python
>>> client = Client("http://api.server.com/your/v1/")
>>> client.your.objects.get(name="your")
<your: {u"id": u"1", u"name": u"your", u"status": u"any"}>
```

Count
------
```python
>>> client = Client("http://api.server.com/your/v1/")
>>> client.your.objects.count()
100
```

Filter
------
```python
>>> client = Client("http://api.server.com/your/v1/")
>>> client.your.objects.filter(name="your")
<QuerySet <class 'Response'> (3/3)>
```

Save
----
```python
>>> client = Client("http://api.server.com/your/v1/")
>>> your = client.your(name="name")
>>> your
<your: {u"name": u"name"}>
>>> your.save()  # save Your object.
>>> your
<your: {u"id": u"2", u"name": u"name"}>
```

Delete
------
```python
>>> client = Client("http://api.server.com/your/v1/")
>>> message = client.message(subject="subject delete 1", body="body delete 1")
>>> message.save()
>>> message.id
<message: {u"id": u"1", u"subject": u"subject delete 1", u"body": u"body delete 1"}>
>>> message.delete()  # remove Message object.
>>> try:
>>>     message.id
>>> except AttributeError:
>>>     assert True  # throw AttributeError.
```


Setup
=====

```bash
$ pip install git+git://github.com/bizmobile/bizmobile-python.git
```

Documentation
=============

[BizMobile Developer Center](https://developer.bizmo.in/)

License
==========



