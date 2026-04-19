"""Mode definitions for agent (BUILD vs PLAN)"""

from enum import StrEnum


class PlanMode(StrEnum):
    BUILD = "build"  # 可以执行写操作
    PLAN = "plan"  # 只读、分析计划


__all__ = ["PlanMode"]
