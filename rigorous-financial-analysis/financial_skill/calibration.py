"""Strict point-in-time forecast calibration.
Use publication dates, not simply fiscal period labels, to avoid look-ahead.
"""
from dataclasses import dataclass
from datetime import date
from math import isfinite

from .domain import finite


@dataclass(frozen=True)
class ForecastRecord:
    forecast_asof: date
    target_period_end: date
    actual_published_on: date
    bear: float
    base: float
    bull: float
    realized: float

    def __post_init__(self) -> None:
        if not self.forecast_asof < self.actual_published_on:
            raise ValueError('Actual became available before forecast: lookahead risk')
        if not self.forecast_asof < self.target_period_end <= self.actual_published_on:
            raise ValueError('Period dates inconsistent')
        for n in ('bear','base','bull','realized'):
            finite(getattr(self, n), n)
        if self.bear > self.base or self.base > self.bull:
            raise ValueError('Scenario bounds must be ordered bear <= base <= bull')


@dataclass(frozen=True)
class CalibrationMetrics:
    samples: int
    mae: float
    signed_bias: float
    scenario_coverage: float
    wape: float | None


def calibrate(records: tuple[ForecastRecord, ...]) -> CalibrationMetrics:
    if not records:
        raise ValueError('Need at least one out-of-sample forecast')
    errors = [r.base - r.realized for r in records]
    scale = sum(abs(r.realized) for r in records)
    return CalibrationMetrics(len(records), sum(abs(e) for e in errors)/len(errors),
                              sum(errors)/len(errors),
                              sum(r.bear <= r.realized <= r.bull for r in records)/len(records),
                              sum(abs(e) for e in errors)/scale if scale else None)
