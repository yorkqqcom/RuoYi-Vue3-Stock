from datetime import datetime

from sqlalchemy import CHAR, BigInteger, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON

from config.database import Base
from config.env import DataBaseConfig


class TushareApiConfig(Base):
    """
    Tushare接口配置表
    """

    __tablename__ = 'tushare_api_config'
    __table_args__ = {'comment': 'Tushare接口配置表'}

    config_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='配置ID')
    api_name = Column(String(100), nullable=False, comment='接口名称')
    api_code = Column(String(100), nullable=False, comment='接口代码（如：stock_basic）')
    api_desc = Column(Text, nullable=True, comment='接口描述')
    api_params = Column(Text, nullable=True, comment='接口参数（JSON格式）')
    data_fields = Column(Text, nullable=True, comment='数据字段（JSON格式，用于指定需要下载的字段）')
    status = Column(CHAR(1), nullable=True, server_default='0', comment='状态（0正常 1停用）')
    create_by = Column(String(64), nullable=True, server_default="''", comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now(), comment='创建时间')
    update_by = Column(String(64), nullable=True, server_default="''", comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now(), comment='更新时间')
    remark = Column(String(500), nullable=True, server_default="''", comment='备注信息')


class TushareDownloadTask(Base):
    """
    Tushare下载任务表
    """

    __tablename__ = 'tushare_download_task'
    __table_args__ = {'comment': 'Tushare下载任务表'}

    task_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='任务ID')
    task_name = Column(String(100), nullable=False, comment='任务名称')
    config_id = Column(BigInteger, nullable=False, comment='接口配置ID')
    cron_expression = Column(String(255), nullable=True, comment='cron执行表达式')
    start_date = Column(String(20), nullable=True, comment='开始日期（YYYYMMDD）')
    end_date = Column(String(20), nullable=True, comment='结束日期（YYYYMMDD）')
    task_params = Column(Text, nullable=True, comment='任务参数（JSON格式，覆盖接口默认参数）')
    save_path = Column(String(500), nullable=True, comment='保存路径')
    save_format = Column(String(20), nullable=True, server_default='csv', comment='保存格式（csv/excel/json）')
    save_to_db = Column(CHAR(1), nullable=True, server_default='0', comment='是否保存到数据库（0否 1是）')
    data_table_name = Column(String(100), nullable=True, comment='数据存储表名（为空则使用默认表tushare_data）')
    status = Column(CHAR(1), nullable=True, server_default='0', comment='状态（0正常 1暂停）')
    last_run_time = Column(DateTime, nullable=True, comment='最后运行时间')
    next_run_time = Column(DateTime, nullable=True, comment='下次运行时间')
    run_count = Column(Integer, nullable=True, server_default='0', comment='运行次数')
    success_count = Column(Integer, nullable=True, server_default='0', comment='成功次数')
    fail_count = Column(Integer, nullable=True, server_default='0', comment='失败次数')
    create_by = Column(String(64), nullable=True, server_default="''", comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now(), comment='创建时间')
    update_by = Column(String(64), nullable=True, server_default="''", comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now(), comment='更新时间')
    remark = Column(String(500), nullable=True, server_default="''", comment='备注信息')


class TushareDownloadLog(Base):
    """
    Tushare下载日志表
    """

    __tablename__ = 'tushare_download_log'
    __table_args__ = {'comment': 'Tushare下载日志表'}

    log_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='日志ID')
    task_id = Column(BigInteger, nullable=False, comment='任务ID')
    task_name = Column(String(100), nullable=False, comment='任务名称')
    config_id = Column(BigInteger, nullable=False, comment='接口配置ID')
    api_name = Column(String(100), nullable=False, comment='接口名称')
    download_date = Column(String(20), nullable=True, comment='下载日期（YYYYMMDD）')
    record_count = Column(Integer, nullable=True, server_default='0', comment='记录数')
    file_path = Column(String(500), nullable=True, comment='文件路径')
    status = Column(CHAR(1), nullable=True, server_default='0', comment='执行状态（0成功 1失败）')
    error_message = Column(Text, nullable=True, comment='错误信息')
    duration = Column(Integer, nullable=True, comment='执行时长（秒）')
    create_time = Column(DateTime, nullable=True, default=datetime.now(), comment='创建时间')


class TushareData(Base):
    """
    Tushare数据存储表（通用表）
    """

    __tablename__ = 'tushare_data'
    __table_args__ = {'comment': 'Tushare数据存储表（通用表）'}

    data_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='数据ID')
    task_id = Column(BigInteger, nullable=False, comment='任务ID')
    config_id = Column(BigInteger, nullable=False, comment='接口配置ID')
    api_code = Column(String(100), nullable=False, comment='接口代码')
    download_date = Column(String(20), nullable=True, comment='下载日期（YYYYMMDD）')
    # 根据数据库类型选择 JSON 或 JSONB
    if DataBaseConfig.db_type == 'postgresql':
        data_content = Column(JSONB, nullable=True, comment='数据内容（JSONB格式）')
    else:
        data_content = Column(JSON, nullable=True, comment='数据内容（JSON格式）')
    create_time = Column(DateTime, nullable=True, default=datetime.now(), comment='创建时间')
