# This Python file uses the following encoding: utf-8
# @author runhey
# github https://github.com/runhey
from pydantic import BaseModel, Field
from datetime import time
from tasks.Component.SwitchOnmyoji.config import Onmyoji

from tasks.Component.config_scheduler import Scheduler as BaseScheduler
from tasks.Component.config_base import ConfigBase, Time, TimeDelta
from tasks.Component.GeneralBattle.config_general_battle import GreenMarkType
from enum import Enum
from tasks.Component.SwitchSoul.switch_soul_config import SwitchSoulConfig


class Scheduler(BaseScheduler):
    # 下次运行星期（可多选），支持用逗号、顿号分割，支持数字1-7（周一到周日）或中文"周一"到"周日"
    # 空字符串表示不启用此功能，使用success_interval
    next_run_weekdays: str = Field(
        default='',
        description='下次运行星期，可多选，支持格式：1,2,3 或 周一,周二,周三 或 1、2、3。1=周一, 7=周日；为空表示不启用'
    )
    # 下次运行时间
    next_run_time: Time = Field(
        default=Time(hour=9, minute=0, second=0),
        description='下次运行时间，指定下次运行的具体时间'
    )


class DuelConfig(ConfigBase):
    # 是否切换阴阳师
    switch_enabled: bool = Field(default=True, description='是否切换阴阳师')
    # 切换阴阳师
    switch_onmyoji: Onmyoji = Field(default=Onmyoji.YORIMITSU, description='切换阴阳师')
    # 一键切换斗技御魂
    switch_all_soul: bool = Field(default=False, description='switch_all_soul_help')
    # 限制时间
    limit_time: Time = Field(default=Time(minute=30), description='limit_time_help')
    # 目标分数
    target_score: int = Field(default=2000, description='target_score_help')
    # 刷满荣誉就退出
    honor_full_exit: bool = Field(default=False, description='honor_full_exit_help')
    # 是否开启绿标
    green_enable: bool = Field(default=False, description='green_enable_help')
    # 选哪一个绿标
    green_mark: GreenMarkType = Field(default=GreenMarkType.GREEN_LEFT1, description='green_mark_help')


class DuelCelebConfig(ConfigBase):
    # 是否开启名仕战斗
    celeb_battle: bool = Field(default=False, description='是否开启名仕战斗')
    # 填写第五手式神名称，如果阵容式神被办，第五手就会换式神，退出斗技
    ban_name: str = Field(default='', description='填写第五手式神名称')
    initial_score: int = Field(default=3800, description='设置初始斗技分值默认为8颗星之后每赢一场加100输一场减100')


class Duel(ConfigBase):
    scheduler: Scheduler = Field(default_factory=Scheduler)
    duel_config: DuelConfig = Field(default_factory=DuelConfig)
    duel_celeb_config: DuelCelebConfig = Field(default_factory=DuelCelebConfig)
    switch_soul: SwitchSoulConfig = Field(default_factory=SwitchSoulConfig)
