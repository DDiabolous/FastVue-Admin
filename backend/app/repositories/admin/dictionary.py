from app.models.admin.dictionary import Dictionary

from app.repositories.base import Repository


class DictionaryRepository(Repository):
    model = Dictionary
    search_fields = ('type', 'label', 'value')

    def ordering(self):
        return [Dictionary.sort, Dictionary.createdAt.desc(), Dictionary.id]
