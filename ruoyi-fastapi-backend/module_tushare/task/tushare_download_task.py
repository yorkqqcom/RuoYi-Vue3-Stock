import json
import os
import traceback
from datetime import datetime
from typing import Any

import pandas as pd
import tushare as ts
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import AsyncSessionLocal
from config.env import DataBaseConfig, TushareConfig
from module_tushare.dao.tushare_dao import (
    TushareApiConfigDao,
    TushareDataDao,
    TushareDownloadLogDao,
    TushareDownloadTaskDao,
)
from module_tushare.entity.do.tushare_do import TushareData, TushareDownloadLog
from module_tushare.entity.vo.tushare_vo import TushareDownloadTaskModel
from utils.log_util import logger


def pandas_dtype_to_db_type(dtype, db_type: str = 'postgresql') -> str:
    """
    将 pandas 数据类型转换为数据库类型

    :param dtype: pandas 数据类型
    :param db_type: 数据库类型 ('postgresql' 或 'mysql')
    :return: 数据库类型字符串
    """
    import pandas as pd
    import numpy as np
    
    dtype_str = str(dtype)
    
    # 整数类型
    if pd.api.types.is_integer_dtype(dtype):
        if 'int64' in dtype_str or 'Int64' in dtype_str:
            return 'BIGINT' if db_type == 'postgresql' else 'BIGINT'
        elif 'int32' in dtype_str or 'Int32' in dtype_str:
            return 'INTEGER' if db_type == 'postgresql' else 'INT'
        elif 'int16' in dtype_str or 'Int16' in dtype_str:
            return 'SMALLINT' if db_type == 'postgresql' else 'SMALLINT'
        else:
            return 'INTEGER' if db_type == 'postgresql' else 'INT'
    
    # 浮点数类型
    elif pd.api.types.is_float_dtype(dtype):
        if 'float64' in dtype_str or 'Float64' in dtype_str:
            return 'DOUBLE PRECISION' if db_type == 'postgresql' else 'DOUBLE'
        elif 'float32' in dtype_str or 'Float32' in dtype_str:
            return 'REAL' if db_type == 'postgresql' else 'FLOAT'
        else:
            return 'DOUBLE PRECISION' if db_type == 'postgresql' else 'DOUBLE'
    
    # 布尔类型
    elif pd.api.types.is_bool_dtype(dtype):
        return 'BOOLEAN' if db_type == 'postgresql' else 'TINYINT(1)'
    
    # 日期时间类型
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return 'TIMESTAMP(0)' if db_type == 'postgresql' else 'DATETIME'
    
    # 日期类型（pandas 中没有单独的日期类型，通常使用 datetime64）
    # 注意：pandas 的 is_date_dtype 在新版本中已移除，这里通过检查是否为 datetime64[ns] 的日期部分来判断
    # 实际上，pandas 中日期通常存储为 datetime64，所以这里可以省略
    
    # 字符串类型
    elif pd.api.types.is_string_dtype(dtype) or pd.api.types.is_object_dtype(dtype):
        # 默认使用 VARCHAR，可以根据实际数据长度调整
        return 'VARCHAR(500)' if db_type == 'postgresql' else 'VARCHAR(500)'
    
    # 默认返回文本类型
    else:
        return 'TEXT' if db_type == 'postgresql' else 'TEXT'


async def ensure_table_exists(session: AsyncSession, table_name: str, api_code: str, df: pd.DataFrame | None = None) -> None:
    """
    确保表存在，如果不存在则根据 DataFrame 结构创建

    :param session: 数据库会话
    :param table_name: 表名
    :param api_code: 接口代码（用于注释）
    :param df: DataFrame，用于确定表结构
    :return: None
    """
    import re
    
    # 验证表名，只允许字母、数字和下划线
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name):
        raise ValueError(f'无效的表名: {table_name}')
    
    # 检查表是否存在
    if DataBaseConfig.db_type == 'postgresql':
        check_sql = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = :table_name
            )
        """
        # PostgreSQL 表名和索引名需要用双引号转义
        table_name_escaped = f'"{table_name}"'
    else:
        check_sql = """
            SELECT COUNT(*) as count
            FROM information_schema.tables 
            WHERE table_schema = DATABASE()
            AND table_name = :table_name
        """
        # MySQL 表名和索引名需要用反引号转义
        table_name_escaped = f'`{table_name}`'
    
    result = await session.execute(text(check_sql), {'table_name': table_name})
    
    if DataBaseConfig.db_type == 'postgresql':
        table_exists = result.scalar()
    else:
        table_exists = result.scalar() > 0
    
    if not table_exists:
        if df is None or df.empty:
            raise ValueError(f'无法创建表 {table_name}：DataFrame 为空，无法确定表结构')
        
        # 根据 DataFrame 的列和数据类型创建表结构
        columns = []
        
        # 添加系统字段
        if DataBaseConfig.db_type == 'postgresql':
            columns.append('data_id BIGSERIAL NOT NULL PRIMARY KEY')
        else:
            columns.append('data_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY')
        
        columns.append('task_id BIGINT NOT NULL')
        columns.append('config_id BIGINT NOT NULL')
        columns.append('api_code VARCHAR(100) NOT NULL')
        columns.append('download_date VARCHAR(20)')
        columns.append('create_time TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP' if DataBaseConfig.db_type == 'postgresql' else 'create_time DATETIME DEFAULT CURRENT_TIMESTAMP')
        
        # 添加 DataFrame 的列
        for col_name in df.columns:
            # 验证列名，只允许字母、数字和下划线
            safe_col_name = re.sub(r'[^a-zA-Z0-9_]', '_', str(col_name))
            if not safe_col_name or safe_col_name[0].isdigit():
                safe_col_name = f'col_{safe_col_name}'
            
            # 获取列的数据类型
            col_dtype = df[col_name].dtype
            db_type_str = pandas_dtype_to_db_type(col_dtype, DataBaseConfig.db_type)
            
            # PostgreSQL 需要转义列名
            if DataBaseConfig.db_type == 'postgresql':
                col_def = f'"{safe_col_name}" {db_type_str}'
            else:
                col_def = f'`{safe_col_name}` {db_type_str}'
            
            columns.append(col_def)
        
        # 生成简短的索引名称（避免名称过长）
        idx_suffix = table_name[-20:] if len(table_name) > 20 else table_name
        # 生成简短的索引名称（避免名称过长）
        idx_suffix = table_name[-20:] if len(table_name) > 20 else table_name
        
        # 创建表（PostgreSQL 需要分开执行多个 SQL 语句）
        if DataBaseConfig.db_type == 'postgresql':
            # 创建表
            create_table_sql = f"CREATE TABLE {table_name_escaped} (\n    " + ",\n    ".join(columns) + "\n)"
            await session.execute(text(create_table_sql))
            await session.flush()
            
            # 创建索引（分开执行）
            index_sqls = [
                f'CREATE INDEX idx_tid_{idx_suffix} ON {table_name_escaped}(task_id)',
                f'CREATE INDEX idx_cid_{idx_suffix} ON {table_name_escaped}(config_id)',
                f'CREATE INDEX idx_ac_{idx_suffix} ON {table_name_escaped}(api_code)',
                f'CREATE INDEX idx_dd_{idx_suffix} ON {table_name_escaped}(download_date)',
                f'CREATE INDEX idx_ct_{idx_suffix} ON {table_name_escaped}(create_time)',
            ]
            
            for index_sql in index_sqls:
                await session.execute(text(index_sql))
                await session.flush()
            
            # 添加注释（分开执行）
            comment_sqls = [
                f"COMMENT ON TABLE {table_name_escaped} IS 'Tushare数据存储表（{api_code}）'",
                f"COMMENT ON COLUMN {table_name_escaped}.data_id IS '数据ID'",
                f"COMMENT ON COLUMN {table_name_escaped}.task_id IS '任务ID'",
                f"COMMENT ON COLUMN {table_name_escaped}.config_id IS '接口配置ID'",
                f"COMMENT ON COLUMN {table_name_escaped}.api_code IS '接口代码'",
                f"COMMENT ON COLUMN {table_name_escaped}.download_date IS '下载日期（YYYYMMDD）'",
                f"COMMENT ON COLUMN {table_name_escaped}.create_time IS '创建时间'",
            ]
            
            # 为 DataFrame 的列添加注释
            for col_name in df.columns:
                safe_col_name = re.sub(r'[^a-zA-Z0-9_]', '_', str(col_name))
                if not safe_col_name or safe_col_name[0].isdigit():
                    safe_col_name = f'col_{safe_col_name}'
                comment_sqls.append(f"COMMENT ON COLUMN {table_name_escaped}.\"{safe_col_name}\" IS '{col_name}'")
            
            for comment_sql in comment_sqls:
                await session.execute(text(comment_sql))
                await session.flush()
        else:
            # MySQL 可以在一个语句中执行
            # 创建索引定义
            index_defs = [
                f'INDEX idx_tid_{idx_suffix} (task_id)',
                f'INDEX idx_cid_{idx_suffix} (config_id)',
                f'INDEX idx_ac_{idx_suffix} (api_code)',
                f'INDEX idx_dd_{idx_suffix} (download_date)',
                f'INDEX idx_ct_{idx_suffix} (create_time)',
            ]
            
            create_sql = f"CREATE TABLE {table_name_escaped} (\n    " + ",\n    ".join(columns + index_defs) + f"\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Tushare数据存储表（{api_code}）';"
            await session.execute(text(create_sql))
            await session.flush()
        
        logger.info(f'已创建数据表: {table_name}，包含 {len(df.columns)} 个数据列')


async def download_tushare_data(task_id: int, download_date: str | None = None, session: AsyncSession | None = None) -> None:
    """
    下载Tushare数据的异步任务函数

    :param task_id: 任务ID
    :param download_date: 下载日期（YYYYMMDD格式），如果为None则使用当前日期
    :param session: 可选的数据库会话，如果为None则创建新会话
    :return: None
    """
    start_time = datetime.now()
    task = None
    config = None
    log = None
    use_external_session = session is not None
    # 保存任务名称和配置信息，避免在异常处理中访问 ORM 对象导致延迟加载问题
    task_name = None
    config_id = None
    api_name = None

    try:
        if session is None:
            session_context = AsyncSessionLocal()
            session = await session_context.__aenter__()
        else:
            session_context = None
        
        try:
            # 获取任务信息
            task = await TushareDownloadTaskDao.get_task_detail_by_id(session, task_id)
            if not task:
                logger.error(f'任务ID {task_id} 不存在')
                return
            
            # 保存任务名称，避免在异常处理中访问 ORM 对象
            task_name = task.task_name

            # 获取接口配置信息
            config = await TushareApiConfigDao.get_config_detail_by_id(session, task.config_id)
            if not config:
                logger.error(f'接口配置ID {task.config_id} 不存在')
                return
            
            # 保存配置信息，避免在异常处理中访问 ORM 对象
            config_id = config.config_id
            api_name = config.api_name

            if config.status != '0':
                logger.warning(f'接口配置 {config.api_name} 已停用')
                return

            # 确定下载日期
            if download_date is None:
                download_date = datetime.now().strftime('%Y%m%d')

            # 解析参数
            api_params = {}
            if config.api_params:
                api_params = json.loads(config.api_params)

            # 任务参数覆盖接口默认参数
            if task.task_params:
                task_params = json.loads(task.task_params)
                api_params.update(task_params)

            # 如果任务指定了日期范围，使用任务日期
            if task.start_date and task.end_date:
                api_params['start_date'] = task.start_date
                api_params['end_date'] = task.end_date
            elif download_date:
                # 如果没有指定日期范围，使用单日期
                api_params['trade_date'] = download_date

            # 调用tushare接口
            logger.info(f'开始下载任务: {task.task_name}, 接口: {config.api_code}, 参数: {api_params}')

            # 获取tushare pro接口
            # 优先从配置类获取，如果没有则从环境变量获取
            ts_token = TushareConfig.tushare_token or os.getenv('TUSHARE_TOKEN', '')
            if not ts_token:
                raise ValueError(
                    'TUSHARE_TOKEN未设置，请在.env.dev文件中配置TUSHARE_TOKEN环境变量。'
                    '例如：TUSHARE_TOKEN=your_tushare_token_here'
                )

            pro = ts.pro_api(ts_token)

            # 动态调用接口
            api_func = getattr(pro, config.api_code, None)
            if not api_func:
                raise ValueError(f'接口 {config.api_code} 不存在')

            # 调用接口获取数据
            try:
                df = api_func(**api_params)
            except Exception as api_error:
                error_detail = f'Tushare接口调用失败: {str(api_error)}\n参数: {api_params}'
                logger.exception(f'任务 {task.task_name} Tushare接口调用异常: {error_detail}')
                raise Exception(error_detail) from api_error

            if df is None or df.empty:
                logger.warning(f'任务 {task.task_name} 下载数据为空')
                record_count = 0
            else:
                record_count = len(df)

                # 如果指定了数据字段，只保留指定字段
                if config.data_fields:
                    data_fields = json.loads(config.data_fields)
                    if isinstance(data_fields, list):
                        # 只保留存在的字段
                        available_fields = [field for field in data_fields if field in df.columns]
                        if available_fields:
                            df = df[available_fields]

                # 保存到数据库（如果启用）
                if task.save_to_db == '1':
                    try:
                        # 确定表名：如果未指定，则使用 tushare_ + api_code
                        table_name = task.data_table_name
                        if not table_name or table_name.strip() == '':
                            table_name = f'tushare_{config.api_code}'
                        
                        # 确保表存在（如果不存在则根据 DataFrame 结构创建）
                        await ensure_table_exists(session, table_name, config.api_code, df)
                        
                        # 准备批量插入数据（直接插入到对应列，而不是 JSONB）
                        await TushareDataDao.add_dataframe_to_table_dao(session, table_name, df, task.task_id, config.config_id, config.api_code, download_date)
                        logger.info(f'已保存 {len(df)} 条数据到数据库表 {table_name}')
                    except Exception as db_error:
                        error_detail = f'保存数据到数据库失败: {str(db_error)}\n表名: {table_name}, 记录数: {len(data_list) if "data_list" in locals() else 0}'
                        logger.exception(f'任务 {task.task_name} 保存数据到数据库异常: {error_detail}')
                        raise Exception(error_detail) from db_error

                # 保存到文件（如果配置了保存路径）
                file_path = None
                if task.save_path:
                    try:
                        save_path = task.save_path
                        os.makedirs(save_path, exist_ok=True)

                        # 生成文件名
                        file_name = f"{config.api_code}_{download_date}_{datetime.now().strftime('%H%M%S')}"
                        save_format = task.save_format or 'csv'

                        if save_format == 'csv':
                            file_path = os.path.join(save_path, f'{file_name}.csv')
                            df.to_csv(file_path, index=False, encoding='utf-8-sig')
                        elif save_format == 'excel':
                            file_path = os.path.join(save_path, f'{file_name}.xlsx')
                            df.to_excel(file_path, index=False, engine='openpyxl')
                        elif save_format == 'json':
                            file_path = os.path.join(save_path, f'{file_name}.json')
                            df.to_json(file_path, orient='records', force_ascii=False, indent=2)
                        else:
                            file_path = os.path.join(save_path, f'{file_name}.csv')
                            df.to_csv(file_path, index=False, encoding='utf-8-sig')

                        logger.info(f'数据已保存到文件: {file_path}')
                    except Exception as file_error:
                        error_detail = f'保存数据到文件失败: {str(file_error)}\n保存路径: {task.save_path}, 格式: {save_format}'
                        logger.exception(f'任务 {task.task_name} 保存数据到文件异常: {error_detail}')
                        # 文件保存失败不影响整体流程，只记录错误
                        raise Exception(error_detail) from file_error

            # 计算执行时长
            duration = int((datetime.now() - start_time).total_seconds())

            # 创建下载日志
            file_path_value = file_path if record_count > 0 else None
            log = TushareDownloadLog(
                task_id=task.task_id,
                task_name=task.task_name,
                config_id=config.config_id,
                api_name=config.api_name,
                download_date=download_date,
                record_count=record_count,
                file_path=file_path_value,
                status='0',
                duration=duration,
                create_time=datetime.now(),
            )

            await TushareDownloadLogDao.add_log_dao(session, log)
            
            # 更新任务统计
            task_model = TushareDownloadTaskModel(
                taskId=task.task_id,
                runCount=(task.run_count or 0) + 1,
                successCount=(task.success_count or 0) + 1,
                lastRunTime=datetime.now()
            )
            await TushareDownloadTaskDao.edit_task_dao(session, task_model)
            
            await session.commit()

            logger.info(f'任务 {task_name or task.task_name if task else task_id} 执行成功，记录数: {record_count}, 耗时: {duration}秒')
        finally:
            # 如果使用的是外部会话，不关闭它；否则关闭内部创建的会话
            if session_context is not None:
                await session_context.__aexit__(None, None, None)

    except Exception as e:
        # 获取完整的异常堆栈信息
        error_traceback = traceback.format_exc()
        error_message = str(e)
        # 组合错误消息和堆栈信息，但限制长度（数据库字段可能有限制）
        full_error_message = f'{error_message}\n\n堆栈跟踪:\n{error_traceback}'
        # 限制错误消息长度（Text字段通常可以存储很大，但为了安全限制在5000字符）
        max_error_length = 5000
        if len(full_error_message) > max_error_length:
            full_error_message = full_error_message[:max_error_length] + '\n... (错误信息过长，已截断)'
        
        # 记录完整的异常信息到日志
        # 使用保存的 task_name，避免访问 ORM 对象导致延迟加载问题
        logger.exception(f'任务 {task_name if task_name else (task.task_name if task else task_id)} 执行失败: {error_message}')
        logger.error(f'任务异常堆栈:\n{error_traceback}')

        # 记录错误日志
        # 注意：如果在后台线程中，使用当前会话记录错误（如果可用）
        # 如果会话不可用或已关闭，则跳过错误日志记录（避免事件循环冲突）
        try:
            # 只有在会话可用时才记录错误日志
            # 检查会话是否可用：尝试访问会话的内部属性
            session_available = False
            if session is not None:
                try:
                    # 尝试访问会话的 bind 属性来检查会话是否可用
                    _ = session.bind
                    session_available = True
                except (AttributeError, RuntimeError):
                    session_available = False
            
            if session_available:
                try:
                    # 使用保存的值，避免访问 ORM 对象
                    if task and config and task_name and config_id and api_name:
                        duration = int((datetime.now() - start_time).total_seconds())
                        
                        # 更新任务统计
                        error_task = await TushareDownloadTaskDao.get_task_detail_by_id(session, task.task_id)
                        if error_task:
                            task_model = TushareDownloadTaskModel(
                                taskId=task.task_id,
                                runCount=(error_task.run_count or 0) + 1,
                                failCount=(error_task.fail_count or 0) + 1,
                                lastRunTime=datetime.now()
                            )
                            await TushareDownloadTaskDao.edit_task_dao(session, task_model)
                            await session.commit()

                        log = TushareDownloadLog(
                            task_id=task.task_id,
                            task_name=task_name,  # 使用保存的值
                            config_id=config_id,  # 使用保存的值
                            api_name=api_name,  # 使用保存的值
                            download_date=download_date,
                            record_count=0,
                            file_path=None,
                            status='1',
                            error_message=full_error_message,
                            duration=duration,
                            create_time=datetime.now(),
                        )

                        await TushareDownloadLogDao.add_log_dao(session, log)
                        await session.commit()
                except Exception as session_error:
                    # 如果使用当前会话失败，记录但不抛出异常
                    logger.warning(f'使用当前会话记录错误日志失败: {session_error}')
            else:
                # 会话不可用，只记录到日志文件
                logger.warning('会话不可用，跳过数据库错误日志记录，错误信息已记录到日志文件')
        except Exception as log_error:
            logger.exception(f'记录错误日志失败: {log_error}')
            logger.error(f'记录错误日志异常堆栈:\n{traceback.format_exc()}')


def download_tushare_data_sync(task_id: int, download_date: str | None = None) -> None:
    """
    下载Tushare数据的同步任务函数（用于定时任务调度）
    在新线程中创建新的事件循环和数据库连接

    :param task_id: 任务ID
    :param download_date: 下载日期（YYYYMMDD格式），如果为None则使用当前日期
    :return: None
    """
    import asyncio
    from urllib.parse import quote_plus
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from config.env import DataBaseConfig
    
    # 在新线程中创建新的事件循环
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # 在新线程中创建新的数据库引擎和会话
        # 这样可以避免事件循环冲突
        async_db_url = (
            f'mysql+asyncmy://{DataBaseConfig.db_username}:{quote_plus(DataBaseConfig.db_password)}@'
            f'{DataBaseConfig.db_host}:{DataBaseConfig.db_port}/{DataBaseConfig.db_database}'
        )
        if DataBaseConfig.db_type == 'postgresql':
            async_db_url = (
                f'postgresql+asyncpg://{DataBaseConfig.db_username}:{quote_plus(DataBaseConfig.db_password)}@'
                f'{DataBaseConfig.db_host}:{DataBaseConfig.db_port}/{DataBaseConfig.db_database}'
            )
        
        # 创建新的引擎，绑定到当前线程的事件循环
        thread_engine = create_async_engine(
            async_db_url,
            echo=DataBaseConfig.db_echo,
            max_overflow=DataBaseConfig.db_max_overflow,
            pool_size=DataBaseConfig.db_pool_size,
            pool_recycle=DataBaseConfig.db_pool_recycle,
            pool_timeout=DataBaseConfig.db_pool_timeout,
        )
        ThreadSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=thread_engine)
        
        # 使用新会话运行下载任务
        async def download_with_new_session():
            async with ThreadSessionLocal() as session:
                await download_tushare_data(task_id, download_date, session=session)
        
        # 运行异步函数
        loop.run_until_complete(download_with_new_session())
        
        # 清理引擎
        loop.run_until_complete(thread_engine.dispose())
    finally:
        # 清理事件循环
        loop.close()
