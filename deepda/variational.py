from typing import Callable

import torch
from numpy import ndarray

__all__ = "apply_3DVar", "apply_4DVar"


def apply_3DVar(
    H: Callable,
    B: torch.Tensor,
    R: torch.Tensor,
    xb: torch.Tensor,
    y: torch.Tensor,
    max_iterations: int = 1000,
    learning_rate: float = 1e-3,
    logging: bool = True,
) -> tuple[torch.Tensor, dict[str, list]]:
    """ """
    xb_inner = xb.unsqueeze(0) if xb.ndim == 1 else xb
    y_inner = y.unsqueeze(0) if y.ndim == 1 else y

    new_x0 = torch.nn.Parameter(xb_inner.detach().clone())

    intermediate_results = {
        "J": [],
        "J_grad_norm": [],
        "background_states": [],
    }

    trainer = torch.optim.Adam([new_x0], lr=learning_rate)
    sequence_length = xb_inner.size(0)
    for n in range(max_iterations):
        trainer.zero_grad(set_to_none=True)
        loss = 0
        for i in range(sequence_length):
            one_x0 = new_x0[i].ravel()
            x0_minus_xb = one_x0 - xb_inner[i].ravel()
            y_minus_H_x0 = y_inner[i].ravel() - H(one_x0).ravel()
            loss += (
                x0_minus_xb @ torch.linalg.solve(B, x0_minus_xb)
                + y_minus_H_x0 @ torch.linalg.solve(R, y_minus_H_x0)
            )
        loss.backward(retain_graph=True)
        J, J_grad_norm = loss.item(), torch.norm(new_x0.grad).item()
        if logging:
            print(
                f"Iterations: {n}, J: {J}, Norm of J gradient: {J_grad_norm}"
            )
        trainer.step()
        intermediate_results["J"].append(J)
        intermediate_results["J_grad_norm"].append(J_grad_norm)
        latest_x0 = new_x0.detach().clone().reshape_as(xb)
        intermediate_results["background_states"].append(latest_x0)

    return latest_x0, intermediate_results


def apply_4DVar(
    time_obs: list | tuple | ndarray | torch.Tensor,
    gap: int,
    M: Callable,
    H: Callable,
    B: torch.Tensor,
    R: torch.Tensor,
    xb: torch.Tensor,
    y: torch.Tensor,
    max_iterations: int = 1000,
    learning_rate: float = 1e-3,
    logging: bool = True,
    args: tuple = (None,),
) -> tuple[torch.Tensor, dict[str, list]]:
    """
    """
    new_x0 = torch.nn.Parameter(xb.detach().clone())

    intermediate_results = {
        "Jb": [],
        "Jo": [],
        "J_grad_norm": [],
        "background_states": [],
    }

    def Jb(x0: torch.Tensor, xb: torch.Tensor, y: torch.Tensor):
        x0_minus_xb = x0 - xb
        y_minus_H_x0 = y - H(x0).ravel()
        return (
            x0_minus_xb @ torch.linalg.solve(B, x0_minus_xb)
            + y_minus_H_x0 @ torch.linalg.solve(R, y_minus_H_x0)
        )

    def Jo(xp: torch.Tensor, y: torch.Tensor):
        y_minus_H_xp = y - H(xp).ravel()
        return y_minus_H_xp @ torch.linalg.solve(R, y_minus_H_xp)

    trainer = torch.optim.Adam([new_x0], lr=learning_rate)
    device = xb.device
    for n in range(max_iterations):
        trainer.zero_grad(set_to_none=True)
        current_time = time_obs[0]
        loss_Jb = Jb(new_x0.ravel(), xb.ravel(), y[0].ravel())
        xp = new_x0
        loss_Jo = 0
        for iobs, time_ibos in enumerate(time_obs[1:], start=1):
            time_fw = torch.linspace(
                current_time, time_ibos, gap + 1, device=device
            )
            xf = M(xp, time_fw, *args)
            sequence_length = xf.size(1)
            xp = xf[-sequence_length:]
            for i in range(sequence_length):
                loss_Jo += Jo(xp[i].ravel(), y[iobs, i].ravel())
            current_time = time_ibos
        total_loss = loss_Jb + loss_Jo
        total_loss.backward(retain_graph=True)
        J_grad_norm = torch.norm(new_x0.grad).item()
        if logging:
            print(
                f"Iterations: {n}, J: {total_loss.item()}, "
                f"Norm of J gradient: {J_grad_norm}"
            )
        trainer.step()
        intermediate_results["Jb"].append(loss_Jb.item())
        intermediate_results["Jo"].append(loss_Jo.item())
        intermediate_results["J_grad_norm"].append(J_grad_norm)
        latest_x0 = new_x0.detach().clone()
        intermediate_results["background_states"].append(latest_x0)

    return latest_x0, intermediate_results
