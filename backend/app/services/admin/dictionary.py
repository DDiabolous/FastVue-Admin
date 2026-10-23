from app.repositories.admin.dictionary import DictionaryRepository

from app.services.admin.base import ResourceService


class DictionaryService(ResourceService):
    repository = DictionaryRepository()
    resource = 'dictionary'
    public_fields = ['id', 'type', 'label', 'value', 'sort', 'status', 'createdAt']
