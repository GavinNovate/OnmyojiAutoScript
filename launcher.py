#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import quote


API_BASE = "http://127.0.0.1:22288"
# launcher.txt 写法说明：
# 1) 每行一个账号（配置名）
# 2) 支持写 abc / abc.json / abc.config
# 3) 空行和以 # 开头的行会被忽略
# 4) 示例：
#    abc
#    def.json
#    ghi.config
LAUNCHER_FILE = Path("config") / "launcher.txt"
LAUNCH_INTERVAL_SECONDS = 30
SERVER_READY_TIMEOUT_SECONDS = 120


def normalize_name(raw: str) -> str:
    name = raw.strip()
    if name.endswith(".json"):
        return name[:-5]
    if name.endswith(".config"):
        return name[:-7]
    return name


def read_accounts() -> list[str]:
    if not LAUNCHER_FILE.exists():
        print(f"错误: 找不到列表文件 {LAUNCHER_FILE}")
        return []

    accounts: list[str] = []
    with LAUNCHER_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            accounts.append(normalize_name(line))
    return accounts


def wait_server_ready(timeout_seconds: int) -> bool:
    print(f"等待 server 就绪（最多 {timeout_seconds} 秒）...")
    start = time.time()
    while time.time() - start < timeout_seconds:
        try:
            with urlopen(f"{API_BASE}/test", timeout=3) as resp:
                if resp.status == 200:
                    print("✓ server 已就绪")
                    return True
        except (URLError, HTTPError, TimeoutError):
            pass
        time.sleep(2)
    return False


def start_config(name: str) -> bool:
    encoded_name = quote(name, safe="")
    try:
        with urlopen(f"{API_BASE}/{encoded_name}/start", timeout=8) as resp:
            return resp.status == 200
    except (URLError, HTTPError, TimeoutError):
        return False


def main() -> int:
    accounts = read_accounts()
    if not accounts:
        print("错误: launcher.txt 里没有可启动账号")
        return 1

    print(f"读取到 {len(accounts)} 个账号: {', '.join(accounts)}")

    if not wait_server_ready(SERVER_READY_TIMEOUT_SECONDS):
        print("错误: 等待 server 超时，请确认 oas.exe/osa.exe 已启动")
        return 2

    for i, account in enumerate(accounts, start=1):
        ok = start_config(account)
        mark = "✓" if ok else "✗"
        print(f"[{i}/{len(accounts)}] 启动 {account} {mark}")

        if i < len(accounts):
            print(f"等待 {LAUNCH_INTERVAL_SECONDS} 秒后启动下一个...")
            time.sleep(LAUNCH_INTERVAL_SECONDS)

    print("全部启动流程完成")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
