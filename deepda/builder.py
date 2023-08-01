from dataclasses import asdict
from typing import Any, Callable

import torch
from numpy import ndarray
from torch._C import _LinAlgError as LinAlgError

from . import Algorithms, Device
from .executor import Executor, Parameters, _GenericTensor

__all__ = "Parameters", "CaseBuilder"


class CaseBuilder:
    __slots__ = "case_name", "__parameters", "__executor"

    def __init__(
        self,
        case_name: str = "",
        parameters: dict[str, Any] | Parameters = None,
    ) -> None:
        self.case_name = case_name
        self.__parameters = Parameters()
        if parameters is not None:
            self.set_all_parameters(parameters)
        self.__executor = Executor()

    def set_all_parameters(
        self, parameters: dict[str, Any] | Parameters
    ) -> "CaseBuilder":
        if isinstance(parameters, Parameters):
            parameters = asdict(parameters)
        checked_builder = CaseBuilder()
        for param_name, param_value in parameters.items():
            checked_builder.set_parameter(param_name, param_value)
        self.__parameters = checked_builder.__parameters
        return self

    def set_parameter(self, name: str, value: Any) -> "CaseBuilder":
        if not hasattr(self.__parameters, name):
            raise AttributeError(
                f"Parameter '{name}' does not exist in Parameters."
            )
        setter_method = getattr(self, f"set_{name}", None)
        if setter_method is None:
            raise AttributeError(
                f"Setter method for parameter '{name}' not found."
            )
        return setter_method(value)

    def set_algorithm(self, algorithm: Algorithms) -> "CaseBuilder":
        if algorithm in Algorithms:
            self.__parameters.algorithm = algorithm
        return self

    def set_device(self, device: Device) -> "CaseBuilder":
        if device in Device:
            self.__parameters.device = device
        return self

    def set_forward_model(self, forward_model: Callable) -> "CaseBuilder":
        if not isinstance(forward_model, Callable):
            raise TypeError(
                "forward_model must be a callable type, "
                f"given {type(forward_model)=}"
            )
        self.__parameters.forward_model = forward_model
        return self

    def set_observation_model(
        self, observation_model: torch.Tensor | Callable
    ) -> "CaseBuilder":
        if not isinstance(observation_model, (torch.Tensor | Callable)):
            raise TypeError(
                "observation_model must be an instance of Tensor "
                f"or a callable type, given {type(observation_model)=}"
            )
        self.__parameters.observation_model = observation_model
        return self

    @staticmethod
    def check_covariance_matrix(cov_matrix: torch.Tensor) -> None:
        if cov_matrix.ndim != 2 or (
            size := cov_matrix.size(0)
        ) != cov_matrix.size(1):
            raise LinAlgError(
                "Covariance matrix should be a 2D square matrix."
            )
        if not torch.allclose(cov_matrix, cov_matrix.T):
            raise LinAlgError(
                "Covariance matrix should be a symmetric matrix."
            )
        if torch.linalg.matrix_rank(cov_matrix) != size:
            raise LinAlgError("The input matrix is a singular matrix.")

    def set_background_covariance_matrix(
        self, background_covariance_matrix: torch.Tensor
    ) -> "CaseBuilder":
        if not isinstance(background_covariance_matrix, torch.Tensor):
            raise TypeError(
                "background_covariance_matrix must be an instance of Tensor, "
                f"given {type(background_covariance_matrix)=}"
            )
        self.check_covariance_matrix(background_covariance_matrix)
        self.__parameters.background_covariance_matrix = (
            background_covariance_matrix
        )
        return self

    def set_observation_covariance_matrix(
        self, observation_covariance_matrix: torch.Tensor
    ) -> "CaseBuilder":
        if not isinstance(observation_covariance_matrix, torch.Tensor):
            raise TypeError(
                "observation_covariance_matrix "
                "must be an instance of Tensor, "
                f"given {type(observation_covariance_matrix)=}"
            )
        self.check_covariance_matrix(observation_covariance_matrix)
        self.__parameters.observation_covariance_matrix = (
            observation_covariance_matrix
        )
        return self

    def set_background_state(
        self, background_state: torch.Tensor
    ) -> "CaseBuilder":
        if not isinstance(background_state, torch.Tensor):
            raise TypeError(
                "background_state must be an instance of Tensor, "
                f"given {type(background_state)=}"
            )
        self.__parameters.background_state = background_state
        return self

    def set_observations(self, observations: torch.Tensor) -> "CaseBuilder":
        if not isinstance(observations, torch.Tensor):
            raise TypeError(
                f"observations must be an instance of Tensor, "
                f"given {type(observations)=}"
            )
        self.__parameters.observations = observations
        return self

    def set_observation_time_steps(
        self, observation_time_steps: _GenericTensor
    ) -> "CaseBuilder":
        if not isinstance(
            observation_time_steps, (list, tuple, ndarray, torch.Tensor)
        ):
            raise TypeError(
                "observation_time_steps must be a "
                f"{_GenericTensor.__bound__} type, "
                f"given {type(observation_time_steps)=}"
            )
        self.__parameters.observation_time_steps = observation_time_steps
        return self

    def set_gap(self, gap: int) -> "CaseBuilder":
        if not isinstance(gap, int):
            raise TypeError(f"gap must be an integer, given {type(gap)=}")
        self.__parameters.gap = gap
        return self

    def set_num_steps(self, num_steps: int) -> "CaseBuilder":
        if not isinstance(num_steps, int):
            raise TypeError(
                f"num_steps must be an integer, given {type(num_steps)=}"
            )
        self.__parameters.num_steps = num_steps
        return self

    def set_num_ensembles(self, num_ensembles: int) -> "CaseBuilder":
        if not isinstance(num_ensembles, int):
            raise TypeError(
                "num_ensembles must be an integer, "
                f"given {type(num_ensembles)=}"
            )
        self.__parameters.num_ensembles = num_ensembles
        return self

    def set_start_time(self, start_time: int | float) -> "CaseBuilder":
        if not isinstance(start_time, (int, float)):
            raise TypeError(
                "start_time must be an integer or a floating point number, "
                f"given {type(start_time)=}"
            )
        self.__parameters.start_time = start_time
        return self

    def set_args(self, args: tuple) -> "CaseBuilder":
        if not isinstance(args, tuple):
            raise TypeError(f"args must be a tuple, given {type(args)=}")
        self.__parameters.args = args
        return self

    def set_max_iterations(self, max_iterations: int) -> "CaseBuilder":
        if not isinstance(max_iterations, int):
            raise TypeError(
                "max_iterations must be an integer, "
                f"given {type(max_iterations)=}"
            )
        self.__parameters.max_iterations = max_iterations
        return self

    def set_learning_rate(self, learning_rate: int | float) -> "CaseBuilder":
        if not isinstance(learning_rate, (int, float)):
            raise TypeError(
                "learning_rate must be an integer or "
                f"a floating point number, given {type(learning_rate)=}"
            )
        self.__parameters.learning_rate = learning_rate
        return self

    def set_logging(self, logging: bool) -> "CaseBuilder":
        if not isinstance(logging, bool):
            raise TypeError(f"logging must be a bool, given {type(logging)=}")
        self.__parameters.logging = logging
        return self

    def execute(self) -> dict[str, torch.Tensor]:
        return self.__executor.set_input_parameters(self.__parameters).run()

    def get_results_dict(self) -> dict[str, torch.Tensor]:
        return self.__executor.get_results_dict()

    def get_result(self, name: str) -> torch.Tensor:
        return self.__executor.get_result(name)

    def get_parameters_dict(self) -> dict[str, Any]:
        return asdict(self.__parameters)

    def __repr__(self) -> str:
        params_dict = self.get_parameters_dict()
        str_list = [
            f"Parameters for Case: {self.case_name}",
            "--------------------------------------",
        ]
        str_list.extend(
            f"{param_name}:\n{param_value}\n"
            for param_name, param_value in params_dict.items()
        )
        return "\n".join(str_list)