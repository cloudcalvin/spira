import gdspy
import inspect
import collections
import numpy as np
from copy import copy, deepcopy

from spira.core.descriptor import BaseField
from spira.core.descriptor import DataField


class MetaBase(type):
    """
    Base Metaclass to register and bind class to property
    functions. All elements connect to this metaclass.
    """

    @classmethod
    def __prepare__(cls, name, bases, **kwds):
        return collections.OrderedDict()

    def __new__(cls, name, bases, attrs):
        mixins = []

        link_mixins = attrs.get('__mixins__')
        if link_mixins:
            mixins.extend(link_mixins)

        bases = list(bases)
        bases.extend(mixins)
        bases = tuple(bases)

        cls = super().__new__(cls, name, bases, dict(attrs))

        if not hasattr(cls, 'registry'):
            cls.registry = {}
        cls.registry[name] = cls

        return cls

    def __init__(cls, name, bases, attrs):

        super().__init__(name, bases, attrs)

        cls.__props__ = []
        cls.__params__ = {}

        locked_fields = []
        unlocked_fields = []

        for k, v in cls.__get_fields__():
            if not k in cls.__props__:

                if hasattr(v, 'bind_property'):
                    v.bind_property(cls, k)
                v.validate_binding(cls, k)

                if v.locked:
                    locked_fields.append(k)
                else:
                    unlocked_fields.append(k)

                cls.__params__[k] = v
                cls.__props__.append(k)

        cls.__locked_fields__ = locked_fields
        cls.__unlocked_fields__ = unlocked_fields
        cls.__generate_docs__()


class MetaInitializer(MetaBase):
    """
    Metaclass that initiates spira classes for
    meta-configuring classes and parameters.
    """

    MODULES = ['gdspy', 'meshio', 'pygmsh']
    SECTIONS = ['Desc', 'Parameters', 'Examples', 'Notes', 'Returns']

    def __map_parameters__(cls, *params, **keyword_params):
        f = inspect.getfullargspec(cls.__init__)
        p, d = f.args, f.defaults
        if d is None: d = []
        kwargs = {}
        for k, v in zip(p[-len(d):], d):
            kwargs[k] = v
        kwargs.update(keyword_params)
        for k, v in zip(p[1:len(params)+1], params):
            kwargs[k] = v
        return kwargs

    def __generate_docs__(cls):

        output = []
        output.extend(cls.__get_class_docs__())
        output.extend(cls.__get_function_docs__())

        cls.__doc__ = '\n'.join(output)

    def __get_class_docs__(cls):

        output = list()

        class_docs = {}
        if cls.__doc__:
            lines = inspect.getdoc(cls).split('\n')

            lines = list(filter(lambda x: len(x.strip()) > 0, lines))

            section = 'Desc'
            class_docs[section] = []

            for i in range(len(lines)):
                if '---' in lines[i]:
                    del class_docs[section][-1]
                    section = lines[i-1].strip()
                    class_docs[section] = []
                line = lines[i].strip()
                class_docs[section].append(line)

        class_docs['Parameters'] = []

        docparam = ''
        for key in cls.SECTIONS:
            if key in class_docs.keys():
                value = class_docs[key]
                if key == 'Desc':
                    docparam += '\n'.join(value)
                elif key == 'Parameters':
                    params = cls.__fields__()
                    if len(params) > 0:
                        docparam += '\nParameters\n'
                        docparam += '---------\n'
                        for p in params:
                            docparam += p + ' : ' + str(type(p)) + '\n'
                            param_attr = getattr(cls, p)
                            if hasattr(param_attr, '__doc__'):
                                docparam += '\t' + param_attr.__doc__ + '\n'
                else:
                    docparam += '{}\n{}\n'.format(key, '\n'.join(value))
                docparam += '\n'

        from sphinxcontrib.napoleon import Config
        config = Config(napoleon_use_param=True, napoleon_use_rtype=True)
        from sphinxcontrib.napoleon.docstring import NumpyDocstring
        lines = NumpyDocstring(docparam, config).lines()

        output.extend(lines)

        return output

    def __get_function_docs__(cls):

        prefix = '.. function:: '

        output = list()

        def _functions(module, cdef_name):
            functions = list()
            for f in inspect.getmembers(cdef_name[1], inspect.isfunction):
                functions.append(f)
            return functions

        def _ignore_module(module, fdef_name):
            remove = False
            for c in inspect.getmembers(module, inspect.isclass):
                functions = _functions(module, c)
                for f in functions:
                    if f[0] == fdef_name:
                        remove = True
            return remove

        cls_dir = dir(cls)
        for a in dir(MetaInitializer):
            if a in cls_dir:
                cls_dir.remove(a)
        for a in cls_dir:
            for module in cls.MODULES:
                if _ignore_module(module, a):
                    cls_dir.remove(a)

        for attr_name in cls_dir:
            if attr_name.find('__') < 0:
                attr = getattr(cls, attr_name)
                if inspect.isfunction(attr):
                    sig = inspect.signature(attr)

                    if len(dict(sig.parameters)) > 1:
                        fargs = prefix + attr_name + str(sig)
                        output.append(fargs)

                    if inspect.getdoc(attr) is not None:
                        output.append('\n' + inspect.getdoc(attr))
                    output.append('\n')
        return output


class __Field__(metaclass=MetaInitializer):
    """ This is the FieldConstructor """

    def __init__(self, **kwargs):
        if not hasattr(self, '__store__'):
            self.__store__ = dict()

        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def __unlocked_field_params__(cls):
        return cls.__unlocked_fields__

    @classmethod
    def __locked_fields_params__(cls):
        return cls.__locked_fields__

    @classmethod
    def __fields__(cls):
        return cls.__props__

    @classmethod
    def __get_fields__(cls):
        prop = []
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, BaseField):
                prop.append([attr_name, attr])
        return prop

    def __external_fields__(self):
        ex_fields = []
        for i in self.__unlocked_field_params__():
            field = getattr(self.__class__, i)
            if isinstance(field, DataField):
                if field.__field_was_stored__(self):
                    ex_fields.append(i)
            else:
                ex_fields.append(i)
        return ex_fields

    def __copy__(self):
        kwargs = {}
        for p in self.__external_fields__():
            kwargs[p] = getattr(self, p)
        return self.__class__(**kwargs)

    def __deepcopy__(self, memo):
        from copy import deepcopy
        kwargs = {}
        for p in self.__external_fields__():
            kwargs[p] = deepcopy(getattr(self, p), memo)
        return self.__class__(**kwargs)

    def modified_copy(self, **override_kwargs):
        """ Returns a copy, but where the user can
        override properties using. """
        kwargs = {}
        for p in self.__external_fields__():
            kwargs[p] = getattr(self, p)
        kwargs.update(override_kwargs)
        return self.__class__(**kwargs)


class FieldInitializer(__Field__):
    """
    Set the keyword arguments of the class and
    bind geometric property operations to the
    object for API usage.
    """

    def __init__(self, **kwargs):
        if not hasattr(self, '__store__'):
            self.__store__ = dict()
        self.__store_fields__(kwargs)
        self.__validation_check__()

    def __repr__(self):
        class_string = '[SPiRA: {}]'.format(self.__class__.__name__)
        if hasattr(self, '__keywords__'):
            _repr = list()
            for k, v in self.__keywords__.items():
                if ('__' not in k) and (v is not None):
                    _repr.append('{} {}'.format(k, v))
            c = ', '.join(_repr)
            class_string = '{} ({})'.format(class_string, c)
        return class_string

    def __store_fields__(self, kwargs):
        props = self.__fields__()
        for key, value in kwargs.items():
            if key == 'doc':
                self.__doc__ = value
            else:
                if key not in props:
                    raise ValueError("Keyword argument \'{}\' " +
                        "does not match any properties " +
                        "of {}.".format(key, type(self)))
                setattr(self, key, value)

    def __validation_check__(self):
        if not self.validate_parameters():
            raise AttributeError('Width is not large enough.')

    def validate_parameters(self):
        return True


class MetaElemental(MetaInitializer):

    def __call__(cls, *params, **keyword_params):
        kwargs = cls.__map_parameters__(*params, **keyword_params)
        instance = super().__call__(**kwargs)
        instance.__keywords__ = kwargs
        return instance


class MetaCell(MetaInitializer):
    """
    Called when an instance of a SPiRA class is
    created. Pareses all kwargs and passes it to
    the FieldInitializer for storing.

    class Via(spira.Cell):
        layer = param.LayerField()

    Gets called here and passes
    kwargs['layer': 50] to FieldInitializer.
    >>> via = Via(layer=50)
    """

    _ID = 0

    def __call__(cls, *params, **keyword_params):

        kwargs = cls.__map_parameters__(*params, **keyword_params)

        from spira import settings
        lib = None
        if 'library' in kwargs:
            lib = kwargs['library']
            del(kwargs['library'])
        if lib is None:
            lib = settings.get_library()

        if kwargs['name'] is None:
            kwargs['name'] = '{}-{}'.format(cls.__name__, cls._ID)
            cls._ID += 1

        name = kwargs['name']

        cls.__keywords__ = kwargs

        cls = super().__call__(**kwargs)

        retrieved_cell = lib.get_cell(cell_name=name)
        if retrieved_cell is None:
            lib += cls
            return cls
        else:
            del cls
            return retrieved_cell

class CellInitializer(FieldInitializer, metaclass=MetaCell):

    def __str__(self):
        return self.__repr__()

    @property
    def id(self):
        return self.__str__()



# from spira import param
class ElementalInitializer(FieldInitializer, metaclass=MetaElemental):

    # gdspy_commit = param.BoolField()

    def flatten(self):
        return [self]

    def commit_to_gdspy(self, cell, gdspy_commit=None):
        return None

    def dependencies(self):
        return None

    def __str__(self):
        return self.__repr__()

    @property
    def id(self):
        return self.__str__()










