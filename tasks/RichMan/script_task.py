# This Python file uses the following encoding: utf-8
# @author runhey
# github https://github.com/runhey
from time import sleep
from datetime import time, datetime, timedelta

from module.logger import logger
from module.exception import TaskEnd


from tasks.RichMan.assets import RichManAssets
from tasks.RichMan.config import RichMan
from tasks.RichMan.mall.mall import Mall
from tasks.RichMan.guild import Guild
from tasks.RichMan.shrine import Shrine
from tasks.RichMan.thousand_things import ThousandThings


class ScriptTask(Mall, Guild, ThousandThings, Shrine):

    def run(self):
        con: RichMan = self.config.rich_man
        # 千物宝箱
        self.execute_tt(con.thousand_things)
        # 神龛
        self.execute_shrine(con.shrine)
        # 功勋商店
        self.execute_guild(con.guild_store)
        # 商店
        self.execute_mall()

        scheduler = self.config.rich_man.scheduler
        if scheduler.next_run_weekdays and scheduler.next_run_weekdays.strip():
            logger.info('使用周几调度逻辑设置下次运行时间')
            self.custom_next_run_by_weekday(
                task='RichMan',
                weekdays_str=scheduler.next_run_weekdays,
                run_time=scheduler.next_run_time,
                float_time=scheduler.float_time
            )
        else:
            self.set_next_run(task='RichMan', success=True, finish=False)

        raise TaskEnd('RichMan')


if __name__ == '__main__':
    from module.config.config import Config
    from module.device.device import Device
    c = Config('oas1')
    d = Device(c)
    t = ScriptTask(c, d)

    # t.run()
    t.execute_mall()



