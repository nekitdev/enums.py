# -*- encoding: utf-8 -*-

# type: ignore

"""Enhanced Enum Implementation for Python.

Less sophisticated, less restrictive, more magical and funky!

Example

>>> from enums import Enum

>>> class Color(Enum):
...     ALPHA = 0
...     RED = 1
...     GREEN = 2
...     BLUE = 3

>>> Color.RED  # attribute access
<Color.RED: 1>
>>> Color["GREEN"]  # subscript access
<Color.GREEN: 2>
>>> Color(3)  # call access
<Color.BLUE: 3>

>>> color = Color.from_name("alpha")
>>> print(color.name)
ALPHA
>>> print(color.value)
0
>>> print(color.title)
Alpha

MIT License

Copyright (c) 2020-present nekitdev

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__title__ = "enums"
__author__ = "nekitdev"
__copyright__ = "Copyright 2020-present nekitdev"
__license__ = "MIT"
__version__ = "0.6.0"

import sys
from types import DynamicClassAttribute as dynamic_attribute, FrameType, MappingProxyType
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

try:
    from typing import NoReturn  # type: ignore  # this may error on earlier versions

except ImportError:  # pragma: no cover
    NoReturn = None  # type: ignore

__all__ = (
    # type (metaclass)
    "EnumType",
    # alias (for backwards compatibility)
    "EnumMeta",
    # enumerations
    "Enum",
    "StrEnum",
    "IntEnum",
    # flag boundary
    "FlagBoundary",
    # boundaries
    "CONFORM",
    "EJECT",
    "KEEP",
    "STRICT",
    # flags
    "Flag",
    "IntFlag",
    # traits
    "Trait",
    "Order",
    "StrFormat",
    # auto item
    "auto",
    # unique decorator
    "unique",
    # function with generate_next_value(...) signature
    "enum_generate_next_value",
)

DEFAULT_DOCUMENTATION = "An enumeration."
ENUM_DEFINITION = "Name([trait_type, ...] [data_type] enum_type)"  # enum derive definition
NOT_COVERED = "({value} not covered)"

UNDEFINED = "undefined"  # similar to the string below, denotes undefined items or names
UNKNOWN = "<unknown>"  # string that kind of declares unknown sources (mainly modules)

DEFAULT_DIR_INCLUDE = ["__class__", "__doc__", "__module__", "__members__"]  # some dir() dunders

DESCRIPTOR_ATTRIBUTES = ("__get__", "__set__", "__delete__")  # attributes that define a descriptor
ENUM_PRESERVE = ("__format__", "__repr__", "__str__", "__reduce_ex__")  # to preserve in enums
PICKLE_METHODS = ("__getnewargs_ex__", "__getnewargs__", "__reduce_ex__", "__reduce__")

INVALID_ENUM_NAMES = {"mro", ""}  # any others?

OBJECT_DIR = object.__dir__  # function to use for fetching dirs
OBJECT_NEW = object.__new__  # default new function used to create enum values
USELESS_NEW = {None, None.__new__, object.__new__}  # new functions that are not useful in creation
# NOTE: Enum's new function is added here when it is defined

# some methods defined as strings because we use them in attribute calls or namespace checks
DOC = "__doc__"
MAIN = "__main__"
MODULE = "__module__"
NAME = "__name__"
NEW = "__new__"
NEW_MEMBER = "__new_member__"
REDUCE_EX = "__reduce_ex__"

E = TypeVar("E", bound="Enum")
F = TypeVar("F", bound="Flag")
FB = TypeVar("FB", bound="FlagBoundary")
IF = TypeVar("IF", bound="IntFlag")

T = TypeVar("T")
U = TypeVar("U")

S = TypeVar("S", bound="Singleton")

ENUM_DEFINED = False  # flag that is going to be set after Enum is created
FLAG_DEFINED = False  # flag that will be set after Flag is created

FLAG_FINAL = "Flag"


class Singleton:
    INSTANCE = None

    def __repr__(self) -> str:  # pragma: no cover
        return f"<{self.__class__.__name__}>"

    @classmethod
    def __new__(cls: Type[S], *args: Any, **kwargs: Any) -> S:
        if cls.INSTANCE is None:
            cls.INSTANCE = cast(S, super().__new__(cls))

        return cls.INSTANCE


class NULL(Singleton):
    pass


null = NULL()


class auto:
    value = null


EMPTY = ""
SPACE = " "

DASH = "-"
UNDER = "_"

SEMI = ";"
COMMA = ","

PIPE = "|"

concat_pipe = PIPE.join
concat_separated = (COMMA + SPACE).join
concat_space = SPACE.join

delimiter_to_empty = str.maketrans({DASH: EMPTY, UNDER: EMPTY})
delimiter_to_space = str.maketrans({DASH: SPACE, UNDER: SPACE})
separator_to_space = str.maketrans({SEMI: SPACE, COMMA: SPACE})


def _casefold_name(name: str) -> str:
    return name.casefold().translate(delimiter_to_empty)


def _create_title(entity: Optional[T], on_undefined: str = UNDEFINED) -> str:
    if entity is None:
        name = on_undefined

    else:
        name = str(entity)

    if name.isupper():
        return name.translate(delimiter_to_space).title()

    return name


def bin(value: int, bits: int = 0) -> str:
    """Similar to built-in function bin(),

    except negative values are represented in two's complement,
    and the leading bit always indicates the sign (0 = positive, 1 = negative).
    """

    length = value.bit_length()

    if value < 0:
        sign = 1

        value = ~value ^ ((1 << length) - 1)

    else:
        sign = 0

    digits = f"{value:0>{length}b}"

    return f"0b{sign} {digits:{sign}>{bits}}"


ONE = "1"


def bit_count(value: int) -> int:
    return f"{value:b}".count(ONE)


def _starts_and_ends_with(string: str, char: str, times: int = 1, strict: bool = True) -> bool:
    if len(char) != 1:
        raise ValueError(f"Expected char to be a string of length 1, got {char!r}.")

    if not times:
        return True  # all strings start and end with empty strings

    part = char * times
    part_len = len(part)

    main_check = (
        len(string) > part_len  # sanity check if we should even begin to check the string
        and string[:part_len] == part  # starts with given char * times
        and string[-part_len:] == part  # ends with the required string
    )

    if strict:  # strict check
        return (
            main_check  # passes main checks
            and string[part_len] != char  # char after start is different
            and string[~part_len] != char  # char before end is different (note: ~x = -x-1)
        )

    return main_check  # relaxed check


ENUM = "enum"

SPECIAL = (UNDER, ENUM + UNDER)


def _is_special(string: str, special: Union[str, Tuple[str, ...]] = SPECIAL) -> bool:
    return string.startswith(special)


try:
    _get_frame = sys._getframe

except AttributeError:  # pragma: no cover
    class _GetFrame(Exception):
        pass

    def _get_frame(level: int = 0) -> FrameType:
        try:
            raise _GetFrame()

        except _GetFrame as error:
            traceback = error.__traceback__

            if traceback is None:
                raise ValueError("No traceback to get the frame from.")

            current_frame = traceback.tb_frame

            if current_frame is None:
                raise ValueError("Can not get current frame.")

            frame = current_frame.f_back

            if frame is None:
                raise ValueError("Can not get caller frame.")

            if level:
                for _ in range(level):
                    frame = frame.f_back

                    if frame is None:
                        raise ValueError("Call stack is not deep enough.") from None

            return frame


def _is_strict_dunder(string: str) -> bool:
    return _starts_and_ends_with(string, UNDER, times=2, strict=True)


def _is_descriptor(some_object: Any) -> bool:
    return any(
        hasattr(some_object, attribute)
        for attribute in DESCRIPTOR_ATTRIBUTES
    )


def _traverse_data_types(bases: Tuple[Type[Any], ...]) -> Iterator[Type[Any]]:
    for chain in bases:
        candidate: Optional[Type[Any]] = None

        for base in chain.__mro__:
            if base is object:  # not useful in our case
                continue

            elif issubclass(base, Enum):  # derived from enum -> try using member type
                member_type = base._member_type

                if member_type is not object:  # something actually useful
                    yield member_type
                    break  # move onto the next chain

            elif NEW in base.__dict__:
                yield candidate or base  # if we have a candidate, yield it, and use base otherwise
                break

            else:
                candidate = base


def _find_data_type(bases: Tuple[Type[Any], ...]) -> Type[Any]:
    traverser = _traverse_data_types(bases)

    data_type = next(traverser, object)

    excessive = list(traverser)

    if excessive:
        names = (excessive_data_type.__name__ for excessive_data_type in excessive)

        raise TypeError(
            f"Excessive data types (using {data_type.__name__}): {concat_separated(names)}"
        )

    return data_type


def _find_enum_type(bases: Tuple[Type[Any], ...]) -> Type[E]:
    if not bases:
        return Enum if ENUM_DEFINED else object

    enum_type = bases[-1]

    if ENUM_DEFINED and not issubclass(enum_type, Enum):
        raise TypeError(f"New enumerations should be created as {ENUM_DEFINITION!r}.")

    if enum_type._member_map:
        raise TypeError("Enumerations can not be extended.")

    return enum_type


def _make_class_unpicklable(cls: Type[T]) -> None:
    def _break_on_reduce_attempt(instance: T, protocol: int) -> NoReturn:  # pragma: no cover
        raise TypeError(f"{instance} can not be pickled.")

    setattr(cls, REDUCE_EX, _break_on_reduce_attempt)
    setattr(cls, MODULE, UNKNOWN)


def _make_namespace_unpicklable(namespace: Dict[str, Any]) -> None:
    def _break_on_reduce_attempt(instance: Any, protocol: int) -> NoReturn:  # pragma: no cover
        raise TypeError(f"{instance} can not be pickled.")

    namespace.update({REDUCE_EX: _break_on_reduce_attempt, MODULE: UNKNOWN})


VALUE = "value"
VALUE_ATTRIBUTE = UNDER + VALUE


def _create_enum_member(
    member_name: Optional[str],
    member_type: Type[T],
    member_value: Any,
    enum_class: Type[E],
    new_function: Callable[..., E],
    use_args: bool,
    dynamic_attributes: Iterable[str],
) -> E:
    """Create and add enum member. Setting name to None has special meaning;
    This will attempt to add to value -> member map only;
    Said special case is intended for creation of composite flags.
    """
    # double check if already defined, and raise error in that case
    if member_name is not None:
        if member_name in enum_class._member_map:
            raise ValueError(
                f"{member_name!r} already defined as: {enum_class._member_map[member_name]!r}."
            )

    # handle value and initialization

    if isinstance(member_value, tuple):  # do nothing if value is an instance of tuple
        args = member_value

    else:  # wrap into tuple otherwise
        args = (member_value,)

    if member_type is tuple:  # special case for tuple enums
        args = (args,)  # wrap args again another time

    if use_args:
        enum_member = new_function(enum_class, *args)

        if not hasattr(enum_member, VALUE_ATTRIBUTE):  # if value was not defined already
            if member_type is not object:
                member_value = member_type(*args)

            enum_member._value = member_value

    else:
        enum_member = new_function(enum_class)

        if not hasattr(enum_member, VALUE_ATTRIBUTE):  # if value was not defined previously
            enum_member._value = member_value

    enum_class._member_values.append(member_value)

    enum_member._name = member_name
    enum_member.__object_class__ = enum_class
    enum_member.__init__(*args)

    enum_member._sort_order = len(enum_class._member_names)  # for sorting by definition

    if member_name is not None:
        for name, canonical_member in enum_class._member_map.items():
            if canonical_member._value == enum_member._value:
                enum_member = canonical_member
                break

        else:
            if not FLAG_DEFINED or not issubclass(enum_class, Flag):
                enum_class._member_names.append(member_name)

            elif FLAG_DEFINED and issubclass(enum_class, Flag) and _is_single_bit(member_value):
                enum_class._member_names.append(member_name)

        # boost performance for any member that would not shadow dynamic_attribute
        if member_name not in dynamic_attributes:
            setattr(enum_class, member_name, enum_member)

        # now add to member mapping
        enum_class._member_map[member_name] = enum_member

    try:
        # see if member with this value exists
        previous_member = enum_class._value_map.get(member_value)

        if previous_member is not None:
            if previous_member._name is None:  # if the name is not set
                previous_member._name = enum_member._name

            enum_member = previous_member

        # attempt to add value to value -> member map in order to make lookups constant, O(1)
        # if value is not hashable, this will fail and our lookups will be linear, O(n)
        enum_class._value_map.setdefault(member_value, enum_member)  # in order to support threading

    except TypeError:  # not hashable
        pass

    return enum_member  # return member in case something wants to use it


def enum_generate_next_value(
    name: str, start: Optional[T], count: int, member_values: List[T]
) -> T:  # pragma: no cover
    """Empty function that shows signature of enum_generate_next_value() functions.

    name: str -> Name of enum entry which value should be generated.
    start: Optional[T] -> Passed as None if auto() is being used.
    count: int -> Amount of already existing unique members at the time of the call.
    member_values: List[T] -> List of previous member values.
    """
    raise NotImplementedError


def incremental_next_value(name: str, start: Optional[T], count: int, member_values: List[T]) -> T:
    """Implementation of enum_generate_next_value()
    that automatically increments last possible member value.

    If not possible to generate new value, returns start (1 by default).
    """
    if start is None:
        start = cast(T, 1)

    for member_value in reversed(member_values):  # find value we can increment
        try:
            return member_value + 1  # type: ignore

        except TypeError:  # unsupported operand type(s) for +: T, int  # pragma: no cover
            pass

    else:
        return start


def strict_bit_next_value(
    name: str, start: Optional[int], count: int, member_values: List[int]
) -> int:
    """Implementation of enum_generate_next_value()
    that automatically generates next power of two after previous value.

    If not possible to generate new value, returns start (1 by default).
    """
    if start is None:
        start = 1

    for member_value in reversed(member_values):
        try:
            high_bit = _high_bit(member_value)

        except Exception:  # noqa
            raise ValueError(f"Invalid flag value: {member_value!r}.") from None

        return 1 << (high_bit + 1)

    else:
        return start


def casefold_name_next_value(
    name: str, start: Optional[str], count: int, member_values: List[str]
) -> str:
    return name.casefold()


AUTO_ON_MISSING = "enum_auto_on_missing"
GENERATE_NEXT_VALUE = "enum_generate_next_value"
IGNORE = "enum_ignore"
START = "enum_start"


class EnumDict(Generic[T], Dict[str, Any]):
    def __init__(self) -> None:
        super().__init__()

        self._auto_on_missing: bool = False
        self._start: Optional[T] = None
        self._generate_next_value: Optional[Callable[..., T]] = None
        self._member_names: List[str] = []
        self._member_values: List[T] = []
        self._ignore: List[str] = []

    def __setitem__(self, key: str, value: Any) -> None:
        if key == AUTO_ON_MISSING:
            self._auto_on_missing = bool(value)

        elif key == IGNORE:
            if isinstance(value, str):  # process enum_ignore if given a string
                ignore = filter(bool, value.translate(separator_to_space).split())

            else:
                ignore = value

            self._ignore = list(ignore)

        elif key == GENERATE_NEXT_VALUE:  # setting enum_generate_next_value(...) function
            self._generate_next_value = cast(Callable[..., T], value)

        elif key == START:  # set starting value
            self._start = cast(T, value)

        elif key in self._member_names:  # something overrides enum?
            raise ValueError(f"Attempt to reuse key: {key!r}.")

        elif _is_strict_dunder(key) or _is_descriptor(value) or key in self._ignore:
            pass

        else:
            if key in self:  # enum overrides something?
                raise ValueError(f"{key!r} already defined as: {self[key]!r}.")

            if isinstance(value, auto):
                if value.value is null:  # null -> generate next value
                    if self._generate_next_value is None:
                        raise RuntimeError(
                            "Attempt to use auto value while "
                            "enum_generate_next_value was not defined."
                        )

                    value.value = self._generate_next_value(
                        key, self._start, len(self._member_names), self._member_values.copy()
                    )

                value = cast(T, value.value)

            self._member_names.append(key)
            self._member_values.append(value)

        super().__setitem__(key, value)

    def __missing__(self, key: str) -> None:
        if _is_strict_dunder(key) or not self._auto_on_missing:
            raise KeyError(key)

        self[key] = auto()

    def update(  # type: ignore
        self,
        mapping: Union[Iterable[Tuple[str, Any]], Mapping[str, Any]],
        **keywords: Any,
    ) -> None:  # pragma: no cover
        items = mapping.items() if isinstance(mapping, Mapping) else mapping

        for key, value in items:
            self[key] = value

        for key, value in keywords.items():
            self[key] = value


def _find_new(
    namespace: EnumDict[U], member_type: Type[T], enum_type: Type[E]
) -> Tuple[Callable[..., T], bool, bool]:  # new_function, new_member_save, new_use_args
    """Find __new__ function to create member types with."""
    new_function = namespace.get(NEW)

    if new_function is None:
        new_member_save = False

        for method in (NEW_MEMBER, NEW):  # check for __new_member__ first
            for possible in (member_type, enum_type):
                target = getattr(possible, method, None)

                if target not in USELESS_NEW:
                    new_function = target
                    break

            if new_function is not None:  # assigned in inner loop, break from outer loop
                break

        else:
            new_function = OBJECT_NEW

    else:
        new_member_save = True

    new_use_args = new_function is not OBJECT_NEW

    return new_function, new_member_save, new_use_args


DIRECT_CALLER = 1
WRAPPING_CALLER = 2


BOUNDARY = "boundary"
BOUNDARY_ATTRIBUTE = UNDER + BOUNDARY

MEMBER_MAP = "member_map"
MEMBER_MAP_ATTRIBUTE = UNDER + MEMBER_MAP


class EnumType(type):
    @classmethod
    def __prepare__(
        meta_cls,
        cls: str,
        bases: Tuple[Type[Any], ...],
        *,
        auto_on_missing: bool = False,
        ignore: Optional[Union[str, Iterable[str]]] = None,
        start: Optional[T] = None,
        **kwargs: Any,
    ) -> EnumDict[T]:
        """Prepare class initialization."""
        enum_dict = EnumDict()

        enum_type = _find_enum_type(bases)

        enum_dict.update({
            AUTO_ON_MISSING: auto_on_missing,
            GENERATE_NEXT_VALUE: getattr(enum_type, GENERATE_NEXT_VALUE, None),
            IGNORE: ignore or [],
            START: start,
        })

        return enum_dict

    def __new__(
        meta_cls,
        cls_name: str,
        bases: Tuple[Type[Any], ...],
        namespace: EnumDict[T],
        *,
        # boundary for Flag types
        boundary: Optional[FB] = None,
        # these are used and processed by our meta_cls.__prepare__(...), outside this function
        auto_on_missing: bool = False,
        ignore: Optional[Union[str, Iterable[str]]] = None,
        start: Optional[T] = None,
    ) -> Type[E]:  # XXX: perhaps we should have FlagType?
        """Initialize new class. This function is *very* magical."""
        global ENUM_DEFINED  # alright, magical things here
        global FLAG_DEFINED  # magic!

        # add enum_ignore to self
        enum_ignore = list(namespace.get(IGNORE, []))
        enum_ignore.append(IGNORE)

        for key in enum_ignore:  # remove all keys in enum_ignore
            if key in namespace:
                del namespace[key]

        enum_type = _find_enum_type(bases)
        member_type = _find_data_type(bases)

        new_function, new_member_save, new_use_args = _find_new(
            namespace, member_type, enum_type
        )

        enum_members = {}

        flag_mask = 0

        for name in namespace._member_names:
            value = namespace[name]

            if isinstance(value, int):
                flag_mask |= value  # compute flag mask in case we are working on the Flag

            enum_members[name] = value  # save all members into separate mapping

        all_bits = (1 << flag_mask.bit_length()) - 1

        # remove enum members so they do not get baked into new class
        for name in namespace._member_names:
            del namespace[name]

        # check for invalid names
        invalid_names = set(enum_members) & INVALID_ENUM_NAMES

        if invalid_names:
            raise ValueError(f"Invalid member names: {concat_separated(invalid_names)}.")

        # add default documentation if we need to
        namespace.setdefault(DOC, DEFAULT_DOCUMENTATION)

        if REDUCE_EX not in namespace:
            if member_type is not object:
                member_type_dict = member_type.__dict__

                if not any(method_name in member_type_dict for method_name in PICKLE_METHODS):
                    _make_namespace_unpicklable(namespace)

        # create dummy enum class to manipulate Method Resolution Order (MRO)

        dummy_class = super().__new__(meta_cls, cls_name, bases, EnumDict())

        mro = list(dummy_class.mro())

        try:
            mro.remove(dummy_class)

        except ValueError:  # pragma: no cover
            pass

        try:
            if mro.index(member_type) < mro.index(enum_type):
                # we need to preserve enum_type functions
                mro.remove(enum_type)
                mro.insert(mro.index(member_type), enum_type)

        except ValueError:  # pragma: no cover
            pass

        bases = tuple(mro)  # now back to tuple

        # create our new class
        enum_class = super().__new__(meta_cls, cls_name, bases, namespace)

        for name in ENUM_PRESERVE:  # on top of it, preserve names that should ideally belong to us
            if name in namespace:
                continue

            class_method = getattr(enum_class, name)
            type_method = getattr(member_type, name, None)
            enum_method = getattr(enum_type, name, None)

            if type_method is not None and type_method is class_method:
                setattr(enum_class, name, enum_method)

        enum_class._start = start  # save value in case generate_next_value(...) is called later on

        # add member names list and member type, along with new_function and new_use_args
        enum_class._member_names: List[str] = []  # list of member names
        enum_class._member_values: List[T] = []  # list of member values
        enum_class._member_type = member_type  # member type
        enum_class._new_function = new_function
        enum_class._use_args = new_use_args

        # add member mappings
        enum_class._member_map: Dict[str, E] = {}  # name -> member mapping
        enum_class._value_map: Dict[T, E] = {}  # value -> member mapping for hashable values

        # save DynamicClassAttribute attributes from super classes so we know if
        # we can take the shortcut of storing members in the class dict

        dynamic_attributes: Set[str] = {
            key
            for subclass in enum_class.mro()
            for key, value in subclass.__dict__.items()
            if isinstance(value, dynamic_attribute)
        }

        enum_class._dynamic_attributes = dynamic_attributes

        for member_name in namespace._member_names:  # create our fellow enum members
            _create_enum_member(
                member_name=member_name,
                member_type=member_type,
                member_value=enum_members[member_name],
                enum_class=enum_class,
                new_function=new_function,
                use_args=new_use_args,
                dynamic_attributes=dynamic_attributes,
            )

        if ENUM_DEFINED:  # if enum was created (this will be false on initial run)
            if new_member_save:  # save as new_member if needed
                enum_class.__new_member__ = new_function

            enum_class.__new__ = Enum.__new__

        else:
            ENUM_DEFINED = True

        # in the end, handle flags, their boundaries and attributes
        is_flag = FLAG_DEFINED and issubclass(enum_class, Flag)

        is_flag_final = False

        if not FLAG_DEFINED and cls_name == FLAG_FINAL:
            FLAG_DEFINED = True

            is_flag_final = True

        if is_flag_final or is_flag:  # save flag attributes
            enum_class._flag_mask = flag_mask
            enum_class._all_bits = all_bits

            enum_class._boundary = FlagBoundary(
                boundary or getattr(enum_type, BOUNDARY_ATTRIBUTE, None)
            )

        if is_flag:
            enum_class._modify_mask_and_iter()

        return enum_class  # finally! :)

    def _modify_mask_and_iter(cls: Type[F]) -> None:
        single_bit_total = 0
        multi_bit_total = 0

        for flag in cls._member_map.values():
            flag_value = flag._value

            if _is_single_bit(flag_value):
                single_bit_total |= flag_value

            else:
                multi_bit_total |= flag_value  # multi-bit flags are considered aliases

        if cls._boundary is not KEEP:
            missed = list(_iter_bits_lsb(multi_bit_total & ~single_bit_total))

            if missed:
                raise TypeError(
                    f"Invalid flag {cls.__name__!r}; "
                    f"missing values: {concat_separated(map(str, missed))}"
                )

        cls._flag_mask = single_bit_total

        flag_list = [flag._value for flag in cls]

        if sorted(flag_list) != flag_list:
            # definition order is not the same as increasing value order
            cls._iter_member = cls._iter_member_by_defintion

    def add_member(cls: Type[E], name: str, value: T) -> E:
        """Add new member to the enumeration; auto() is allowed."""
        if isinstance(value, auto):
            if value.value is null:  # null -> generate next value
                value.value = cls.enum_generate_next_value(
                    name, cls._start, len(cls._member_names), cls._member_values.copy()
                )

            value = value.value

        member = _create_enum_member(
            member_name=name,
            member_type=cls._member_type,
            member_value=value,
            enum_class=cls,
            new_function=cls._new_function,
            use_args=cls._use_args,
            dynamic_attributes=cls._dynamic_attributes,
        )

        if FLAG_DEFINED and issubclass(cls, Flag):
            cls._flag_mask |= member._value  # include value in the mask
            cls._all_bits = (1 << cls._flag_mask.bit_length()) - 1  # re-calculate all_bits

            cls._modify_mask_and_iter()  # modify mask and iteration, if needed

        return member

    def update(cls, **name_to_value: T) -> None:
        """Add new member to the enumeration for each name and value in arguments supplied."""
        for name, value in name_to_value.items():
            cls.add_member(name, value)

    @property
    def boundary(cls) -> Optional[FB]:
        return getattr(cls, BOUNDARY_ATTRIBUTE, None)

    def __call__(
        cls: Type[E],
        value: Any,
        names: Union[str, Dict[str, U], List[str], Tuple[str, ...]] = (),
        module: Optional[str] = None,
        qualname: Optional[str] = None,
        type: Optional[Type[T]] = None,
        start: Optional[T] = None,
        boundary: Optional[FB] = None,
        direct_call: bool = False,
        **members: U,
    ) -> Union[E, Type[E]]:
        """With value argument only, search member by value.
        Otherwise, functional API: create new enum class.
        """
        if not members and not names and not type:
            return cls.__new__(cls, value)

        return cls.create(
            value,
            names,
            module=module,
            qualname=qualname,
            type=type,
            start=start,
            boundary=boundary,
            direct_call=direct_call,
            **members,
        )

    def create(
        cls: Type[E],
        cls_name: str,
        names: Union[str, Dict[str, U], List[str], Tuple[str, ...]] = (),
        *,
        module: Optional[str] = None,
        qualname: Optional[str] = None,
        type: Optional[Type[T]] = None,
        start: Optional[T] = None,
        boundary: Optional[FB] = None,
        direct_call: bool = True,
        **members: U,
    ) -> Type[E]:
        """Convenient implementation of creating a new enum."""
        meta_cls = cls.__class__

        bases = (cls,) if type is None else (type, cls)

        enum_type = _find_enum_type(bases)
        namespace = meta_cls.__prepare__(cls_name, bases)

        if isinstance(names, str):  # parse names if required
            names = list(filter(bool, names.translate(separator_to_space).split()))

        if isinstance(names, (tuple, list)) and names and isinstance(names[0], str):
            original_names, names = names, []
            member_values = []

            for count, name in enumerate(original_names):
                # generate values
                value = enum_type.enum_generate_next_value(name, start, count, member_values.copy())

                member_values.append(value)

                names.append((name, value))

        for item in names:  # either mapping or (name, value) pair
            if isinstance(item, str):
                member_name, member_value = item, names[item]
            else:
                member_name, member_value = item

            namespace[member_name] = member_value

        for member_name, member_value in members.items():
            namespace[member_name] = member_value

        enum_class = meta_cls.__new__(meta_cls, cls_name, bases, namespace, boundary=boundary)

        if module is None:
            try:
                module = _get_frame(
                    DIRECT_CALLER if direct_call else WRAPPING_CALLER
                ).f_globals.get(NAME)

            except (AttributeError, ValueError):  # pragma: no cover
                pass

        if module is None:  # pragma: no cover
            _make_class_unpicklable(enum_class)

        else:
            enum_class.__module__ = module

        if qualname is not None:
            enum_class.__qualname__ = qualname

        return enum_class

    def __bool__(cls) -> bool:
        return True  # classes and types should always return True

    def __contains__(cls: Type[E], member: E) -> bool:
        if not isinstance(member, Enum):
            raise TypeError(
                "Unsupported operand type(s) for 'in': '{other_name}' and '{self_name}'".format(
                    other_name=type(member).__qualname__, self_name=cls.__class__.__qualname__
                )
            )

        return isinstance(member, cls) and member._name in cls._member_map

    def __delattr__(cls, name: str) -> None:
        if name in cls._member_map:
            raise AttributeError(f"Can not delete Enum member: {name!r}.")

        super().__delattr__(name)

    def __getattr__(cls: Type[E], name: str) -> E:
        if _is_strict_dunder(name):
            raise AttributeError(name)

        try:
            return cls._member_map[name]

        except KeyError:
            raise AttributeError(name) from None

    def __getitem__(cls: Type[E], name: str) -> E:
        return cls._member_map[name]

    def __iter__(cls: Type[E]) -> Iterator[E]:
        """Same as cls.get_members()."""
        return cls.get_members()

    def __reversed__(cls: Type[E]) -> Iterator[E]:
        """Same as cls.get_members(reverse=True)."""
        return cls.get_members(reverse=True)

    def __len__(cls) -> int:
        """Return count of unique members (no aliases)."""
        return len(cls._member_names)

    def __repr__(cls) -> str:
        """Standard-like enum class representation."""
        return f"<enum {cls.__name__!r}>"

    def __setattr__(cls, name: str, value: T) -> None:
        """Set new attribute, blocking member reassign attempts.
        To add new fields, consider using Enum.add_member or Enum.update.
        """
        member_map = cls.__dict__.get(MEMBER_MAP_ATTRIBUTE, {})  # we have to prevent recursion

        if name in member_map:
            raise AttributeError(f"Attempt to reassign enum member: {member_map[name]}.")

        super().__setattr__(name, value)

    def __dir__(cls) -> List[str]:
        added_behavior = [key for key in OBJECT_DIR(cls) if not _is_special(key)]

        return DEFAULT_DIR_INCLUDE + added_behavior + cls._member_names

    def get_members(cls: Type[E], reverse: bool = False) -> Iterator[E]:
        """Return iterator over unique members (without aliases), optionally reversing it."""
        names = cls._member_names

        if reverse:
            names = reversed(names)

        return (cls._member_map[name] for name in names)

    @property
    def members(cls: Type[E]) -> Mapping[str, E]:
        """Return mapping proxy for member map (includes aliases).
        Order is guaranteed from Python 3.7 (CPython 3.6) only.
        """
        return MappingProxyType(cls._member_map)

    __members__ = members

    @property
    def casefold_names(cls: Type[E]) -> Dict[str, E]:
        """Create mapping of casefold_name -> member for CI (case insensitive) comparison/lookup."""
        return {_casefold_name(name): member for name, member in cls.members.items()}

    def from_name(cls, name: str) -> None:
        """CI (case insensitive) member by name lookup."""
        return cls.casefold_names[_casefold_name(name)]

    def from_value(cls: Type[E], value: T, default: Union[U, NULL] = null) -> E:
        """Lookup member by name and value. On failure, call from_value(default)."""
        if isinstance(value, str):
            try:
                return cls.from_name(value)

            except KeyError:
                pass

        try:
            return cls(value)

        except Exception:  # noqa
            if default is null:
                raise

            return cls.from_value(cast(U, default))

    def as_dict(cls) -> Dict[str, T]:
        """Return casefold_name -> member_value mapping overall all members."""
        return {name.casefold(): member.value for name, member in cls.members.items()}


EnumMeta = EnumType  # alias for compatibility purposes


class Enum(metaclass=EnumType):
    """Generic enumeration.

    Derive from this class to define new enumerations.
    """

    def __new__(cls: Type[E], value: T) -> E:
        """Implement member by value lookup."""
        # all enum instances are created during class construction without calling this method;
        # this method is called by the metaclass __call__ and pickle

        if type(value) is cls:
            return value

        try:
            return cls._value_map[value]

        except KeyError:
            # not found, no need to do long O(n) search
            pass

        except TypeError:
            # not there, then do long search, O(n) behavior
            for member in cls._member_map.values():
                if member._value == value:
                    return member

        # still not found -> try enum_missing hook
        try:
            exception = None
            result = cls.enum_missing(value)

        except AttributeError:
            result = None

        except Exception as error:
            exception = error
            result = None

        if isinstance(result, cls):
            return result

        elif (
            FLAG_DEFINED and issubclass(cls, Flag)
            and cls._boundary is EJECT and isinstance(result, int)
        ):
            return result

        else:
            error_invalid = ValueError(f"{value!r} is not a valid {cls.__name__}.")

            if result is None and exception is None:  # no result, no error
                raise error_invalid

            elif exception is None:
                exception = ValueError(
                    f"Error in {cls.__name__}.enum_missing: "
                    f"returned {result} instead of None or a valid member."
                )

            raise error_invalid from exception

    enum_generate_next_value = staticmethod(incremental_next_value)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}.{self._name}: {self._value}>"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}.{self._name}"

    def __format__(self, format_spec: str) -> str:
        # pure enum
        if self._member_type is object:
            cls, value = str, str(self)

        # mix-in enum
        else:
            cls, value = self._member_type, self._value

        return cls.__format__(value, format_spec)

    def __hash__(self) -> int:
        return hash(self._name)

    def __reduce_ex__(self: E, protocol: int) -> Tuple[Type[E], T]:
        return self.__class__, (self._value,)

    def __dir__(self) -> List[str]:
        added_behavior = [
            key for key in OBJECT_DIR(self) if not _is_special(key) and key not in self._member_map
        ]

        return DEFAULT_DIR_INCLUDE + added_behavior

    @dynamic_attribute
    def title(self) -> str:
        """Title (human-readable name) of the Enum member."""
        return _create_title(self._name)

    @dynamic_attribute
    def name(self) -> Optional[str]:
        """Name of the Enum member."""
        return self._name

    @dynamic_attribute
    def value(self) -> T:
        """Value of the Enum member."""
        return self._value


USELESS_NEW.add(Enum.__new__)


class IntEnum(int, Enum):
    """Generic enumeration for integer-based values."""


class StrEnum(str, Enum):
    """Generic enumeration for string-based values."""

    enum_generate_next_value = staticmethod(casefold_name_next_value)


def unique(enumeration: Type[E]) -> Type[E]:
    """Class decorator for enumerations ensuring unique member values."""
    duplicates = []

    for name, member in enumeration.members.items():
        if name != member.name:
            duplicates.append((name, member.name))

    if duplicates:
        alias_details = concat_separated(f"{alias} -> {name}" for alias, name in duplicates)

        raise ValueError(f"Duplicates found in {enumeration!r}: {alias_details}.")

    return enumeration


class FlagBoundary(StrEnum):
    """Simple enumeration for Flag boundaries.

    "strict" -> error is raised (default for Flag)
    "conform" -> extra bits are discarded
    "eject" -> lose flag status (default for IntFlag)
    "keep" -> keep flag status and all bits
    """

    STRICT = auto()
    CONFORM = auto()
    EJECT = auto()
    KEEP = auto()


STRICT, CONFORM, EJECT, KEEP = FlagBoundary


def _high_bit(value: int) -> int:
    """Return index of the highest bit, and -1 if value is 0."""
    return value.bit_length() - 1


def _is_single_bit(value: int) -> bool:
    if not value:
        return False  # no bits

    value &= value - 1

    return not value


def _iter_bits_lsb(value: int) -> Iterator[int]:  # least significant bit
    while value:
        bit = value & (~value + 1)  # essentially (value & -value)

        yield bit

        value ^= bit


class Flag(Enum, boundary=STRICT):
    """Support for bit flags."""

    enum_generate_next_value = staticmethod(strict_bit_next_value)

    @classmethod
    def _iter_member_by_value(cls: Type[F], value: int) -> Iterator[F]:
        """Extract all members from the value in increasing value order."""
        for value in _iter_bits_lsb(value & cls._flag_mask):
            yield cls._value_map[value]

    _iter_member = _iter_member_by_value

    @classmethod
    def _iter_member_by_defintion(cls: Type[F], value: int) -> Iterator[F]:
        """Extract all members from the value in definition order."""
        yield from sorted(
            cls._iter_member_by_value(value),
            key=lambda flag: flag._sort_order,
        )

    def __iter__(self: F) -> Iterator[F]:
        yield from self._iter_member(self._value)

    @classmethod
    def enum_missing(cls: Type[F], value: int) -> Union[int, F]:
        """Create composite members on missing enums."""
        if not isinstance(value, int):
            raise ValueError(f"{value!r} is not a valid {cls.__name__}.")

        flag_mask = cls._flag_mask
        all_bits = cls._all_bits

        boundary = cls._boundary

        negative_value: Optional[int] = None

        if (
            # must be in range (e.g. -16 <-> +15, i.e. ~15 <-> 15)
            not ~all_bits <= value <= all_bits
            # must not include any skipped flags
            or value & (all_bits ^ flag_mask)
        ):
            if boundary is STRICT:
                bits = max(value.bit_length(), flag_mask.bit_length())

                raise ValueError(
                    f"Invalid value {value!r} in {cls.__name__}:\n"
                    f"    given {bin(value, bits)}\n"
                    f"  allowed {bin(flag_mask, bits)}"
                )

            elif boundary is CONFORM:
                value &= flag_mask

            elif boundary is EJECT:
                return value

            elif boundary is KEEP:
                if value < 0:
                    value = max(all_bits + 1, 1 << value.bit_length()) + value

            else:  # pragma: no cover  # huh?
                raise ValueError(f"Unknown flag boundary: {cls._boundary!r}.")

        if value < 0:
            negative_value = value
            value += all_bits + 1

        unknown = value & ~flag_mask

        if unknown and boundary is not KEEP:  # pragma: no cover  # hm?
            raise ValueError(
                f"{cls.__name__}({value!r}) -> unknown values {unknown!r} [{bin(unknown)}]"
            )

        member = _create_enum_member(
            member_name=None,
            member_type=cls._member_type,
            member_value=value,
            enum_class=cls,
            new_function=cls._new_function,
            use_args=cls._use_args,
            dynamic_attributes=cls._dynamic_attributes,
        )

        if negative_value is not None:
            cls._value_map[negative_value] = member

        return member

    def __contains__(self: F, other: F) -> bool:
        if not isinstance(other, self.__class__):
            raise TypeError(
                "Unsupported operand type(s) for 'in': '{other_name}' and '{self_name}'".format(
                    other_name=type(other).__qualname__, self_name=self.__class__.__qualname__
                )
            )

        if not self._value or not other._value:
            return False

        return other._value & self._value == other._value

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}.{self._composite_name}: {self._value}>"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}.{self._composite_name}"

    def __len__(self) -> int:
        return bit_count(self._value)

    @classmethod
    def from_args(cls: Type[F], *args: int) -> F:
        result = cls(0)

        for arg in args:
            result |= cls.from_value(arg)

        return result

    @classmethod
    def _prepare_names(cls: Type[F], value: int) -> Tuple[List[str], int]:
        flag_mask = cls._flag_mask

        unknown = value & ~flag_mask
        value &= flag_mask

        names = [flag._name for flag in cls._iter_member(value)]

        return names, unknown

    @property
    def _composite_name(self) -> str:
        if self._name is None:
            names, unknown = self._prepare_names(self._value)

            if not names:
                return hex(unknown)

            if unknown:
                names.append(hex(unknown))

            return concat_pipe(names)

        return self._name

    @dynamic_attribute
    def name(self) -> str:
        """Name of the flag, which accounts for composites."""
        return self._composite_name

    @property
    def _composite_title(self) -> str:
        if self._name is None:
            names, unknown = self._prepare_names(self._value)

            if not names:
                return hex(unknown)

            title = concat_separated(map(_create_title, names))

            if unknown:
                return title + SPACE + NOT_COVERED.format(value=hex(unknown))

            return title

        return _create_title(self._name)

    @dynamic_attribute
    def title(self) -> str:
        """Title of the Flag, which accounts for composites."""
        return self._composite_title

    def __bool__(self) -> bool:
        return bool(self._value)

    def __or__(self: F, other: F) -> F:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.__class__(self._value | other._value)

    def __and__(self: F, other: F) -> F:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.__class__(self._value & other._value)

    def __xor__(self: F, other: F) -> F:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.__class__(self._value ^ other._value)

    def __invert__(self: F) -> F:
        if self._boundary is KEEP:
            return self.__class__(~self._value)

        return self.__class__(self._flag_mask ^ self._value)

    __ior__ = __or__
    __iand__ = __and__
    __ixor__ = __xor__

    __ror__ = __or__
    __rand__ = __and__
    __rxor__ = __xor__


class IntFlag(int, Flag, boundary=KEEP):
    """Support for integer-based bit flags."""

    def __contains__(self: F, other: Union[int, F]) -> bool:
        if isinstance(other, self.__class__):
            value = other._value

        elif isinstance(other, int):
            value = other

        else:
            raise TypeError(
                "Unsupported operand type(s) for 'in': '{other_name}' and '{self_name}'".format(
                    other_name=type(other).__qualname__, self_name=self.__class__.__qualname__
                )
            )

        if not self._value or not value:
            return False

        return value & self._value == value

    def __or__(self: F, other: Union[int, F]) -> Union[int, F]:
        if isinstance(other, self.__class__):
            value = other._value

        elif isinstance(other, int):
            value = other

        else:  # pragma: no cover
            return NotImplemented

        return self.__class__(self._value | value)

    def __and__(self: F, other: Union[int, F]) -> Union[int, F]:
        if isinstance(other, self.__class__):
            value = other._value

        elif isinstance(other, int):
            value = other

        else:  # pragma: no cover
            return NotImplemented

        return self.__class__(self._value & value)

    def __xor__(self: F, other: Union[int, F]) -> Union[int, F]:
        if isinstance(other, self.__class__):
            value = other._value

        elif isinstance(other, int):
            value = other

        else:  # pragma: no cover
            return NotImplemented

        return self.__class__(self._value ^ value)

    __ior__ = __or__
    __iand__ = __and__
    __ixor__ = __xor__

    __ror__ = __or__
    __rand__ = __and__
    __rxor__ = __xor__


class Trait:
    """Base class to indicate traits (also known as mixins) for enums."""


class StrFormat(Trait):
    """Trait that calls str(member) when formatting."""

    def __format__(self, format_spec: str) -> str:
        return str(self).__format__(format_spec)


class Order(Trait):
    """Trait that implements ordering (==, !=, <, >, <= and >=) for enums."""

    _name: str
    _value: Any

    def __hash__(self) -> int:  # need to redefine because we implement == and !=
        return hash(self._name)

    def __eq__(self, other: Any) -> bool:
        try:
            other = self.__class__(other)

        except Exception:  # noqa  # pragma: no cover
            return NotImplemented

        return self._value == other._value

    def __ne__(self, other: Any) -> bool:
        try:
            other = self.__class__(other)

        except Exception:  # noqa  # pragma: no cover
            return NotImplemented

        return self._value != other._value

    def __lt__(self, other: Any) -> bool:
        try:
            other = self.__class__(other)

        except Exception:  # noqa  # pragma: no cover
            return NotImplemented

        return self._value < other._value

    def __gt__(self, other: Any) -> bool:
        try:
            other = self.__class__(other)

        except Exception:  # noqa  # pragma: no cover
            return NotImplemented

        return self._value > other._value

    def __le__(self, other: Any) -> bool:
        try:
            other = self.__class__(other)

        except Exception:  # noqa  # pragma: no cover
            return NotImplemented

        return self._value <= other._value

    def __ge__(self, other: Any) -> bool:
        try:
            other = self.__class__(other)

        except Exception:  # noqa  # pragma: no cover
            return NotImplemented

        return self._value >= other._value


if __name__ == MAIN:  # pragma: no cover
    import doctest

    doctest.testmod()  # test documentation on top of the module
