from app.models.dictionary import Dictionary

from .base import Repository


class DictionaryRepository(Repository):
    model = Dictionary
    search_fields = ('type', 'label', 'value')

    def ordering(self):
        return [Dictionary.sort, Dictionary.createdAt.desc(), Dictionary.id]
