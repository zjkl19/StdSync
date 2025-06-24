# ==================== stdsync/core/models.py ===============
"""
数据类定义模块
"""
from dataclasses import dataclass
from datetime import date
from typing import List


@dataclass
class Standard:
    """通用标准数据类（国家或企业都可复用）"""
    code: str
    name: str
    impl_date: date | None


@dataclass
class CompanyStandard(Standard):
    """公司内部标准行"""
    dept: str | None = None
    receive_date: date | None = None


@dataclass
class AnnouncementItem(Standard):
    """国家标准公告条目，附带旧标准号列表"""
    replaced_codes: List[str]


@dataclass
class MatchResult:
    """比对结果，用于报表输出"""
    company: CompanyStandard
    gb_old_code: str | None
    gb_new_code: str | None
    status: str                 # OBSOLETE / REVIEW / OK / UNUSED
    similarity: int | None = None
    reason: str | None = None
    days_to_replace: int | None = None