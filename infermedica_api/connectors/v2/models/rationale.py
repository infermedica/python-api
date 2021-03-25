from .base import BaseModel


class RationaleResult(BaseModel):
    """Model class for handling rationale result object."""

    @staticmethod
    def from_json(json):
        """
        Constructs RationaleResult object from given dict and returns it.

        :param json: Dict with a rationale result value.
        :type json: dict

        :returns: RationaleResult object
        :rtype: :class:`infermedica_api.models.RationaleResult`
        """
        return RationaleResult(**json)
