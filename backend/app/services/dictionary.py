from app.repositories.dictionary import DictionaryRepository

from .base import ResourceService


class DictionaryService(ResourceService):
    repository = DictionaryRepository()
    resource = 'dictionary'
    public_fields = ['id', 'type', 'label', 'value', 'sort', 'status', 'createdAt']
