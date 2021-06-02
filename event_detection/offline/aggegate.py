"""Helper module for getting features accross an entire trajectory."""


from concurrent.futures import ThreadPoolExecutor
from typing import List

import pandas as pd

from event_detection import signal


class SignalAggregator:
    """Using generators computes signals across a trajectory.

    This class can be used to create appropriate data structures for use in
    analysising a whole trajectory with offline methods. See the `__call__`
    method for usage.
    """

    def __init__(self, generators: List[signal.Generator]):
        """Create a `SignalAggregator` object.

        Parameters
        ----------
        generators: list[event_detection.signal.Generator]
            A sequence of signal generators to use for generating the
            multivariate signal of a trajectory.
        """
        self._generators = generators
        self._signals = []

    def __call__(self, trajectory, threads: int = 0):
        """Compute signals from generators across the trajectory.

        These signals are stored internally unto asked for by `to_dataframe`.
        This can be called multiple times, and the stored signals values will be
        appended.

        Parameters
        ----------
        trajectory: a trajectory-like object
            An object when iterated over, yields objects compatible with
            `signal.Generator` objects. Examples include `gsd.hoomd.Trajectory`
            and a Python generator of ``(box, positions)`` tuples.
        threads: int
            The number of threads to use, 0 means serial. This only helps if the
            trajectory like object is a generator-like object that has IO for
            every step.
        """
        if threads >= 1:
            with ThreadPoolExecutor(max_workers=threads) as pool:
                self._signals.extend(
                    pool.map(self._compute_single_frame, trajectory)
                )

        self._signals.extend(
            self._compute_single_frame(system) for system in trajectory
        )

    def _compute_single_frame(self, frame):
        return {
            name: signal
            for generator in self._generators
            for name, signal in generator.generate(frame).items()
        }

    def to_dataframe(self) -> pd.DataFrame:
        """Return the aggregated signals as a pandas DataFrame.

        Returns
        -------
        signals: pandas.DataFrame
            The aggregated signals. The columns are features, and the indices
            correspond to system frames in the order passed to `__call__`.
        """
        return pd.DataFrame(
            {
                col: [frame[col] for frame in self._signals]
                for col in self._signals[0]
            }
        )
