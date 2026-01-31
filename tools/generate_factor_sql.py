#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据 features 目录下的特征定义，自动生成 factor_definition 表的 INSERT SQL 语句。

用法（在项目根目录执行）：
    python tools/generate_factor_sql.py > ruoyi-fastapi-backend/sql/factor_definition_auto.sql

注意：
- 这里只是根据特征名自动生成因子代码及基础元数据（category/freq/window_size 等）；
- expr/source_table/window_size 等需要你根据实际数据表结构和计算逻辑再细化调整。
"""

import datetime
import os
import sys
from typing import List, Tuple, Optional

# 确保项目根目录在 sys.path 中，方便导入 features 包
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from features.price_action_features import PriceActionFeatureExtractor
from features.technical_features import TechnicalFeatureExtractor
from features.pattern_features import PatternFeatureExtractor
from features.market_features import MarketFeatureExtractor
from features.time_series_features import TimeSeriesFeatureExtractor
from features.moneyflow_features import MoneyFlowFeatureExtractor


# ===================== 可根据实际情况调整的默认配置 =====================

DEFAULT_FREQ = "D"  # 因子频率：日频
DEFAULT_WINDOW = 20  # 默认滚动窗口，可按分类再细分
DEFAULT_CALC_TYPE = "PY_EXPR"  # 当前因子引擎仅支持 PY_EXPR
# 行情源表名（请改成你真实的 Tushare 行情表名，比如 daily_quote / stock_daily_quote 等）
DEFAULT_SOURCE_TABLE = "daily_quote"
DEFAULT_ENABLE_FLAG = "0"  # 0 启用、1 停用

# 每个因子大类映射到 factor_definition.category 字段
CATEGORY_MAP = {
    "price_action": "PRICE_ACTION",
    "technical": "TECHNICAL",
    "pattern": "PATTERN",
    "market": "MARKET",
    "time_series": "TIME_SERIES",
    "moneyflow": "MONEYFLOW",
}

# 针对不同大类给一个简单的中文名称前缀
CATEGORY_NAME_PREFIX = {
    "price_action": "价格行为",
    "technical": "技术指标",
    "pattern": "形态",
    "market": "市场",
    "time_series": "时间序列",
    "moneyflow": "资金流",
}


def _escape_sql_str(s: str) -> str:
    """简单转义单引号，避免 SQL 语法错误。"""
    return s.replace("'", "''")


def make_row(category_key: str, factor_code: str) -> Tuple[
    str, str, str, str, int, str, Optional[str], Optional[str], Optional[str], Optional[str], str, str
]:
    """
    构造一条 factor_definition 记录的字段值。

    返回：
        (factor_code, factor_name, category, freq, window_size,
         calc_type, expr, source_table, dependencies, params, enable_flag, remark)
    """
    category = CATEGORY_MAP.get(category_key, category_key.upper())
    name_prefix = CATEGORY_NAME_PREFIX.get(category_key, category_key)

    # 因子中文名：简单规则 = 前缀 + "_" + 原始 code
    factor_name = f"{name_prefix}_{factor_code}"

    # expr：这里先留空，由你后续手工填写具体 pandas 表达式
    expr: Optional[str] = None

    # params/dependencies 先用 NULL，占位
    dependencies: Optional[str] = None
    params: Optional[str] = None

    remark = (
        "auto generated from features by script at "
        f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    return (
        factor_code,
        factor_name,
        category,
        DEFAULT_FREQ,
        DEFAULT_WINDOW,
        DEFAULT_CALC_TYPE,
        expr,
        DEFAULT_SOURCE_TABLE,
        dependencies,
        params,
        DEFAULT_ENABLE_FLAG,
        remark,
    )


def build_factor_rows() -> List[
    Tuple[str, str, str, str, int, str, Optional[str], Optional[str], Optional[str], Optional[str], str, str]
]:
    """
    从各个 FeatureExtractor 中收集 factor_code 列表，生成行数据。
    """
    rows: List[
        Tuple[str, str, str, str, int, str, Optional[str], Optional[str], Optional[str], Optional[str], str, str]
    ] = []

    # 价格行为特征
    pa_names = PriceActionFeatureExtractor().get_feature_names()
    for name in pa_names:
        factor_code = f"price_action_{name}"
        rows.append(make_row("price_action", factor_code))

    # 技术指标特征
    tech_names = TechnicalFeatureExtractor().get_feature_names()
    for name in tech_names:
        factor_code = f"technical_{name}"
        rows.append(make_row("technical", factor_code))

    # 形态特征
    pattern_names = PatternFeatureExtractor().get_feature_names()
    for name in pattern_names:
        factor_code = f"pattern_{name}"
        rows.append(make_row("pattern", factor_code))

    # 市场特征
    market_names = MarketFeatureExtractor().get_feature_names()
    for name in market_names:
        factor_code = f"market_{name}"
        rows.append(make_row("market", factor_code))

    # 时间序列特征
    ts_names = TimeSeriesFeatureExtractor().get_feature_names()
    for name in ts_names:
        factor_code = f"time_series_{name}"
        rows.append(make_row("time_series", factor_code))

    # 资金流特征
    mf_names = MoneyFlowFeatureExtractor().get_feature_names()
    for name in mf_names:
        factor_code = f"moneyflow_{name}"
        rows.append(make_row("moneyflow", factor_code))

    return rows


def main() -> None:
    rows = build_factor_rows()

    print("-- 自动生成的因子定义 SQL")
    print("-- 请根据实际情况检查/修改：source_table / expr / window_size / category 等字段")
    print()

    for row in rows:
        (
            factor_code,
            factor_name,
            category,
            freq,
            window_size,
            calc_type,
            expr,
            source_table,
            dependencies,
            params,
            enable_flag,
            remark,
        ) = row

        parts = [
            "INSERT INTO factor_definition (",
            "factor_code, factor_name, category, freq, window_size, ",
            "calc_type, expr, source_table, dependencies, params, enable_flag, remark",
            ") VALUES (",
            f"'{_escape_sql_str(factor_code)}', ",
            f"'{_escape_sql_str(factor_name)}', ",
            f"'{_escape_sql_str(category)}', ",
            f"'{_escape_sql_str(freq)}', ",
            f"{int(window_size)}, ",
            f"'{_escape_sql_str(calc_type)}', ",
            (f"'{_escape_sql_str(expr)}', " if expr else "NULL, "),
            (f"'{_escape_sql_str(source_table)}', " if source_table else "NULL, "),
            ("NULL, " if dependencies is None else f"'{_escape_sql_str(dependencies)}', "),
            ("NULL, " if params is None else f"'{_escape_sql_str(params)}', "),
            f"'{_escape_sql_str(enable_flag)}', ",
            f"'{_escape_sql_str(remark)}'",
            ");",
        ]
        sql = "".join(parts)
        print(sql)


if __name__ == "__main__":
    main()

