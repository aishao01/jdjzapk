"""
utils.py — 工具函数
时间解析、金额计算、备份恢复、格式化
"""

from datetime import datetime


def parse_time(t: str) -> int:
    """HH:MM -> 分钟数，失败返回0"""
    try:
        parts = t.strip().split(':')
        return int(parts[0]) * 60 + int(parts[1])
    except (ValueError, IndexError):
        return 0


def time_diff_min(start: str, end: str) -> int:
    """两个时间 HH:MM -> 分钟差，>=0"""
    s = parse_time(start)
    e = parse_time(end)
    return max(0, e - s)


def time_diff_hours(start: str, end: str) -> float:
    """两个时间 HH:MM -> 小时数"""
    return time_diff_min(start, end) / 60.0


def calc_total_hours(am_s, am_e, pm_s, pm_e, ot_s, ot_e) -> float:
    """计算上午+下午+加班总小时数"""
    return (time_diff_hours(am_s, am_e) +
            time_diff_hours(pm_s, pm_e) +
            time_diff_hours(ot_s, ot_e))


def calc_amount(hours: float, price: float, unit: str, days: int = 1) -> float:
    """
    根据单位计算金额
    - 小时: hours * price
    - 台/班: (hours/8) * price
    - 包月/次/天: 数量 * price (数量由外部传入)
    """
    if unit in ('小时', 'h'):
        return hours * price
    elif unit == '台/班':
        return (hours / 8.0) * price if hours else 0
    elif unit == '包月':
        return hours * price  # hours 作为手动填写数量
    elif unit == '次':
        return hours * price  # hours 作为次数
    elif unit == '天':
        return days * price if days else price
    return hours * price


def calc_date_range_days(start: str, end: str) -> int:
    """计算日期范围的天数"""
    try:
        d1 = datetime.strptime(start[:10], '%Y-%m-%d')
        d2 = datetime.strptime(end[:10], '%Y-%m-%d')
        return max(1, (d2 - d1).days + 1)
    except (ValueError, TypeError):
        return 1


def timestamp_filename(prefix: str, ext: str = 'db') -> str:
    """生成带时间戳的文件名: prefix_YYYYMMDD_HHMM.ext"""
    return f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M')}.{ext}"


def get_now_str(fmt: str = '%Y-%m-%d') -> str:
    """获取当前日期/时间字符串"""
    return datetime.now().strftime(fmt)


def get_all_time_options(step_min: int = 30) -> list:
    """生成所有时间选项 HH:MM，默认30分钟一格"""
    times = []
    for h in range(0, 24):
        for m in range(0, 60, step_min):
            times.append(f'{h:02d}:{m}')
    return times


# 常用的默认工作时间
DEFAULT_AM_START = '07:00'
DEFAULT_AM_END   = '11:00'
DEFAULT_PM_START = '13:00'
DEFAULT_PM_END   = '17:00'
