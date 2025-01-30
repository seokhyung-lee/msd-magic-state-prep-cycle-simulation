# msd-magic-state-prep-cycle-simulation
Python code for simulating the magic state preparation cycle of a cultivation + distillation scheme from arXiv:2409.07707.

Use the function `simulate_msd()` to perform the simulation. By default, it returns the average interval between two consecutive rounds and the average idling time of each magic state after generation.

The docstring of the function is as follows:

```
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
    Average idling time of each magic state after generation.
    If get_all is True, return the idling times of all stages instead.
T_idle_se: float
    Standard error of T_idle. (Only returned if get_all is False.)
```

See [arXiv:2409.07707](https://arxiv.org/abs/2409.07707) for more details. Feel free to reach out to [me](https://seokhyung-lee.github.io) if you have any questions.
