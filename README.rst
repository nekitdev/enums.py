enums.py
========

*Less sophisticated, less restrictive, more magical and funky!*

.. image:: https://img.shields.io/pypi/l/enums.py.svg
    :target: https://opensource.org/licenses/MIT
    :alt: Project License

.. image:: https://img.shields.io/pypi/v/enums.py.svg
    :target: https://pypi.python.org/pypi/enums.py
    :alt: Library Version

.. image:: https://img.shields.io/pypi/pyversions/enums.py.svg
    :target: https://pypi.python.org/pypi/enums.py
    :alt: Required Python Versions

.. image:: https://img.shields.io/pypi/status/enums.py.svg
    :target: https://github.com/nekitdev/enums.py
    :alt: Development Status

.. image:: https://img.shields.io/pypi/dm/enums.py.svg
    :target: https://pypi.python.org/pypi/enums.py
    :alt: Library Downloads / Month

.. image:: https://app.codacy.com/project/badge/Grade/a961fd80512140f29ddb2a42b8cf5fb1
    :target: https://app.codacy.com/gh/nekitdev/enums.py/dashboard
    :alt: Code Quality

.. image:: https://img.shields.io/coveralls/github/nekitdev/enums.py
    :target: https://coveralls.io/github/nekitdev/enums.py
    :alt: Code Coverage

enums.py is a module that implements enhanced enumerations for Python.

**Incompatible with standard library!**

Below are many examples of using this module.

Prerequisites
-------------

Code snippets and examples are using several common imports and types,
which are mainly omitted for simplicity:

.. code-block:: python3

    from typing import TypeVar  # for different typing purposes

    from enums import (  # library imports used in examples
        # enumerations
        Enum,
        StrEnum,
        IntEnum,
        # flag boundary
        FlagBoundary,
        # boundaries
        CONFORM,
        EJECT,
        KEEP,
        STRICT,
        # flags
        Flag,
        IntFlag,
        # traits
        Trait,
        Order,
        StrFormat,
        # auto item
        auto,
        # unique decorator
        unique,
    )

    T = TypeVar("T")  # general (and generic) type variable

    E = TypeVar("E", bound=Enum)  # enumeration type variable

    F = TypeVar("F", bound=Flag)  # flag type variable
    FB = TypeVar("FB", bound=FlagBoundary)  # flag boundary type variable
    IF = TypeVar("IF", bound=IntFlag)  # integer flag type variable

Creating Enumerations
---------------------

There are many ways to create enumerations.

This can be done in classical way:

.. code-block:: python3

    class Color(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

Like the standard ``enum`` module, ``enums.py`` has ``auto`` class:

.. code-block:: python3

    class Color(Enum):
        RED = auto()
        GREEN = auto()
        BLUE = auto()

Enumerations can be created without explicit ``class`` usage:

.. code-block:: python3

    Color = Enum("Color", ["RED", "GREEN", "BLUE"])

Strings can also be used here:

.. code-block:: python3

    Color = Enum("Color", "RED GREEN BLUE")

You can also use keyword arguments in order to define members:

.. code-block:: python3

    Color = Enum("Color", RED=1, GREEN=2, BLUE=3)

Same with ``auto()``, of course:

.. code-block:: python3

    Color = Enum("Color", RED=auto(), GREEN=auto(), BLUE=auto())

All code snippets above produce ``Color`` in the end, which has 3 members:

- ``<Color.RED: 1>``

- ``<Color.GREEN: 2>``

- ``<Color.BLUE: 3>``

Using Arguments
---------------

Enumeration members that have ``tuple`` values but do not subclass ``tuple``
are interpreted as values passed to ``__init__`` of their class:

.. code-block:: python3

    class Planet(Enum):
        MERCURY = (3.303e+23, 2.4397e6)
        VENUS   = (4.869e+24, 6.0518e6)
        EARTH   = (5.976e+24, 6.37814e6)
        MARS    = (6.421e+23, 3.3972e6)
        JUPITER = (1.9e+27,   7.1492e7)
        SATURN  = (5.688e+26, 6.0268e7)
        URANUS  = (8.686e+25, 2.5559e7)
        NEPTUNE = (1.024e+26, 2.4746e7)

        def __init__(self, mass: float, radius: float) -> None:
            self.mass = mass  # kg
            self.radius = radius  # m

        @property
        def surface_gravity(self) -> float:
            # universal gravitational constant
            G = 6.67300E-11  # m^3 kg^(-1) s^(-2)

            return G * self.mass / (self.radius * self.radius)

    print(Planet.EARTH.value)  # (5.976e+24, 6378140.0)
    print(Planet.EARTH.surface_gravity)  # 9.802652743337129

Iteration
---------

It is possible to iterate over unique enumeration members:

.. code-block:: python3

    Color = Enum("Color", RED=1, GREEN=2, BLUE=3)

    for color in Color:
        print(Color.title)

    # Red
    # Green
    # Blue

Or over all members, including aliases:

.. code-block:: python3

    Color = Enum("Color", RED=1, GREEN=2, BLUE=3, R=1, G=2, B=3)

    for name, color in Color.members.items():
        print(name, color.name)

    # RED RED
    # GREEN GREEN
    # BLUE BLUE
    # R RED
    # G GREEN
    # B BLUE

Member Attributes
-----------------

Enumeration members have several useful attributes:

- *name*, which represents their actual name;

- *value*, which contains their value;

- *title*, which is more human-readable version of their *name*.

.. code-block:: python3

    print(Color.BLUE.name)  # BLUE
    print(Color.BLUE.value)  # 3
    print(Color.BLUE.title)  # Blue

Advanced Access
---------------

Enumeration members can be accessed with case insensitive strings:

.. code-block:: python3

    class Test(Enum):
        TEST = 13

    test = Test.from_name("test")  # <Test.TEST: 13>

**Note that if two members have same case insensitive name version, last in wins!**

**Also keep in mind** ``Enum.from_name`` **will not work with composite flags!**

You can use ``Flag.from_args`` to create composite flag from multiple values or names:

.. code-block:: python3

    Perm = Flag("Perm", "Z X W R", start=0)

    Perm.from_args("r", "w", "x")  # <Perm.X|R|W: 7>

    Perm.from_args(2, 4)  # <Perm.W|R: 6>

There is also ``Enum.from_value``, which tries to use ``Enum.from_name`` if given value is string,
and otherwise (also if failed), it attempts by-value lookup. This function accepts ``default``
argument, such that ``Enum.from_value(default)`` will be called on fail if ``default`` was given.

Example:

.. code-block:: python3

    class Perm(Flag):
        Z, X, W, R = 0, 1, 2, 4

    Perm.from_value(8, default=0)  # <Perm.Z: 0>
    Perm.from_value("broken", "r")  # <Perm.R: 4>

String Enumeration
------------------

``StrEnum`` is a simple type derived from ``Enum``,
which only affects ``enum_generate_next_value``
by making it use the casefolded version of the member name:

.. code-block:: python3

    class Relationship(StrEnum):
        BLOCKED = auto()  # "blocked"
        FOLLOWED = auto()  # "followed"
        FRIEND = auto()  # "friend"

Flags
-----

``Flag`` is a special enumeration that focuses around supporting bit-flags along with operations on them,
such as **OR** ``|``, **AND** ``&``, **XOR** ``^`` and **INVERT** ``~``.

.. code-block:: python3

    class Perm(Flag):
        Z = 0
        X = 1
        W = 2
        R = 4

    # <Perm.W|R: 6>
    RW = Perm.R | Perm.W

    # <Perm.R: 4>
    R = (Perm.R | Perm.W) & Perm.R

    # <Perm.X|W: 3>
    WX = Perm.W ^ Perm.X

    # <Perm.Z: 0>
    Z = Perm.X ^ Perm.X

    # <Perm.X|R: 5>
    RX = ~Perm.W

Flag Boundaries
---------------

Flags can have different *boundaries* (of type ``FlagBoundary``)
that define how unknown bits are handled.

STRICT
~~~~~~

*Strict* boundary is pretty straightforward: an exception is raised on any unknown bits.

.. code-block:: python3

    class Strict(Flag, boundary=STRICT):
        X = auto()  # 0b0001
        Y = auto()  # 0b0010
        Z = auto()  # 0b0100

    strict = Strict(0b1101)  # error!

    # Traceback (most recent call last):
    # <...>
    # ValueError: Invalid value 13 in Strict:
    #     given 0b0 1101
    #   allowed 0b0 0111
    # <...>

CONFORM
~~~~~~~

*Conform* boundary is going to remove any invalid bits, leaving only known ones.

.. code-block:: python3

    class Conform(Flag, boundary=CONFORM):
        X = auto()  # 0b0001
        Y = auto()  # 0b0010
        Z = auto()  # 0b0100

    conform = Conform(0b1101)  # 0b0101 -> <Conform.X|Z: 5>

EJECT
~~~~~

*Eject* boundary is going to remove ``Flag`` membership from out-of-range values.

.. code-block:: python3

    class Eject(Flag, boundary=EJECT):
        X = auto()  # 0b0001
        Y = auto()  # 0b0010
        Z = auto()  # 0b0100

    eject = Eject(0b1101)  # 13

KEEP
~~~~

*Keep* boundary is going to save all invalid bits.

.. code-block:: python3

    class Keep(Flag, boundary=KEEP):
        X = auto()  # 0b0001
        Y = auto()  # 0b0010
        Z = auto()  # 0b0100

    keep = Keep(0b1101)  # <Keep.X|Z|0x8: 13>

Type Restriction and Inheritance
--------------------------------

Enumeration members can be restricted to have values of the same type:

.. code-block:: python3

    class OnlyInt(IntEnum):
        SOME = 1
        OTHER = "2"  # will be casted
        BROKEN = "broken"  # error will be raised on creation

As well as inherit behavior from that type:

.. code-block:: python3

    class Access(IntFlag):
        NONE = 0
        SIMPLE = 1
        MAIN = 2

    FULL = Access.SIMPLE | Access.MAIN

    print(FULL + 10)  # 13

Because ``IntEnum`` and ``IntFlag`` are subclasses of ``int``,
they lose their membership when ``int`` operations are used with them.

Method Resolution Order
-----------------------

``enums.py`` requires the following definiton of new ``Enum`` subclass:

.. code-block:: python3

    EnumName([trait_type, ...] [data_type] enum_type)

For example:

.. code-block:: python3

    class Value(Order, Enum):
        """Generic value that supports ordering."""

    class FloatValue(float, Value):
        """Float value that inherits Value."""

Here, ``FloatValue`` bases are going to be transformed into:

.. code-block:: python3

    (Value, float, Order, Enum)

Which allows us to preserve functions defined in enumerations or flags,
while still having *traits* work nicely with overriding them.

Traits
------

``enums.py`` implements special *traits* (aka *mixins*), which add specific behavior to classes.
Each Trait implements some functionality for enumerations, but does not subclass ``Enum``.
Therefore they are pretty much useless on their own.

StrFormat
~~~~~~~~~

Default ``__format__`` of ``Enum`` will attempt to use ``__format__`` of member data type, if given:

.. code-block:: python3

    class Foo(IntEnum):
        BAR = 42

    print(f"{Foo.BAR}")  # 42

``StrFormat`` overwrites that behavior and uses ``str(member).__format__(format_spec)`` instead:

.. code-block:: python3

    class Foo(StrFormat, IntEnum):
        BAR = 42

    print(f"{Foo.BAR}")  # Foo.BAR

Order
~~~~~

``Order`` trait implements ordering (``==``, ``!=``, ``<``, ``>``, ``<=`` and ``>=``)
for enumeration members. This function will attempt to find member by value.

Example:

.. code-block:: python3

    class Grade(Order, Enum):
        A = 5
        B = 4
        C = 3
        D = 2
        F = 1

    print(Grade.A > Grade.C)  # True
    print(Grade.F <= Grade.D)  # True

    print(Grade.B == 4)  # True
    print(Grade.F >= 0)  # True

Unique Enumerations
-------------------

Enumeration members can have aliases, for example:

.. code-block:: python3

    class Color(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3
        R, G, B = RED, GREEN, BLUE  # aliases

``enums.py`` has ``@unique`` class decorator, that can be used
to check and identify that enumeration does not have aliases.

That is, the following snippet will error:

.. code-block:: python3

    @unique
    class Color(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3
        R, G, B = RED, GREEN, BLUE  # aliases

With the following exception:

.. code-block:: python3

    ValueError: Duplicates found in <enum 'Color'>: R -> RED, G -> GREEN, B -> BLUE.

Class Keyword Arguments
-----------------------

``Enum`` class knows several class keyword arguments:

- **auto_on_missing** - ``bool``
- **ignore** - ``Union[str, Iterable[str]]``
- **start** - ``T``
- **boundary** - ``FB`` (used in ``Flag``)

auto_on_missing
~~~~~~~~~~~~~~~

Boolean flag, if set to ``True`` (default is ``False``), allows to do something like:

.. code-block:: python3

    class Color(Enum, auto_on_missing=True):
        RED  # 1
        GREEN  # 2
        BLUE  # 3

    print(repr(Color.RED))  # <Color.RED: 1>

ignore
~~~~~~

Works same as putting ``enum_ignore`` inside the class (default is ``()`` (empty tuple)):

.. code-block:: python3

    class Time(Enum, ignore=("time_vars", "day")):
        time_vars = vars()

        for day in range(366):
            time_vars[f"day_{day}"] = day

    day = Time.day_365  # <Time.day_365: 365>

start
~~~~~

Just like ``enum_start``, defines a *start* value that should be used for enum members (default is ``None``):

.. code-block:: python3

    class Perm(Flag, start=0):
        Z = auto()  # 0
        X = auto()  # 1
        W = auto()  # 2
        R = auto()  # 4

    print(repr(Perm.R | Perm.W))  # <Perm.R|W: 6>

boundary
~~~~~~~~

Represents boundaries for flags. See :ref:`the following section <Flag Boundaries>`.

Special Names
-------------

``enums.py`` uses special names for managing behavior:

- **enum_missing** - ``classmethod(cls: Type[E], value: T) -> E``

- **enum_ignore** - ``Union[str, Iterable[str]]``

- **enum_generate_next_value** - ``staticmethod(name: str, start: Optional[T], count: int, member_values: List[T]) -> T``

- **enum_auto_on_missing** - ``bool``

- **enum_start** - ``T``

- **_name** - ``Optional[str]``

- **_value** - ``T``

enum_missing
~~~~~~~~~~~~

Class method that should be used in order to process values that are not present in the enumeration:

.. code-block:: python3

    from typing import Union

    class Speed(Enum):
        SLOW = 1
        NORMAL = 2
        FAST = 3

        @classmethod
        def enum_missing(cls, value: Union[float, int]) -> Enum:
            if value < 1:
                return cls.SLOW

            elif value > 3:
                return cls.FAST

            else:
                return cls.NORMAL

    speed = Speed(5)  # <Speed.FAST: 3>

enum_ignore
~~~~~~~~~~~

Iterable of strings or a string that contains names of class members
that should be ignored when creating enumeration members:

.. code-block:: python3

    class Time(IntEnum):
        enum_ignore = ["Time", "second"]  # or "Time, second" or "Time second" or "Time,second"

        Time = vars()

        for second in range(60):
            Time[f"s_{second}"] = second

    print(repr(Time.s_59))  # <Time.s_59: 59>
    print(repr(Time.s_0)) # <Time.s_0: 0>

enum_generate_next_value
~~~~~~~~~~~~~~~~~~~~~~~~

Static method that takes member name, start value (default is None, unless specified otherwise),
count of unique members already created and list of all member values (including aliases).

This method should output value for the new member:

.. code-block:: python3

    from typing import List, Optional

    class CountEnum(Enum):
        @staticmethod
        def enum_generate_next_value(
            name: str, start: Optional[T], count: int, values: List[T]
        ) -> T:
            """Return count of unique members + 1."""
            return count + 1

    class Mark(CountEnum):
        F = auto()  # 1
        D = auto()  # 2
        C = auto()  # 3
        B = auto()  # 4
        A = auto()  # 5

enum_auto_on_missing
~~~~~~~~~~~~~~~~~~~~

Boolean that indicates whether auto() should be used to generate values for missing names:

.. code-block:: python3

    class Color(Enum):
        enum_auto_on_missing = True
        RED, GREEN, BLUE  # 1, 2, 3

enum_start
~~~~~~~~~~

Variable that indicates what value should be passed as ``start`` to ``enum_generate_next_value``.

_name
~~~~~

Private attribute, name of the member. Ideally it should *never* be modified.

_value
~~~~~~

Private attribute, value of the member. Again, it is better *not* to modify it, unless required.

Updating (Mutating) Enumerations
--------------------------------

Unlike in standard ``enum`` module, enumerations can be mutated:

.. code-block:: python3

    class Color(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    ALPHA = Color.add_member("ALPHA", 0)  # <Color.ALPHA: 0>

Or using ``Enum.update()`` for several members:

.. code-block:: python3

    class Color(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    Color.update(ALPHA=0, BROKEN=-1)

Even ``Flag`` flags operate nicely when mutated:

.. code-block:: python3

    class P(Flag):
        R = 4
        W = 2
        X = 1
        Z = 0

    RWX = P.R | P.W | P.X  # <P.R|W|X: 7>

    P.update(RWX=RWX.value)  # RWX is now <P.RWX: 7>

Installing
----------

**Python 3.6 or higher is required**

To install the library, you can just run the following command:

.. code:: sh

    # Linux / OS X
    python3 -m pip install --upgrade enums.py

    # Windows
    py -3 -m pip install --upgrade enums.py

In order to install the library from source, you can do the following:

.. code:: sh

    $ git clone https://github.com/nekitdev/enums.py
    $ cd enums.py
    $ python -m pip install --upgrade .

Testing
-------

In order to test the library, you need to have *coverage*, *flake8* and *pytest* packages.

They can be installed like so:

.. code:: sh

    $ cd enums.py
    $ python -m pip install .[test]

Then linting and running tests with coverage:

.. code:: sh

    # lint the source
    $ flake8
    # run tests and record coverage
    $ coverage run -m pytest test_enums.py

Changlelog
----------

- **0.1.0** - Initial release, almost full support of standard enum module;

- **0.1.1** - Make bitwise operations in Flag smarter;

- **0.1.2** - Add IntEnum and IntFlag;

- **0.1.3** - Add Traits and fix bugs;

- **0.1.4** - Add nice dir() implementation for both Enum class and members;

- **0.1.5** - Fix small bugs;

- **0.2.0** - Fix IntEnum to be almost even with standard library, fix bugs and add tests.

- **0.3.0** - Fix MRO resolution and add small enhancements.

- **0.3.1** - Fix small typos and other non-code-related things.

- **0.4.0** - Typing fixes and usage of ``ENUM_DEFINED`` flag instead of setting to ``None`` and checks.

- **0.5.0** - Preserve important methods, such as ``__format__``, ``__repr__``, ``__str__`` and others.

- **0.6.0** - Overall rewrite, implement flag boundaries and improve flags.

Authors
-------

This project is mainly developed by `nekitdev <https://github.com/nekitdev>`_.
