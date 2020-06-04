__author__ = ["Markus Löning"]
__all__ = [
    "check_X",
    "check_y",
    "check_X_y",
]

import numpy as np
import pandas as pd
from sklearn.utils.validation import check_consistent_length
from sktime.utils.data_container import is_nested_dataframe
from sktime.utils.data_container import nested_to_3d_numpy


def check_X(X, return_numpy=False, enforce_univariate=False,
            enforce_min_instances=1, enforce_min_columns=1):
    """Validate input data.

    Parameters
    ----------
    X : pd.DataFrame or np.array
        Input data
    return_numpy : bool, optional (default=False)
        Whether or not to convert and return X as a 3-dimensional
        numpy array.
    enforce_univariate : bool, optional (default=False)
        Enforce that X is univariate.
    enforce_min_instances : int, optional (default=1)
        Enforce minimum number of instances.
    enforce_min_columns : int, optional (default=1)
        Enforce minimum number of columns (or time-series variables).

    Returns
    -------
    X : pd.DataFrame or np.array
        Checked and possibly converted input data

    Raises
    ------
    ValueError
        If X is invalid input data
    """
    # check input type
    allowed_input_types = (pd.DataFrame, np.ndarray)
    if not isinstance(X, allowed_input_types):
        raise ValueError(f"X must be a pd.DataFrame or a np.array, "
                         f"but found: {(type(X))}")

    # check np.array
    # check first if we have the right number of dimensions, otherwise we
    # may not be able to get the shape of the second dimension below
    if isinstance(X, np.ndarray):
        if not X.ndim == 3:
            raise ValueError(
                f"If passed as a np.array, X must be a 3-dimensional "
                f"array, but found shape: {X.shape}")

    n_instances, n_columns = X.shape[:2]

    # check number of columns
    # enforce minimum number of columns
    if n_columns < enforce_min_columns:
        raise ValueError(
            f"X must contain at least: {enforce_min_columns} columns,"
            f"but found only: {n_columns}.")

    # enforce univariate data
    if enforce_univariate:
        if n_columns > 1:
            raise ValueError(
                f"This method requires X to be univariate "
                f"with X.shape[1]== 1, but found: "
                f"X.shape[1] == {X.shape[1]}.")

    # check number of instances
    # enforce minimum number of instances
    if enforce_min_instances > 0:
        _enforce_min_instances(X, min_instances=enforce_min_instances)

    # check pd.DataFrame
    if isinstance(X, pd.DataFrame):
        if not is_nested_dataframe(X):
            raise ValueError(
                f"If passed as a pd.DataFrame, X must be a nested "
                f"pd.DataFrame, with pd.Series or np.arrays inside cells."
            )
        # convert pd.DataFrame
        if return_numpy:
            X = nested_to_3d_numpy(X)

    return X


def check_y(y, enforce_min_instances=1, return_numpy=False):
    """Validate input data.

    Parameters
    ----------
    y : pd.Series or np.array
    enforce_min_instances : int, optional (default=1)
        Enforce minimum number of instances.


    Returns
    -------
    y : pd.Series or np.array

    Raises
    ------
    ValueError
        If y is an invalid input
    """
    if not isinstance(y, (pd.Series, np.ndarray)):
        raise ValueError(
            f"y must be either a pd.Series or a np.ndarray, "
            f"but found type: {type(y)}")

    if enforce_min_instances > 0:
        _enforce_min_instances(y, min_instances=enforce_min_instances)

    if return_numpy and isinstance(y, pd.Series):
        y = y.to_numpy()

    return y


def check_X_y(X, y, enforce_univariate=False, enforce_min_instances=1,
              enforce_min_columns=1):
    """Validate input data.

    Parameters
    ----------
    X : pd.DataFrame
    y : pd.Series or np.array
    enforce_univariate : bool, optional (default=False)
        Enforce that X is univariate.
    enforce_min_instances : int, optional (default=1)
        Enforce minimum number of instances.
    enforce_min_columns : int, optional (default=1)
        Enforce minimum number of columns (or time-series variables).

    Returns
    -------
    X : pd.DataFrame or np.array
    y : pd.Series

    Raises
    ------
    ValueError
        If y or X is invalid input data
    """
    # Since we check for consistent lengths, it's enough to
    # check only X for the minimum number of instances
    X = check_X(X, enforce_univariate=enforce_univariate,
                enforce_min_columns=enforce_min_columns,
                enforce_min_instances=enforce_min_instances)
    y = check_y(y)
    check_consistent_length(X, y)
    return X, y


def _enforce_min_instances(x, min_instances=1):
    if hasattr(x, "shape"):
        n_instances = x.shape[0]
    else:
        x = np.asarray(x)
        n_instances = x.shape[0]

    if min_instances > 0:
        if n_instances < min_instances:
            raise ValueError(
                f"Found array with: {n_instances} instance(s) "
                f"but a minimum of: {min_instances} is required.")
