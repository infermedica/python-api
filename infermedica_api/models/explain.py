from .base import BaseModel


class ExplainResults(BaseModel):
    """Model class for API explain object."""

    def __init__(self, **kwargs):
        super(ExplainResults, self).__init__(**kwargs)

        self.supporting_evidence = [ExplainResult.from_json(val) for val in self.supporting_evidence]
        self.conflicting_evidence = [ExplainResult.from_json(val) for val in self.conflicting_evidence]

    @staticmethod
    def from_json(json):
        """
        Constructs ExplainResults object from given dict and returns it.

        :param json: Dict with explain results value.
        :type json: dict

        :returns: Explain result details object
        :rtype: :class:`infermedica_api.models.ExplainResults`
        """
        return ExplainResults(**json)

    def to_dict(self):
        """
        Transform object to dict.

        :return: ExplainResults object as dict.
        :rtype: dict
        """
        return {
            "supporting_evidence": [result.to_dict() for result in self.supporting_evidence],
            "conflicting_evidence": [result.to_dict() for result in self.conflicting_evidence]
        }


class ExplainResult(BaseModel):
    """Model class for handling single explain result object."""

    @staticmethod
    def from_json(json):
        """
        Constructs ExplainResult object from given dict and returns it.

        :param json: Dict with single explain result value.
        :type json: dict

        :returns: Explain result details object
        :rtype: :class:`infermedica_api.models.ExplainResult`
        """
        return ExplainResult(**json)
