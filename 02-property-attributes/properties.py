

class Property:
    def __init__(self, /, is_required: bool = False):
        # NEW
        self.is_required = is_required

    def __set_name__(self, owner, name):
        self.name = name

    def __set__(self, instance, __value):
        # NEW
        if self.is_required and __value is None:
            raise ValueError(f"{self.name} is required")
        cache = instance.cached_properties
        cache[self.name] = self._validate(__value)

    def __get__(self, instance, owner):
        cache = instance.cached_properties
        return cache.get(self.name)

    def _validate(self, __value):
        return __value
