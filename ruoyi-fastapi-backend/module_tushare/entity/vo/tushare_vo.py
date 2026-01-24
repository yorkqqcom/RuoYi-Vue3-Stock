from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank, Size


class TushareApiConfigModel(BaseModel):
    """
    Tushare接口配置表对应pydantic模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    config_id: int | None = Field(default=None, description='配置ID')
    api_name: str | None = Field(default=None, description='接口名称')
    api_code: str | None = Field(default=None, description='接口代码')
    api_desc: str | None = Field(default=None, description='接口描述')
    api_params: str | None = Field(default=None, description='接口参数（JSON格式）')
    data_fields: str | None = Field(default=None, description='数据字段（JSON格式）')
    status: Literal['0', '1'] | None = Field(default=None, description='状态（0正常 1停用）')
    create_by: str | None = Field(default=None, description='创建者')
    create_time: datetime | None = Field(default=None, description='创建时间')
    update_by: str | None = Field(default=None, description='更新者')
    update_time: datetime | None = Field(default=None, description='更新时间')
    remark: str | None = Field(default=None, description='备注信息')

    @NotBlank(field_name='api_name', message='接口名称不能为空')
    @Size(field_name='api_name', min_length=0, max_length=100, message='接口名称长度不能超过100个字符')
    def get_api_name(self) -> str | None:
        return self.api_name

    @NotBlank(field_name='api_code', message='接口代码不能为空')
    @Size(field_name='api_code', min_length=0, max_length=100, message='接口代码长度不能超过100个字符')
    def get_api_code(self) -> str | None:
        return self.api_code

    def validate_fields(self) -> None:
        self.get_api_name()
        self.get_api_code()


class TushareApiConfigQueryModel(TushareApiConfigModel):
    """
    Tushare接口配置查询模型
    """

    begin_time: str | None = Field(default=None, description='开始时间')
    end_time: str | None = Field(default=None, description='结束时间')


class TushareApiConfigPageQueryModel(TushareApiConfigQueryModel):
    """
    Tushare接口配置分页查询模型
    """

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


class EditTushareApiConfigModel(TushareApiConfigModel):
    """
    编辑Tushare接口配置模型
    """

    type: str | None = Field(default=None, description='操作类型')


class DeleteTushareApiConfigModel(BaseModel):
    """
    删除Tushare接口配置模型
    """

    config_ids: str = Field(description='需要删除的配置ID')


class TushareDownloadTaskModel(BaseModel):
    """
    Tushare下载任务表对应pydantic模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    task_id: int | None = Field(default=None, description='任务ID')
    task_name: str | None = Field(default=None, description='任务名称')
    config_id: int | None = Field(default=None, description='接口配置ID')
    cron_expression: str | None = Field(default=None, description='cron执行表达式')
    start_date: str | None = Field(default=None, description='开始日期')
    end_date: str | None = Field(default=None, description='结束日期')
    task_params: str | None = Field(default=None, description='任务参数（JSON格式）')
    save_path: str | None = Field(default=None, description='保存路径')
    save_format: str | None = Field(default=None, description='保存格式')
    save_to_db: Literal['0', '1'] | None = Field(default=None, description='是否保存到数据库（0否 1是）')
    data_table_name: str | None = Field(default=None, description='数据存储表名（为空则使用默认表tushare_data）')
    status: Literal['0', '1'] | None = Field(default=None, description='状态（0正常 1暂停）')
    last_run_time: datetime | None = Field(default=None, description='最后运行时间')
    next_run_time: datetime | None = Field(default=None, description='下次运行时间')
    run_count: int | None = Field(default=None, description='运行次数')
    success_count: int | None = Field(default=None, description='成功次数')
    fail_count: int | None = Field(default=None, description='失败次数')
    create_by: str | None = Field(default=None, description='创建者')
    create_time: datetime | None = Field(default=None, description='创建时间')
    update_by: str | None = Field(default=None, description='更新者')
    update_time: datetime | None = Field(default=None, description='更新时间')
    remark: str | None = Field(default=None, description='备注信息')

    @NotBlank(field_name='task_name', message='任务名称不能为空')
    @Size(field_name='task_name', min_length=0, max_length=100, message='任务名称长度不能超过100个字符')
    def get_task_name(self) -> str | None:
        return self.task_name

    @NotBlank(field_name='config_id', message='接口配置ID不能为空')
    def get_config_id(self) -> int | None:
        return self.config_id

    def validate_fields(self) -> None:
        self.get_task_name()
        self.get_config_id()


class TushareDownloadTaskQueryModel(TushareDownloadTaskModel):
    """
    Tushare下载任务查询模型
    """

    begin_time: str | None = Field(default=None, description='开始时间')
    end_time: str | None = Field(default=None, description='结束时间')


class TushareDownloadTaskPageQueryModel(TushareDownloadTaskQueryModel):
    """
    Tushare下载任务分页查询模型
    """

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


class EditTushareDownloadTaskModel(TushareDownloadTaskModel):
    """
    编辑Tushare下载任务模型
    """

    type: str | None = Field(default=None, description='操作类型')


class DeleteTushareDownloadTaskModel(BaseModel):
    """
    删除Tushare下载任务模型
    """

    task_ids: str = Field(description='需要删除的任务ID')


class TushareDownloadLogModel(BaseModel):
    """
    Tushare下载日志表对应pydantic模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    log_id: int | None = Field(default=None, description='日志ID')
    task_id: int | None = Field(default=None, description='任务ID')
    task_name: str | None = Field(default=None, description='任务名称')
    config_id: int | None = Field(default=None, description='接口配置ID')
    api_name: str | None = Field(default=None, description='接口名称')
    download_date: str | None = Field(default=None, description='下载日期')
    record_count: int | None = Field(default=None, description='记录数')
    file_path: str | None = Field(default=None, description='文件路径')
    status: Literal['0', '1'] | None = Field(default=None, description='执行状态（0成功 1失败）')
    error_message: str | None = Field(default=None, description='错误信息')
    duration: int | None = Field(default=None, description='执行时长（秒）')
    create_time: datetime | None = Field(default=None, description='创建时间')


class TushareDownloadLogQueryModel(TushareDownloadLogModel):
    """
    Tushare下载日志查询模型
    """

    begin_time: str | None = Field(default=None, description='开始时间')
    end_time: str | None = Field(default=None, description='结束时间')


class TushareDownloadLogPageQueryModel(TushareDownloadLogQueryModel):
    """
    Tushare下载日志分页查询模型
    """

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


class DeleteTushareDownloadLogModel(BaseModel):
    """
    删除Tushare下载日志模型
    """

    log_ids: str = Field(description='需要删除的日志ID')


class TushareDataModel(BaseModel):
    """
    Tushare数据存储表对应pydantic模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    data_id: int | None = Field(default=None, description='数据ID')
    task_id: int | None = Field(default=None, description='任务ID')
    config_id: int | None = Field(default=None, description='接口配置ID')
    api_code: str | None = Field(default=None, description='接口代码')
    download_date: str | None = Field(default=None, description='下载日期（YYYYMMDD）')
    data_content: dict | list | None = Field(default=None, description='数据内容（JSON格式）')
    create_time: datetime | None = Field(default=None, description='创建时间')


class TushareDataQueryModel(TushareDataModel):
    begin_time: str | None = Field(default=None, description='开始时间')
    end_time: str | None = Field(default=None, description='结束时间')


class TushareDataPageQueryModel(TushareDataQueryModel):
    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


class DeleteTushareDataModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    data_ids: str = Field(description='需要删除的数据ID')
