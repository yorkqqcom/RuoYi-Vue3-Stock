from collections.abc import Sequence
from typing import Any

import pandas as pd
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import PageModel
from module_tushare.entity.do.tushare_do import (
    TushareApiConfig,
    TushareData,
    TushareDownloadLog,
    TushareDownloadTask,
)
from module_tushare.entity.vo.tushare_vo import (
    TushareApiConfigModel,
    TushareApiConfigPageQueryModel,
    TushareDataModel,
    TushareDataPageQueryModel,
    TushareDownloadLogPageQueryModel,
    TushareDownloadTaskModel,
    TushareDownloadTaskPageQueryModel,
)
from utils.common_util import CamelCaseUtil
from utils.page_util import PageUtil


class TushareApiConfigDao:
    """
    Tushare接口配置管理模块数据库操作层
    """

    @classmethod
    async def get_config_detail_by_id(cls, db: AsyncSession, config_id: int) -> TushareApiConfig | None:
        """
        根据配置id获取配置详细信息

        :param db: orm对象
        :param config_id: 配置id
        :return: 配置信息对象
        """
        config_info = (await db.execute(select(TushareApiConfig).where(TushareApiConfig.config_id == config_id))).scalars().first()

        return config_info

    @classmethod
    async def get_config_detail_by_info(
        cls, db: AsyncSession, config: TushareApiConfigModel
    ) -> TushareApiConfig | None:
        """
        根据配置参数获取配置信息

        :param db: orm对象
        :param config: 配置参数对象
        :return: 配置信息对象
        """
        config_info = (
            (
                await db.execute(
                    select(TushareApiConfig).where(
                        TushareApiConfig.api_code == config.api_code,
                    )
                )
            )
            .scalars()
            .first()
        )

        return config_info

    @classmethod
    async def get_config_list(
        cls, db: AsyncSession, query_object: TushareApiConfigPageQueryModel, is_page: bool = False
    ) -> PageModel | list[dict[str, Any]]:
        """
        根据查询参数获取配置列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 配置列表信息对象
        """
        query = (
            select(TushareApiConfig)
            .where(
                TushareApiConfig.api_name.like(f'%{query_object.api_name}%') if query_object.api_name else True,
                TushareApiConfig.api_code.like(f'%{query_object.api_code}%') if query_object.api_code else True,
                TushareApiConfig.status == query_object.status if query_object.status else True,
            )
            .order_by(TushareApiConfig.config_id)
            .distinct()
        )

        config_list: PageModel | list[dict[str, Any]] = await PageUtil.paginate(
            db, query, query_object.page_num, query_object.page_size, is_page
        )
        return config_list

    @classmethod
    async def add_config_dao(cls, db: AsyncSession, config: TushareApiConfigModel) -> TushareApiConfig:
        """
        新增配置信息

        :param db: orm对象
        :param config: 配置对象
        :return: 配置对象
        """
        db_config = TushareApiConfig(**config.model_dump(exclude={'config_id'}))
        db.add(db_config)
        await db.flush()
        await db.refresh(db_config)
        return db_config

    @classmethod
    async def edit_config_dao(cls, db: AsyncSession, config: TushareApiConfigModel) -> int:
        """
        编辑配置信息

        :param db: orm对象
        :param config: 配置对象
        :return: 编辑结果
        """
        await db.execute(
            update(TushareApiConfig)
            .where(TushareApiConfig.config_id == config.config_id)
            .values(**config.model_dump(exclude={'config_id'}, exclude_none=True))
        )
        return config.config_id

    @classmethod
    async def delete_config_dao(cls, db: AsyncSession, config_ids: Sequence[int]) -> int:
        """
        删除配置信息

        :param db: orm对象
        :param config_ids: 配置id列表
        :return: 删除结果
        """
        result = await db.execute(delete(TushareApiConfig).where(TushareApiConfig.config_id.in_(config_ids)))
        return result.rowcount


class TushareDownloadTaskDao:
    """
    Tushare下载任务管理模块数据库操作层
    """

    @classmethod
    async def get_task_detail_by_id(cls, db: AsyncSession, task_id: int) -> TushareDownloadTask | None:
        """
        根据任务id获取任务详细信息

        :param db: orm对象
        :param task_id: 任务id
        :return: 任务信息对象
        """
        task_info = (
            (await db.execute(select(TushareDownloadTask).where(TushareDownloadTask.task_id == task_id)))
            .scalars()
            .first()
        )

        return task_info

    @classmethod
    async def get_task_detail_by_info(
        cls, db: AsyncSession, task: TushareDownloadTaskModel
    ) -> TushareDownloadTask | None:
        """
        根据任务参数获取任务信息

        :param db: orm对象
        :param task: 任务参数对象
        :return: 任务信息对象
        """
        task_info = (
            (
                await db.execute(
                    select(TushareDownloadTask).where(
                        TushareDownloadTask.task_name == task.task_name,
                    )
                )
            )
            .scalars()
            .first()
        )

        return task_info

    @classmethod
    async def get_task_list(
        cls, db: AsyncSession, query_object: TushareDownloadTaskPageQueryModel, is_page: bool = False
    ) -> PageModel | list[dict[str, Any]]:
        """
        根据查询参数获取任务列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 任务列表信息对象
        """
        query = (
            select(TushareDownloadTask)
            .where(
                TushareDownloadTask.task_name.like(f'%{query_object.task_name}%') if query_object.task_name else True,
                TushareDownloadTask.config_id == query_object.config_id if query_object.config_id else True,
                TushareDownloadTask.status == query_object.status if query_object.status else True,
            )
            .order_by(TushareDownloadTask.task_id)
            .distinct()
        )

        config_list: PageModel | list[dict[str, Any]] = await PageUtil.paginate(
            db, query, query_object.page_num, query_object.page_size, is_page
        )
        return config_list

    @classmethod
    async def add_task_dao(cls, db: AsyncSession, task: TushareDownloadTaskModel) -> TushareDownloadTask:
        """
        新增任务信息

        :param db: orm对象
        :param task: 任务对象
        :return: 任务对象
        """
        db_task = TushareDownloadTask(**task.model_dump(exclude={'task_id'}))
        db.add(db_task)
        await db.flush()
        await db.refresh(db_task)
        return db_task

    @classmethod
    async def edit_task_dao(
        cls, db: AsyncSession, task_id_or_model: int | TushareDownloadTaskModel, task_dict: dict[str, Any] | None = None
    ) -> int:
        """
        编辑任务信息

        :param db: orm对象
        :param task_id_or_model: 任务ID（int）或任务模型对象（TushareDownloadTaskModel）
        :param task_dict: 任务字段字典（snake_case格式），当第一个参数是task_id时使用
        :return: 编辑结果
        """
        from utils.log_util import logger
        
        # 支持两种调用方式：1) edit_task_dao(db, task_id, task_dict) 2) edit_task_dao(db, task_model)
        if isinstance(task_id_or_model, TushareDownloadTaskModel):
            # 旧的方式：传入模型对象
            task = task_id_or_model
            task_id = task.task_id
            if task_id is None:
                raise ValueError('task_id不能为None')
            task_dict = task.model_dump(
                exclude={
                    'task_id',
                    'last_run_time', 'next_run_time', 'run_count', 'success_count', 'fail_count',
                    'create_by', 'create_time'
                },
                exclude_none=False,
                by_alias=False
            )
        else:
            # 新的方式：直接传入task_id和字典
            task_id = task_id_or_model
            if task_dict is None:
                raise ValueError('当使用task_id时，必须提供task_dict参数')
        
        logger.info(f'[DAO编辑任务] 开始更新，task_id: {task_id}')
        logger.info(f'[DAO编辑任务] 接收到的字典: {task_dict}')
        
        # 从字典中移除 task_id，因为它只用于 WHERE 条件
        update_dict = {k: v for k, v in task_dict.items() if k != 'task_id'}
        # 再次排除不应该更新的字段
        excluded_fields = {
            'last_run_time', 'next_run_time', 'run_count', 'success_count', 'fail_count',
            'create_by', 'create_time'
        }
        update_dict = {k: v for k, v in update_dict.items() if k not in excluded_fields}
        
        logger.info(f'[DAO编辑任务] 准备更新的字段字典: {update_dict}')
        logger.info(f'[DAO编辑任务] 字典键: {list(update_dict.keys())}')
        logger.info(f'[DAO编辑任务] cron_expression值: {update_dict.get("cron_expression")}, 类型: {type(update_dict.get("cron_expression"))}')
        logger.info(f'[DAO编辑任务] task_name值: {update_dict.get("task_name")}')
        
        stmt = update(TushareDownloadTask).where(TushareDownloadTask.task_id == task_id).values(**update_dict)
        logger.info(f'[DAO编辑任务] SQL语句: {stmt}')
        
        result = await db.execute(stmt)
        logger.info(f'[DAO编辑任务] 执行结果: rowcount={result.rowcount}')
        
        if result.rowcount == 0:
            logger.warning(f'[DAO编辑任务] 警告：没有更新任何记录，task_id: {task_id}')
        
        return task_id

    @classmethod
    async def delete_task_dao(cls, db: AsyncSession, task_ids: Sequence[int]) -> int:
        """
        删除任务信息

        :param db: orm对象
        :param task_ids: 任务id列表
        :return: 删除结果
        """
        result = await db.execute(delete(TushareDownloadTask).where(TushareDownloadTask.task_id.in_(task_ids)))
        return result.rowcount


class TushareDownloadLogDao:
    """
    Tushare下载日志管理模块数据库操作层
    """

    @classmethod
    async def get_log_list(
        cls, db: AsyncSession, query_object: TushareDownloadLogPageQueryModel, is_page: bool = False
    ) -> PageModel | list[dict[str, Any]]:
        """
        根据查询参数获取日志列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 日志列表信息对象
        """
        query = (
            select(TushareDownloadLog)
            .where(
                TushareDownloadLog.task_id == query_object.task_id if query_object.task_id else True,
                TushareDownloadLog.task_name.like(f'%{query_object.task_name}%') if query_object.task_name else True,
                TushareDownloadLog.status == query_object.status if query_object.status else True,
            )
            .order_by(TushareDownloadLog.log_id.desc())
            .distinct()
        )

        config_list: PageModel | list[dict[str, Any]] = await PageUtil.paginate(
            db, query, query_object.page_num, query_object.page_size, is_page
        )
        return config_list

    @classmethod
    async def add_log_dao(cls, db: AsyncSession, log: TushareDownloadLog) -> TushareDownloadLog:
        """
        新增日志信息

        :param db: orm对象
        :param log: 日志对象
        :return: 日志对象
        """
        db.add(log)
        await db.flush()
        await db.refresh(log)
        return log

    @classmethod
    async def delete_log_dao(cls, db: AsyncSession, log_ids: Sequence[int]) -> int:
        """
        删除日志信息

        :param db: orm对象
        :param log_ids: 日志id列表
        :return: 删除结果
        """
        result = await db.execute(delete(TushareDownloadLog).where(TushareDownloadLog.log_id.in_(log_ids)))
        return result.rowcount

    @classmethod
    async def clear_log_dao(cls, db: AsyncSession) -> int:
        """
        清空所有日志信息

        :param db: orm对象
        :return: 删除结果
        """
        result = await db.execute(delete(TushareDownloadLog))
        return result.rowcount


class TushareDataDao:
    """
    Tushare数据存储管理模块数据库操作层
    """

    @classmethod
    async def get_data_list(
        cls, db: AsyncSession, query_object: TushareDataPageQueryModel, is_page: bool = False
    ) -> PageModel | list[dict[str, Any]]:
        """
        获取数据列表

        :param db: orm对象
        :param query_object: 查询对象
        :param is_page: 是否分页
        :return: 数据列表
        """
        query = (
            select(TushareData)
            .where(
                TushareData.task_id == query_object.task_id if query_object.task_id else True,
                TushareData.config_id == query_object.config_id if query_object.config_id else True,
                TushareData.api_code.like(f'%{query_object.api_code}%') if query_object.api_code else True,
                TushareData.download_date == query_object.download_date if query_object.download_date else True,
            )
            .order_by(TushareData.data_id.desc())
            .distinct()
        )
        data_list: PageModel | list[dict[str, Any]] = await PageUtil.paginate(
            db, query, query_object.page_num, query_object.page_size, is_page
        )

        return data_list

    @classmethod
    async def add_data_dao(cls, db: AsyncSession, data: TushareData) -> TushareData:
        """
        新增数据

        :param db: orm对象
        :param data: 数据对象
        :return: 新增的数据对象
        """
        db.add(data)
        await db.flush()
        return data

    @classmethod
    async def add_data_batch_dao(cls, db: AsyncSession, data_list: list[TushareData]) -> list[TushareData]:
        """
        批量新增数据

        :param db: orm对象
        :param data_list: 数据对象列表
        :return: 新增的数据对象列表
        """
        db.add_all(data_list)
        await db.flush()
        return data_list

    @classmethod
    async def add_dataframe_to_table_dao(
        cls, db: AsyncSession, table_name: str, df: pd.DataFrame, task_id: int, config_id: int, api_code: str, download_date: str
    ) -> int:
        """
        将 DataFrame 批量插入到指定表（表结构与 DataFrame 列一致）

        :param db: orm对象
        :param table_name: 表名（需要验证，防止SQL注入）
        :param df: pandas DataFrame
        :param task_id: 任务ID
        :param config_id: 配置ID
        :param api_code: 接口代码
        :param download_date: 下载日期
        :return: 插入的记录数
        """
        from sqlalchemy import text
        from config.env import DataBaseConfig
        import json
        import re
        from datetime import datetime

        if df is None or df.empty:
            return 0

        # 验证表名，只允许字母、数字和下划线
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name):
            raise ValueError(f'无效的表名: {table_name}')

        # 准备列名（系统列 + DataFrame 列）
        system_columns = ['task_id', 'config_id', 'api_code', 'download_date', 'create_time']
        
        # 清理和验证 DataFrame 列名
        df_columns = []
        for col in df.columns:
            safe_col = re.sub(r'[^a-zA-Z0-9_]', '_', str(col))
            if not safe_col or safe_col[0].isdigit():
                safe_col = f'col_{safe_col}'
            df_columns.append(safe_col)
        
        all_columns = system_columns + df_columns
        
        # 构建 INSERT SQL
        if DataBaseConfig.db_type == 'postgresql':
            # PostgreSQL 使用命名参数
            col_names = ', '.join([f'"{col}"' if col in df_columns else f'"{col}"' for col in all_columns])
            placeholders = ', '.join([f':{col}' for col in all_columns])
            insert_sql = f'INSERT INTO "{table_name}" ({col_names}) VALUES ({placeholders})'
        else:
            # MySQL 使用命名参数
            col_names = ', '.join([f'`{col}`' for col in all_columns])
            placeholders = ', '.join([f':{col}' for col in all_columns])
            insert_sql = f'INSERT INTO `{table_name}` ({col_names}) VALUES ({placeholders})'

        # 准备批量插入数据
        values_list = []
        create_time = datetime.now()
        
        for idx, row in df.iterrows():
            row_dict = {
                'task_id': task_id,
                'config_id': config_id,
                'api_code': api_code,
                'download_date': download_date,
                'create_time': create_time,
            }
            
            # 添加 DataFrame 的列值
            for orig_col, safe_col in zip(df.columns, df_columns):
                value = row[orig_col]
                # 处理 NaN 值
                if pd.isna(value):
                    row_dict[safe_col] = None
                else:
                    row_dict[safe_col] = value
            
            values_list.append(row_dict)

        # 执行批量插入
        if values_list:
            result = await db.execute(text(insert_sql), values_list)
            await db.flush()
            return len(values_list)
        
        return 0

    @classmethod
    async def add_data_batch_to_table_dao(
        cls, db: AsyncSession, table_name: str, data_list: list[dict]
    ) -> int:
        """
        批量新增数据到指定表（使用动态表名）

        :param db: orm对象
        :param table_name: 表名（需要验证，防止SQL注入）
        :param data_list: 数据字典列表
        :return: 插入的记录数
        """
        from sqlalchemy import text, inspect
        from config.env import DataBaseConfig
        import json
        import re

        if not data_list:
            return 0

        # 验证表名，只允许字母、数字和下划线
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name):
            raise ValueError(f'无效的表名: {table_name}')

        # 根据数据库类型选择不同的插入方式
        if DataBaseConfig.db_type == 'postgresql':
            # PostgreSQL 使用 JSONB，表名需要用双引号转义
            # 使用命名参数，SQLAlchemy 会自动转换为 PostgreSQL 的位置参数
            insert_sql = f"""
                INSERT INTO "{table_name}" (task_id, config_id, api_code, download_date, data_content, create_time)
                VALUES (:task_id, :config_id, :api_code, :download_date, CAST(:data_content AS JSONB), :create_time)
            """
        else:
            # MySQL 使用 JSON，表名用反引号转义
            insert_sql = f"""
                INSERT INTO `{table_name}` (task_id, config_id, api_code, download_date, data_content, create_time)
                VALUES (:task_id, :config_id, :api_code, :download_date, :data_content, :create_time)
            """

        # 准备批量插入数据（统一使用字典列表）
        values_list = []
        for data in data_list:
            # 将字典转换为 JSON 字符串
            data_content = json.dumps(data['data_content'], ensure_ascii=False)
            
            values_list.append({
                'task_id': data['task_id'],
                'config_id': data['config_id'],
                'api_code': data['api_code'],
                'download_date': data['download_date'],
                'data_content': data_content,
                'create_time': data['create_time']
            })

        # 执行批量插入
        result = await db.execute(text(insert_sql), values_list)
        await db.flush()
        return len(values_list)

    @classmethod
    async def delete_data_dao(cls, db: AsyncSession, data_ids: list[int]) -> int:
        """
        删除数据

        :param db: orm对象
        :param data_ids: 数据ID列表
        :return: 删除数量
        """
        result = await db.execute(delete(TushareData).where(TushareData.data_id.in_(data_ids)))
        return result.rowcount

    @classmethod
    async def clear_data_dao(cls, db: AsyncSession) -> int:
        """
        清空所有数据

        :param db: orm对象
        :return: 删除结果
        """
        result = await db.execute(delete(TushareData))
        return result.rowcount
