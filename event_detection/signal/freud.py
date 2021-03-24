"""Interface from freud to event_detection."""

from typing import Dict, Optional, Tuple, Union

try:
    import freud
except ImportError:

    class _ModuleError:
        def __init__(self, module):
            self.module = module

        def __getattribute__(self, attr):
            raise RuntimeError(
                f"This feature is not available as the module "
                f"{object.__getattribute__(self, 'module')} is not available."
            )

    freud = _ModuleError("freud")

import numpy as np

from .generate import Generator
from .reduce import ArrayReducer
from .util import _state_to_freud_system


class FreudDescriptor(Generator):
    """Wraps `freud` compute objects for use in generating signals.

    When a returned quantity returned by an instances internal compute is an
    array this is assumed to be of a consistent size. That is if it returns an
    array of size 100, then it will always be of size 100.
    """

    def __init__(
        self,
        compute,
        attrs: Union[str, Tuple[str, ...]],
        reducers: Optional[Tuple[ArrayReducer]] = None,
        *args,
        **kwargs,
    ):
        r"""Create a `FreudDescriptor` object.

        Parameters
        ----------
        compute: freud.util._Compute
            The freud compute object to generate the signals from.
        attrs: str or Dict[str, str]
            A mapping of attribute names to desired signal names. If the value
            in a entry is ``None`` the key value is used.
        reducers: Sequence[signal.ArrayReducer]
            A sequence of `signal.ArrayReducer` objects to use for creating
            features from distributions or array quantities. All reducers are
            applied to all ``attrs``. If any attributes specified are arrays,
            and this list is empty then an error is produced.
        \*args:
            list of positional arguments to pass to ``compute.compute``.
        \*\*kwargs:
            mapping of keyword arguments to pass to ``compute.compute``.
        """
        self._compute = compute
        self._attrs = {attrs: attrs} if isinstance(attrs, str) else attrs
        self._reducers = reducers
        self._args = args
        self._kwargs = kwargs

    def generate(self, state) -> Dict[str, float]:
        """Generate the specified signals from the internal freud compute.

        state: state-like object
            An object with a `hoomd.Snapshot` like API. Examples include
            `gsd.hoomd.Frame` and `hoomd.Snapshot`. This is used to pass to
            generator to return the corresponding signals.
        """
        system = _state_to_freud_system(state)
        self._compute.compute(system, *self._args, **self._kwargs)
        signal_dict = {}
        for reducer in self._reducers:
            reducer.update(state)
        for attr, name in self._attrs.items():
            if name is None:
                name = attr
            data = getattr(self._compute, attr)
            if isinstance(data, np.ndarray):
                if self._reducers is None:
                    raise RuntimeError(
                        f"Cannot process array quantity "
                        f"{attr} without a filter."
                    )
                signal_dict.update(
                    {
                        "-".join((key, name)): value
                        for reducer in self._reducers
                        for key, value in reducer(data).items()
                    }
                )
            else:
                signal_dict[attr] = data
        return signal_dict
