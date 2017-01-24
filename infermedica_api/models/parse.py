from .base import BaseModel


class ParseMention(BaseModel):
    """Model class for API parse mention object."""

    @staticmethod
    def from_json(json):
        """
        Constructs ParseMention object from given dict and returns it.

        :param json: Dict with mention values
        :type json: dict

        :returns: ParseMention details object
        :rtype: :class:`infermedica_api.models.ParseMention`
        """
        return ParseMention(**json)


class ParseResults(BaseModel):
    """Model class for API parse response object."""

    def __init__(self, **kwargs):
        super(ParseResults, self).__init__(**kwargs)

        self.mentions = [ParseMention.from_json(val) for val in self.mentions]

    @staticmethod
    def from_json(json):
        """
        Constructs ParseResults object from given dict and returns it.

        :param json: Dict with parse result value.
        :type json: dict

        :returns: Parse result object
        :rtype: :class:`infermedica_api.models.ParseResults`
        """
        return ParseResults(**json)

    def to_dict(self):
        """
        Transform object to dict.

        :return: ParseResults object as dict.
        :rtype: dict
        """
        return {
            "mentions": [mention.to_dict() for mention in self.mentions]
        }
