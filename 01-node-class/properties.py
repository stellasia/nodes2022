

class Property:
    """XXX Pattern"""
    def __init__(self):
        pass

    def __set_name__(self, owner, name):
        self.name = name

    def __set__(self, instance, __value):
        # movie.title = "Something"
        cache: dict = instance.cached_properties
        cache[self.name] = __value
        # cache[self.name] = self._validate(__value)

    def __get__(self, instance, _):
        # print(movie.title)
        cache: dict = instance.cached_properties
        return cache.get(self.name)

    # def _validate(self, __value):
    #     return __value


# class IntProperty(Property):
#     def _validate(self, __value):
#         try:
#             return int(__value)
#         except ValueError:
#             raise
#
#
# class UUIDProperty(Property):
#     ...
#
#
# class DateProperty(Property):
#     ...
