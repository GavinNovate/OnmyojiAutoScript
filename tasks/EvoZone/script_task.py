# This Python file uses the following encoding: utf-8
# @author runhey
# github https://github.com/runhey
from time import sleep
from datetime import time, datetime, timedelta
import random

from tasks.Component.GeneralBattle.general_battle import GeneralBattle
from tasks.Component.GeneralInvite.general_invite import GeneralInvite
from tasks.Component.GeneralBuff.general_buff import GeneralBuff
from tasks.Component.GeneralRoom.general_room import GeneralRoom
from tasks.Component.SwitchSoul.switch_soul import SwitchSoul
from tasks.GameUi.game_ui import GameUi
from tasks.GameUi.page import page_main, page_awake_zones, page_shikigami_records
from tasks.EvoZone.assets import EvoZoneAssets
from tasks.EvoZone.config import EvoZone, UserStatus, KirinType
from module.logger import logger
from module.exception import TaskEnd
from tasks.GameUi.page import page_friends


class ScriptTask(GeneralBattle, GeneralInvite, GeneralBuff, GeneralRoom, GameUi, EvoZoneAssets, SwitchSoul):

    def run(self) -> bool:

        limit_count = self.config.evo_zone.evo_zone_config.limit_count
        limit_time = self.config.evo_zone.evo_zone_config.limit_time
        self.current_count = 0
        self.limit_count: int = limit_count
        self.limit_time: timedelta = timedelta(hours=limit_time.hour, minutes=limit_time.minute,
                                               seconds=limit_time.second)
        con = self.config.evo_zone

        if con.switch_soul_config.enable:
            self.ui_get_current_page()
            self.ui_goto(page_shikigami_records)
            self.run_switch_soul(con.switch_soul_config.switch_group_team)
        if con.switch_soul_config.enable_switch_by_name:
            self.ui_get_current_page()
            self.ui_goto(page_shikigami_records)
            self.run_switch_soul_by_name(con.switch_soul_config.group_name, con.switch_soul_config.team_name)

        self.ui_get_current_page()
        self.ui_goto(page_main)

        # 检查协战次数限制（在进入主页之后，模拟器已启动）
        if con.evo_zone_config.limit_by_friend_battle:
            logger.info('已启用协战次数限制')
            friend_count, check_success = self.check_friend_battle_count()
            if friend_count == 0:
                if check_success:
                    # 真实的协战次数为0，标记为成功并跳过
                    logger.info('当前协战次数为0，跳过任务')
                    self.set_next_run('EvoZone', finish=True, success=True)
                    raise TaskEnd
                else:
                    # 协战次数识别失败，标记为失败
                    logger.warning('协战次数识别失败，任务执行失败')
                    self.set_next_run('EvoZone', finish=True, success=False)
                    raise TaskEnd
            else:
                # 将协战次数作为运行次数限制
                self.limit_count = min(self.limit_count, friend_count)
                logger.info('将运行次数限制调整为: %d', self.limit_count)
        config: EvoZone = self.config.evo_zone
        if config.evo_zone_config.soul_buff_enable:
            self.open_buff()
            self.awake(is_open=True)
            self.close_buff()

        success = True
        match config.evo_zone_config.user_status:
            case UserStatus.LEADER:
                success = self.run_leader()
            case UserStatus.MEMBER:
                success = self.run_member()
            case UserStatus.ALONE:
                self.run_alone()
            case UserStatus.WILD:
                self.run_wild()
            case _:
                logger.error('Unknown user status')

        # 记得关掉
        if config.evo_zone_config.soul_buff_enable:
            self.open_buff()
            self.awake(is_open=False)
            self.close_buff()
        # 下一次运行时间
        if success:
            self.set_next_run('EvoZone', finish=True, success=True)
        else:
            self.set_next_run('EvoZone', finish=False, success=False)

        raise TaskEnd

    def evozone_enter(self) -> bool:
        logger.info('Enter evozone')
        # 如果启用随机麒麟类型，则在火、风、水、雷中随机选择
        if self.config.evo_zone.evo_zone_config.random_kirin_type:
            kirin_types = [KirinType.FIREKIRIN, KirinType.WINDKIRIN, KirinType.WATERKIRIN, KirinType.LIGHTNINGKIRIN]
            selected_kirin_type = random.choice(kirin_types)
            logger.info('随机选择的麒麟类型: %s', selected_kirin_type.value)
        else:
            selected_kirin_type = self.config.evo_zone.evo_zone_config.kirin_type
            logger.info('使用的麒麟类型: %s', selected_kirin_type.value)

        kirintype = self.I_LIGHTNING_KIRIN
        match selected_kirin_type:
            case KirinType.FIREKIRIN:
                kirintype = self.I_FIRE_KIRIN
            case KirinType.WINDKIRIN:
                kirintype = self.I_WIND_KIRIN
            case KirinType.WATERKIRIN:
                kirintype = self.I_WATER_KIRIN
            case KirinType.LIGHTNINGKIRIN:
                kirintype = self.I_LIGHTNING_KIRIN
        while True:
            self.screenshot()
            if self.appear(self.I_FORM_TEAM):
                return True
            if self.appear_then_click(kirintype, interval=1):
                continue

    def check_layer(self, layer: str) -> bool:
        """
        检查挑战的层数, 并选中挑战的层
        :return:
        """
        pos = self.list_find(self.L_LAYER_LIST, layer)
        if pos:
            self.device.click(x=pos[0], y=pos[1])
            return True

    def check_lock(self, lock: bool = True) -> bool:
        """
        检查是否锁定阵容, 要求在觉醒界面
        :param lock:
        :return:
        """
        logger.info('Check lock: %s', lock)
        if lock:
            while 1:
                self.screenshot()
                if self.appear(self.I_EVOZONE_LOCK):
                    return True
                if self.appear_then_click(self.I_EVOZONE_UNLOCK, interval=1):
                    continue
        else:
            while 1:
                self.screenshot()
                if self.appear(self.I_EVOZONE_UNLOCK):
                    return True
                if self.appear_then_click(self.I_EVOZONE_LOCK, interval=1):
                    continue

    def run_leader(self):
        logger.info('Start run leader')
        self.ui_get_current_page()
        # self.ui_goto(page_soul_zones)
        self.ui_goto(page_awake_zones)
        self.evozone_enter()
        layer = self.config.evo_zone.evo_zone_config.layer
        logger.info("test0")
        self.check_layer(layer)
        logger.info("test1")
        self.check_lock(self.config.evo_zone.general_battle_config.lock_team_enable)
        logger.info("test2")
        # 创建队伍
        logger.info('Create team')
        while 1:
            self.screenshot()
            if self.appear(self.I_CHECK_TEAM):
                break
            if self.appear_then_click(self.I_FORM_TEAM, interval=1):
                continue
        # 创建房间
        self.create_room()
        self.ensure_private()
        self.create_ensure()

        # 邀请队友
        success = True
        is_first = True
        # 这个时候我已经进入房间了哦
        while 1:
            self.screenshot()
            # 无论胜利与否, 都会出现是否邀请一次队友
            # 区别在于，失败的话不会出现那个勾选默认邀请的框
            if self.check_and_invite(self.config.evo_zone.invite_config.default_invite):
                continue

            # 检查猫咪奖励
            if self.appear_then_click(self.I_PET_PRESENT, action=self.C_WIN_3, interval=1):
                continue

            if self.current_count >= self.limit_count:
                if self.is_in_room():
                    logger.info('EvoZone count limit out')
                    break

            if datetime.now() - self.start_time >= self.limit_time:
                if self.is_in_room():
                    logger.info('EvoZone time limit out')
                    break

            # 如果没有进入房间那就不需要后面的邀请
            if not self.is_in_room():
                # 如果在探索界面或者是出现在组队界面， 那就是可能房间死了
                # 要结束任务
                sleep(0.5)
                if self.appear(self.I_MATCHING) or self.appear(self.I_CHECK_EXPLORATION):
                    sleep(0.5)
                    if self.appear(self.I_MATCHING) or self.appear(self.I_CHECK_EXPLORATION):
                        logger.warning('EvoZone task failed')
                        success = False
                        break
                continue

            # 点击挑战
            if not is_first:
                if self.run_invite(config=self.config.evo_zone.invite_config):
                    self.run_general_battle(config=self.config.evo_zone.general_battle_config)
                else:
                    # 邀请失败，退出任务
                    logger.warning('Invite failed and exit this EvoZone task')
                    success = False
                    break

            # 第一次会邀请队友
            if is_first:
                if not self.run_invite(config=self.config.evo_zone.invite_config, is_first=True):
                    logger.warning('Invite failed and exit this evozone task')
                    success = False
                    break
                else:
                    is_first = False
                    self.run_general_battle(config=self.config.evo_zone.general_battle_config)

        # 当结束或者是失败退出循环的时候只有两个UI的可能，在房间或者是在组队界面
        # 如果在房间就退出
        if self.exit_room():
            pass
        # 如果在组队界面就退出
        if self.exit_team():
            pass

        self.ui_get_current_page()
        self.ui_goto(page_main)

        if not success:
            return False
        return True

    def run_member(self):
        logger.info('Start run member')
        self.ui_get_current_page()
        # self.ui_goto(page_soul_zones)
        # self.evozone_enter()
        # self.check_lock(self.config.evo_zone.general_battle_config.lock_team_enable)

        # 进入战斗流程
        self.device.stuck_record_add('BATTLE_STATUS_S')
        while 1:
            self.screenshot()

            # 检查猫咪奖励
            if self.appear_then_click(self.I_PET_PRESENT, action=self.C_WIN_3, interval=1):
                continue

            if self.current_count >= self.limit_count:
                logger.info('EvoZone count limit out')
                break
            if datetime.now() - self.start_time >= self.limit_time:
                logger.info('EvoZone time limit out')
                break

            if self.check_then_accept():
                continue

            if self.is_in_room():
                self.device.stuck_record_clear()
                if self.wait_battle(wait_time=self.config.evo_zone.invite_config.wait_time):
                    self.run_general_battle(config=self.config.evo_zone.general_battle_config)
                else:
                    break
            # 队长秒开的时候，检测是否进入到战斗中
            elif self.check_take_over_battle(False, config=self.config.evo_zone.general_battle_config):
                continue

        while 1:
            # 有一种情况是本来要退出的，但是队长邀请了进入的战斗的加载界面
            if self.appear(self.I_GI_HOME) or self.appear(self.I_GI_EXPLORE):
                break
            # 如果可能在房间就退出
            if self.exit_room():
                pass
            # 如果还在战斗中，就退出战斗
            if self.exit_battle():
                pass

        self.ui_get_current_page()
        self.ui_goto(page_main)
        return True

    def run_alone(self):
        logger.info('Start run alone')
        self.ui_get_current_page()
        self.ui_goto(page_awake_zones)
        self.evozone_enter()
        layer = self.config.evo_zone.evo_zone_config.layer
        self.check_layer(layer)
        self.check_lock(self.config.evo_zone.general_battle_config.lock_team_enable)

        def is_in_evozone(screenshot=False) -> bool:
            if screenshot:
                self.screenshot()
            return self.appear(self.I_EVOZONE_FIRE)

        while 1:
            self.screenshot()

            # 检查猫咪奖励
            if self.appear_then_click(self.I_PET_PRESENT, action=self.C_WIN_3, interval=1):
                continue

            if not is_in_evozone():
                continue

            if self.current_count >= self.limit_count:
                logger.info('EvoZone count limit out')
                break
            if datetime.now() - self.start_time >= self.limit_time:
                logger.info('EvoZone time limit out')
                break

            # 点击挑战
            while 1:
                self.screenshot()
                if self.appear_then_click(self.I_EVOZONE_FIRE, interval=1):
                    pass

                if not self.appear(self.I_EVOZONE_FIRE):
                    self.run_general_battle(config=self.config.evo_zone.general_battle_config)
                    break

        # 回去
        while 1:
            self.screenshot()
            if not self.appear(self.I_FORM_TEAM):
                break
            if self.appear_then_click(self.I_BACK_Y, interval=1):
                continue

        self.ui_current = page_awake_zones
        self.ui_goto(page_main)

    def run_wild(self):
        logger.error('Wild mode is not implemented')
        pass

    def check_friend_battle_count(self) -> tuple[int, bool]:
        """
        检测当前可用的协战次数
        :return: (可用协战次数, 是否识别成功)，如果检测失败返回(0, False)
        """
        logger.info('开始检测协战次数')
        
        try:
            # 从当前位置导航到主页
            self.ui_get_current_page()
            self.ui_goto(page_main)
            
            # 进入好友界面
            logger.info('进入好友界面')
            self.ui_goto(page_friends)

            # 查找并点击协战按钮
            logger.info('查找协战按钮')
            self.screenshot()
            if self.appear_then_click(self.I_FRIEND_BATTLE_BUTTON, interval=1):
                logger.info('成功找到并点击协战按钮')
                sleep(1)  # 等待界面加载
                
                # OCR识别协战次数
                friend_count, success = self.ocr_friend_battle_count()
                logger.info('检测到的协战次数: %d, 识别成功: %s', friend_count, success)
                
                # 返回主页
                logger.info('返回主页')
                self.ui_goto(page_main)
                
                return friend_count, success
            else:
                logger.warning('未找到协战按钮')
                
        except Exception as e:
            logger.error('检测协战次数失败: %s', str(e))
        
        # 检测失败，确保返回主页
        logger.warning('协战次数检测失败，返回默认值 (0, False)')
        try:
            self.ui_get_current_page()
            self.ui_goto(page_main)
        except Exception:
            pass
        return 0, False

    def ocr_friend_battle_count(self) -> tuple[int, bool]:
        """
        OCR识别协战次数
        :return: (协战次数, 是否识别成功)，识别失败返回(0, False)
        """
        logger.info('开始OCR识别协战次数')
        max_retry = 3

        for attempt in range(max_retry):
            try:
                # 先截图获取最新图像
                self.screenshot()

                # 使用OCR识别指定区域，DigitCounter模式返回 (current, remaining, total)
                ocr_result = self.O_FRIEND_BATTLE_COUNT.ocr(self.device.image)
                logger.info('第%d次OCR识别结果: %s', attempt + 1, str(ocr_result))

                # 如果OCR识别成功，ocr_result 是 (used_count, available_count, total_count)
                if ocr_result and ocr_result != (0, 0, 0):
                    used_count, available_count, total_count = ocr_result

                    # 验证数值是否在合理范围内
                    if 0 <= used_count <= 15 and 0 <= available_count <= 15 and total_count == 15:
                        logger.info('已使用协战次数: %d, 剩余可用: %d, 总计: %d', used_count, available_count, total_count)
                        return available_count, True
                    else:
                        logger.warning('协战次数超出合理范围: used=%d, available=%d, total=%d', used_count, available_count, total_count)
                else:
                    logger.warning('OCR识别失败或返回空结果')

                # 如果不是最后一次重试，等待一下再试
                if attempt < max_retry - 1:
                    sleep(1)

            except Exception as e:
                logger.error('第%d次OCR识别协战次数异常: %s', attempt + 1, str(e))
                if attempt < max_retry - 1:
                    sleep(1)

        logger.warning('OCR识别协战次数失败，已重试%d次', max_retry)
        return 0, False

if __name__ == '__main__':
    from module.config.config import Config
    from module.device.device import Device

    c = Config('oas1')
    d = Device(c)
    t = ScriptTask(c, d)

    t.run()

    # t.check_layer('悲')

    from module.base.timer import timer
