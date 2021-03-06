

class __Float__(object):

    def __init__(self, val=0, **kwargs):
        if val is None:
            self._val = None
        else:
            self._val = float(val)

    def __add__(self, val):
        if isinstance(val, Float):
            return Float(self._val + val._val)
        return self._val + val

    def __iadd__(self, val):
        self._val += val
        return self

    def __sub__(self, other):
        pass
        # print(other)
        # if isinstance(other, __Float__):
        #     return Float(self._val - other._val)
        # return Float(self._val - other)

    def __isub__(self, other):
        if isinstance(other, Float):
            self._val -= other._val
        else:
            self._val -= other
        return self

    def __mul__(self, other):
        if isinstance(other, Float):
            return Float(self._val * other._val)
        return Float(self._val * other)

    def __neg__(self):
        return Float(-self._val)

    def __truediv__(self, other):
        if isinstance(other, Float):
            return Float(self._val / other._val)
        return Float(self._val / other)

    def __repr__(self):
        return 'Float(%s)' % self._val

    def __str__(self):
        return self.__repr__()

    def __float__(self):
        return self._val


class Float(__Float__):
    pass


# from spira.core.descriptor import DataFieldDescriptor
# class FloatField(DataFieldDescriptor):
#     __type__ = Float

#     def __init__(self, default=0.0, **kwargs):
#         if default is None:
#             kwargs['default'] = None
#         else:
#             kwargs['default'] = self.__type__(val=default)
#         print(kwargs['default'])
#         super().__init__(**kwargs)

#     def get_stored_value(self, obj):
#         value = obj.__store__[self.__name__]
#         return value
#         # return value.__float__()

#     def __set__(self, obj, value):
#         if isinstance(value, self.__type__):
#             obj.__store__[self.__name__] = value
#         elif isinstance(value, (int, float)):
#             obj.__store__[self.__name__] = self.__type__(val=value)
#         elif value is None:
#             return None
#         else:
#             raise TypeError("Invalid type in setting value " +
#                             "of {} (expected {}): {}"
#                             .format(self.__class_, type(value)))








