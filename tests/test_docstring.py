import doctest

from deepda import builder, executor, kalman_filter, parameters, variational


def test_builder_docstrings():
    assert (
        doctest.testmod(builder).failed == 0
    ), "Failed docstring tests in deepda.builder :("


def test_executor_docstrings():
    assert (
        doctest.testmod(executor).failed == 0
    ), "Failed docstring tests in deepda.executor :("


def test_kalman_filter_docstrings():
    assert (
        doctest.testmod(kalman_filter).failed == 0
    ), "Failed docstring tests in deepda.kalman_filter :("


def test_parameters_docstrings():
    assert (
        doctest.testmod(parameters).failed == 0
    ), "Failed docstring tests in deepda.parameters :("


def test_variational_docstrings():
    assert (
        doctest.testmod(variational).failed == 0
    ), "Failed docstring tests in deepda.variational :("
