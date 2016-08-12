# -*- coding: utf-8 -*-

"""
infermedica_api.models.base
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains common models for data returned from api.
"""
import json


class ModelCommon(object):
    """Abstract class with implementation of commonly used functions."""

    class Meta:
        abstract = True

    def __str__(self):
        """Returns nicely formatted object."""
        return self.to_json(pretty_print=True)

    def to_json(self, pretty_print=False):
        """
        Returns json dumps of the class object.
        If pretty_print argument set to True,
        returned string is nicely formatted.

        :param pretty_print: Boolean which determinants
        if output should be humanly readable formatted
        :type pretty_print: bool

        :returns: String with json data of the object
        :rtype: str
        """
        if pretty_print:
            return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
        return json.dumps(self, default=lambda o: o.__dict__)

    def to_dict(self):
        """
        Transform class object to dict.

        :return: Class object as dict.
        :rtype: dict
        """
        return dict({key: val.to_dict() if hasattr(val, 'to_dict') else val for key, val in self.__dict__.items()})


class BaseModel(ModelCommon):
    """
    Abstract class of model with init function,
    which generically assign object parameters.
    """

    class Meta:
        abstract = True

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class BaseModelList(list, ModelCommon):
    """
    Abstract class of list model with init function, which assign key mapping.
    """

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        if 'mapping' in kwargs:
            self.mapping = kwargs.pop('mapping')
        else:
            self.mapping = {}

        super(BaseModelList, self).__init__(*args, **kwargs)

    def _get_details(self, _id):
        """
        Generic function to handle object returns by the object id.

        :param _id: Object id
        :type _id: str

        :returns: Model object with given id
        """
        try:
            return self[self.mapping[_id]]
        except (IndexError, KeyError) as e:
            return None

    def to_list(self):
        """
        Transform class object to simple list.

        :return: Class object as simple list.
        :rtype: list
        """
        return [val.to_dict() if hasattr(val, 'to_dict') else val for val in self]

    def to_dict(self):
        """
        Transform class object to list.
        It does not return dict as the name suggest, but it's created for consistency reasons.

        :return: Class object as list.
        :rtype: list
        """
        return self.to_list()
