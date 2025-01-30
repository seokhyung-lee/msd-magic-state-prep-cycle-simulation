from math import ceil
from typing import Optional

import numpy as np


class AuxPatch:
    def __init__(self, group: int):
        self.status = None
        self.clock = 0
        self.group = group

    def change_status(self, status: str):
        self.status = status
        self.clock = 0


def simulate_msd(
    dcult: int,
    dm: int,
    Nm: int,
    psucc_cult: float,
    t_cult: int,
    post_selected_growing: bool = True,
    psucc_growing: Optional[float] = None,
    num_stages: int = 1000,
    seed: Optional[int] = None,
    verbose: bool = False,
    get_all: bool = False,
):
    """
    Simulate the magic state preparation cycle of a cultivation + MSD scheme.

    Parameters
    ----------
    dcult: int
        Code distance of each cultivation patch before growing.
    dm: int
        Code distance of each cultivation patch after growing.
    Nm: int
        Number of cultivation patches on each side of the layout.
        The total number of patches is 2 * Nm.
    psucc_cult: float
        Success rate of cultivation.
    t_cult: int
        Number of time steps for each trial of cultivation, excluding the growing step.
    post_selected_growing: bool (default: True)
        Whether to post-select the growing operation based on the logical gap.
    psucc_growing: float or None (default: None)
        Success rate of the growing operation. Should be given if post_selected_growing is True.
    num_stages: int (default: 10_000)
        Number of stages (i.e., the number of consumed pairs of magic states) to simulate.
    seed: int or None (default: None)
        Random seed.
    verbose: bool (default: False)
        Whether to print intermediate results.
    get_all: bool (default: False)
        Whether to return the data of all stages.
    
    Returns
    -------
    T_intv: float
        Average interval between two consecutive rounds.
        If get_all is True, return the intervals of all stages instead.
    T_intv_se: float
        Standard error of T_intv. (Only returned if get_all is False.)
    T_idle: float
        Average idling time of each magic state after it is generated.
        If get_all is True, return the idling times of all stages instead.
    T_idle_se: float
        Standard error of T_idle. (Only returned if get_all is False.)
    """
    np.random.seed(seed)

    T_cult = ceil(t_cult / 8 - 1e-6)
    need_growing = dm > dcult
    Tm = ceil(T_cult / Nm)

    post_selected_growing = post_selected_growing and need_growing
    T_growing = dm if post_selected_growing else 1

    if verbose:
        print("dm =", dm)
        print("dcult =", dcult)
        print("Number of patches =", Nm)
        print(f"Cultivation success probability = {psucc_cult}")
        print(f"Cultivation rounds = {T_cult}")
        print(f"Cultivation interval = {Tm}")
        print(f"Growing success probability = {psucc_growing}")
        print()

    left_patches = [AuxPatch(0) for _ in range(Nm)]
    right_patches = [AuxPatch(1) for _ in range(Nm)]
    all_patches = left_patches + right_patches

    left_patches[0].change_status("cult")
    right_patches[0].change_status("cult")

    idling_patches = [None, None]
    Ts_idle = []
    stage_clock = 0
    cult_clock = [0, 0]
    Ts_intv = []

    def start_cult_or_not(patch):
        group = patch.group
        if cult_clock[group] >= Tm:
            patch.change_status("cult")
            cult_clock[group] = 0
        elif patch.status is not None:
            patch.change_status(None)

    while True:
        stage_clock += 1
        cult_clock[0] += 1
        cult_clock[1] += 1
        for patch in all_patches:
            patch.clock += 1

        consumable = stage_clock > dm or not Ts_intv

        for patch in all_patches:
            if patch.status is None:
                start_cult_or_not(patch)

            elif patch.status == "cult" and patch.clock == T_cult:
                if consumable or need_growing:
                    cult_success = np.random.choice(
                        [True, False], p=(psucc_cult, 1 - psucc_cult)
                    )
                else:
                    cult_success = False

                if cult_success:
                    if need_growing:
                        patch.change_status("growing")
                    else:
                        prev_idling_patch = idling_patches[patch.group]
                        if prev_idling_patch is not None:
                            start_cult_or_not(prev_idling_patch)
                        patch.change_status("idling")
                        idling_patches[patch.group] = patch

                else:
                    start_cult_or_not(patch)

            elif patch.status == "growing" and patch.clock == T_growing:
                if consumable:
                    growing_success = np.random.choice(
                        [True, False], p=(psucc_growing, 1 - psucc_growing)
                    )
                else:
                    growing_success = False

                if growing_success:
                    prev_idling_patch = idling_patches[patch.group]
                    if prev_idling_patch is not None:
                        start_cult_or_not(prev_idling_patch)
                    patch.change_status("idling")
                    idling_patches[patch.group] = patch
                else:
                    start_cult_or_not(patch)

            elif patch.status == "consumed" and patch.clock == dm + 1:
                start_cult_or_not(patch)

        if consumable and all(idling_patches[group] is not None for group in [0, 1]):
            for patch in idling_patches:
                Ts_idle.append(patch.clock)
                patch.change_status("consumed")
            idling_patches[0] = idling_patches[1] = None
            Ts_intv.append(stage_clock)
            stage_clock = 0

        if verbose:
            print(f"Stage clock: {stage_clock}")
            print(f"cult clock: {cult_clock}")
            print(f"Consumable: {consumable}")
            print("Status: ")
            for patch in left_patches:
                print(f"{patch.status} ({patch.clock})", end=" ")
            print()
            for patch in right_patches:
                print(f"{patch.status} ({patch.clock})", end=" ")
            print()
            print()

        if len(Ts_intv) == num_stages:
            break

    if get_all:
        return Ts_intv[1:], Ts_idle
    else:
        Ts_intv = Ts_intv[1:]
        T_intv = np.mean(Ts_intv)
        T_intv_se = np.std(Ts_intv, ddof=1) / np.sqrt(len(Ts_intv))
        T_idle = np.mean(Ts_idle)
        T_idle_se = np.std(Ts_idle, ddof=1) / np.sqrt(len(Ts_idle))

        return T_intv, T_intv_se, T_idle, T_idle_se
