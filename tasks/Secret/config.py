# This Python file uses the following encoding: utf-8
# @author runhey
# github https://github.com/runhey
from datetime import timedelta
from pydantic import BaseModel, Field

from tasks.Component.config_scheduler import Scheduler as BaseScheduler
from tasks.Component.config_base import ConfigBase, TimeDelta, Time
from tasks.Component.GeneralBattle.config_general_battle import GeneralBattleConfig
from tasks.Component.SwitchSoul.switch_soul_config import SwitchSoulConfig

class Scheduler(BaseScheduler):
    success_interval: TimeDelta = Field(default=TimeDelta(days=7), description='success_interval_help')
    failure_interval: TimeDelta = Field(default=TimeDelta(days=7), description='failure_interval_help')
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

class SecretConfig(BaseModel):
    secret_gold_50: bool = Field(title='Secret Gold 50', default=False, description='secret_gold_50_help')
    secret_gold_100: bool = Field(title='Secret Gold 100', default=False, description='secret_gold_100_help')
    layer_10: bool = Field(title='Layer 10', default=False, description='layer_10_help')
    layer_9: bool = Field(title='Layer 9', default=False)


class Secret(ConfigBase):
    scheduler: Scheduler = Field(default_factory=Scheduler)
    secret_config: SecretConfig = Field(default_factory=SecretConfig)
    general_battle: GeneralBattleConfig = Field(default_factory=GeneralBattleConfig)
    switch_soul: SwitchSoulConfig = Field(default_factory=SwitchSoulConfig)




