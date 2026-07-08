"""Meter polling read plan construction."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import RegisterSpec


@dataclass(frozen=True, slots=True)
class ReadPlanOptions:
    enable_advanced: bool = False
    enable_diagnostic: bool = False
    enable_two_way: bool = False
    enable_config: bool = False
    normal_divisor: int = 3
    slow_divisor: int = 30


@dataclass(slots=True)
class RegisterBatch:
    start: int
    length: int
    function: str
    specs: list[RegisterSpec]


@dataclass(slots=True)
class ReadPlan:
    batches: list[RegisterBatch]
    next_cycle: int


def build_read_plan(specs: Iterable[RegisterSpec], options: ReadPlanOptions, cycle: int) -> ReadPlan:
    included_specs = [spec for spec in specs if should_include_spec(spec, options)]
    specs_to_read = [spec for spec in included_specs if spec.tier == "fast"]
    if cycle % options.normal_divisor == 0:
        specs_to_read.extend(spec for spec in included_specs if spec.tier == "normal")
    if cycle % options.slow_divisor == 0:
        specs_to_read.extend(spec for spec in included_specs if spec.tier == "slow")

    next_cycle = (cycle + 1) % (options.normal_divisor * options.slow_divisor)
    return ReadPlan(batches=build_register_batches(specs_to_read), next_cycle=next_cycle)


def should_include_spec(spec: RegisterSpec, options: ReadPlanOptions) -> bool:
    if spec.category == "advanced" and not options.enable_advanced:
        return False
    if spec.category == "diagnostic" and not options.enable_diagnostic:
        return False
    if spec.category == "config" and not options.enable_config:
        return False
    if spec.category == "two-way" and not options.enable_two_way:
        return False
    return True


def build_register_batches(specs: Iterable[RegisterSpec]) -> list[RegisterBatch]:
    ordered = sorted(specs, key=lambda spec: (spec.function, spec.address))
    batches: list[RegisterBatch] = []
    current: RegisterBatch | None = None
    for spec in ordered:
        if current is None:
            current = RegisterBatch(start=spec.address, length=spec.length, function=spec.function, specs=[spec])
            continue
        end = current.start + current.length
        gap = spec.address - end
        if spec.function == current.function and gap <= 0:
            current.length = (spec.address + spec.length) - current.start
            current.specs.append(spec)
        else:
            batches.append(current)
            current = RegisterBatch(start=spec.address, length=spec.length, function=spec.function, specs=[spec])
    if current:
        batches.append(current)
    return batches
