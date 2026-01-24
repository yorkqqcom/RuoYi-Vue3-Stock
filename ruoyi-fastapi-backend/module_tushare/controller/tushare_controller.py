from datetime import datetime
from typing import Annotated

from fastapi import Form, Path, Query, Request, Response
from fastapi.responses import StreamingResponse
from pydantic_validation_decorator import ValidateFields
from sqlalchemy.ext.asyncio import AsyncSession

from common.annotation.log_annotation import Log
from common.aspect.db_seesion import DBSessionDependency
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.aspect.pre_auth import CurrentUserDependency, PreAuthDependency
from common.enums import BusinessType
from common.router import APIRouterPro
from common.vo import DataResponseModel, PageResponseModel, ResponseBaseModel
from module_tushare.entity.vo.tushare_vo import (
    DeleteTushareApiConfigModel,
    DeleteTushareDownloadLogModel,
    DeleteTushareDownloadTaskModel,
    EditTushareApiConfigModel,
    EditTushareDownloadTaskModel,
    TushareApiConfigModel,
    TushareApiConfigPageQueryModel,
    TushareDownloadLogPageQueryModel,
    TushareDownloadTaskModel,
    TushareDownloadTaskPageQueryModel,
)
from module_tushare.service.tushare_service import (
    TushareApiConfigService,
    TushareDownloadLogService,
    TushareDownloadTaskService,
)
from module_admin.entity.vo.user_vo import CurrentUserModel
from utils.common_util import bytes2file_response
from utils.log_util import logger
from utils.response_util import ResponseUtil

tushare_controller = APIRouterPro(
    prefix='/tushare', order_num=20, tags=['Tushare数据管理'], dependencies=[PreAuthDependency()]
)

# ==================== Tushare接口配置管理 ====================

@tushare_controller.get(
    '/apiConfig/list',
    summary='获取Tushare接口配置分页列表接口',
    description='用于获取Tushare接口配置分页列表',
    response_model=PageResponseModel[TushareApiConfigModel],
    dependencies=[UserInterfaceAuthDependency('tushare:apiConfig:list')],
)
async def get_tushare_api_config_list(
    request: Request,
    api_config_page_query: Annotated[TushareApiConfigPageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    # 获取分页数据
    api_config_page_query_result = await TushareApiConfigService.get_config_list_services(
        query_db, api_config_page_query, is_page=True
    )
    logger.info('获取成功')

    return ResponseUtil.success(model_content=api_config_page_query_result)


@tushare_controller.post(
    '/apiConfig',
    summary='新增Tushare接口配置接口',
    description='用于新增Tushare接口配置',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('tushare:apiConfig:add')],
)
@ValidateFields(validate_model='add_api_config')
@Log(title='Tushare接口配置', business_type=BusinessType.INSERT)
async def add_tushare_api_config(
    request: Request,
    add_api_config: TushareApiConfigModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    add_api_config.create_by = current_user.user.user_name
    add_api_config.create_time = datetime.now()
    add_api_config.update_by = current_user.user.user_name
    add_api_config.update_time = datetime.now()
    add_api_config_result = await TushareApiConfigService.add_config_services(query_db, add_api_config)
    logger.info(add_api_config_result.message)

    return ResponseUtil.success(msg=add_api_config_result.message)


@tushare_controller.put(
    '/apiConfig',
    summary='编辑Tushare接口配置接口',
    description='用于编辑Tushare接口配置',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('tushare:apiConfig:edit')],
)
@ValidateFields(validate_model='edit_api_config')
@Log(title='Tushare接口配置', business_type=BusinessType.UPDATE)
async def edit_tushare_api_config(
    request: Request,
    edit_api_config: EditTushareApiConfigModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    edit_api_config.update_by = current_user.user.user_name
    edit_api_config.update_time = datetime.now()
    edit_api_config_result = await TushareApiConfigService.edit_config_services(query_db, edit_api_config)
    logger.info(edit_api_config_result.message)

    return ResponseUtil.success(msg=edit_api_config_result.message)


@tushare_controller.put(
    '/apiConfig/changeStatus',
    summary='修改Tushare接口配置状态接口',
    description='用于修改Tushare接口配置状态',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('tushare:apiConfig:changeStatus')],
)
@Log(title='Tushare接口配置', business_type=BusinessType.UPDATE)
async def change_tushare_api_config_status(
    request: Request,
    change_api_config: EditTushareApiConfigModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    edit_api_config = EditTushareApiConfigModel(
        configId=change_api_config.config_id,
        status=change_api_config.status,
        updateBy=current_user.user.user_name,
        updateTime=datetime.now(),
        type='status',
    )
    edit_api_config_result = await TushareApiConfigService.edit_config_services(query_db, edit_api_config)
    logger.info(edit_api_config_result.message)

    return ResponseUtil.success(msg=edit_api_config_result.message)


@tushare_controller.delete(
    '/apiConfig/{config_ids}',
    summary='删除Tushare接口配置接口',
    description='用于删除Tushare接口配置',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('tushare:apiConfig:remove')],
)
@Log(title='Tushare接口配置', business_type=BusinessType.DELETE)
async def delete_tushare_api_config(
    request: Request,
    config_ids: Annotated[str, Path(description='需要删除的接口配置ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    delete_api_config = DeleteTushareApiConfigModel(configIds=config_ids)
    delete_api_config_result = await TushareApiConfigService.delete_config_services(query_db, delete_api_config)
    logger.info(delete_api_config_result.message)

    return ResponseUtil.success(msg=delete_api_config_result.message)


@tushare_controller.get(
    '/apiConfig/{config_id}',
    summary='获取Tushare接口配置详情接口',
    description='用于获取指定Tushare接口配置的详情信息',
    response_model=DataResponseModel[TushareApiConfigModel],
    dependencies=[UserInterfaceAuthDependency('tushare:apiConfig:query')],
)
async def query_detail_tushare_api_config(
    request: Request,
    config_id: Annotated[int, Path(description='配置ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    api_config_detail_result = await TushareApiConfigService.config_detail_services(query_db, config_id)
    logger.info(f'获取config_id为{config_id}的信息成功')

    return ResponseUtil.success(data=api_config_detail_result)


@tushare_controller.post(
    '/apiConfig/export',
    summary='导出Tushare接口配置列表接口',
    description='用于导出当前符合查询条件的Tushare接口配置列表数据',
    response_class=StreamingResponse,
    responses={
        200: {
            'description': '流式返回Tushare接口配置列表excel文件',
            'content': {
                'application/octet-stream': {},
            },
        }
    },
    dependencies=[UserInterfaceAuthDependency('tushare:apiConfig:export')],
)
@Log(title='Tushare接口配置', business_type=BusinessType.EXPORT)
async def export_tushare_api_config_list(
    request: Request,
    api_config_page_query: Annotated[TushareApiConfigPageQueryModel, Form()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    # 获取全量数据
    api_config_query_result = await TushareApiConfigService.get_config_list_services(
        query_db, api_config_page_query, is_page=False
    )
    api_config_export_result = await TushareApiConfigService.export_config_list_services(
        request, api_config_query_result
    )
    logger.info('导出成功')

    return ResponseUtil.streaming(data=bytes2file_response(api_config_export_result))


# ==================== Tushare下载任务管理 ====================

@tushare_controller.get(
    '/downloadTask/list',
    summary='获取Tushare下载任务分页列表接口',
    description='用于获取Tushare下载任务分页列表',
    response_model=PageResponseModel[TushareDownloadTaskModel],
    dependencies=[UserInterfaceAuthDependency('tushare:downloadTask:list')],
)
async def get_tushare_download_task_list(
    request: Request,
    download_task_page_query: Annotated[TushareDownloadTaskPageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    # 获取分页数据
    download_task_page_query_result = await TushareDownloadTaskService.get_task_list_services(
        query_db, download_task_page_query, is_page=True
    )
    logger.info('获取成功')

    return ResponseUtil.success(model_content=download_task_page_query_result)


@tushare_controller.post(
    '/downloadTask',
    summary='新增Tushare下载任务接口',
    description='用于新增Tushare下载任务',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('tushare:downloadTask:add')],
)
@ValidateFields(validate_model='add_download_task')
@Log(title='Tushare下载任务', business_type=BusinessType.INSERT)
async def add_tushare_download_task(
    request: Request,
    add_download_task: TushareDownloadTaskModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    add_download_task.create_by = current_user.user.user_name
    add_download_task.create_time = datetime.now()
    add_download_task.update_by = current_user.user.user_name
    add_download_task.update_time = datetime.now()
    add_download_task_result = await TushareDownloadTaskService.add_task_services(query_db, add_download_task)
    logger.info(add_download_task_result.message)

    return ResponseUtil.success(msg=add_download_task_result.message)


@tushare_controller.put(
    '/downloadTask',
    summary='编辑Tushare下载任务接口',
    description='用于编辑Tushare下载任务',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('tushare:downloadTask:edit')],
)
@ValidateFields(validate_model='edit_download_task')
@Log(title='Tushare下载任务', business_type=BusinessType.UPDATE)
async def edit_tushare_download_task(
    request: Request,
    edit_download_task: EditTushareDownloadTaskModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    edit_download_task.update_by = current_user.user.user_name
    edit_download_task.update_time = datetime.now()
    edit_download_task_result = await TushareDownloadTaskService.edit_task_services(query_db, edit_download_task)
    logger.info(edit_download_task_result.message)

    return ResponseUtil.success(msg=edit_download_task_result.message)


@tushare_controller.put(
    '/downloadTask/changeStatus',
    summary='修改Tushare下载任务状态接口',
    description='用于修改Tushare下载任务状态',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('tushare:downloadTask:changeStatus')],
)
@Log(title='Tushare下载任务', business_type=BusinessType.UPDATE)
async def change_tushare_download_task_status(
    request: Request,
    change_download_task: EditTushareDownloadTaskModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    edit_download_task = EditTushareDownloadTaskModel(
        taskId=change_download_task.task_id,
        status=change_download_task.status,
        updateBy=current_user.user.user_name,
        updateTime=datetime.now(),
        type='status',
    )
    edit_download_task_result = await TushareDownloadTaskService.edit_task_services(query_db, edit_download_task)
    logger.info(edit_download_task_result.message)

    return ResponseUtil.success(msg=edit_download_task_result.message)


@tushare_controller.delete(
    '/downloadTask/{task_ids}',
    summary='删除Tushare下载任务接口',
    description='用于删除Tushare下载任务',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('tushare:downloadTask:remove')],
)
@Log(title='Tushare下载任务', business_type=BusinessType.DELETE)
async def delete_tushare_download_task(
    request: Request,
    task_ids: Annotated[str, Path(description='需要删除的下载任务ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    delete_download_task = DeleteTushareDownloadTaskModel(taskIds=task_ids)
    delete_download_task_result = await TushareDownloadTaskService.delete_task_services(query_db, delete_download_task)
    logger.info(delete_download_task_result.message)

    return ResponseUtil.success(msg=delete_download_task_result.message)


@tushare_controller.get(
    '/downloadTask/{task_id}',
    summary='获取Tushare下载任务详情接口',
    description='用于获取指定Tushare下载任务的详情信息',
    response_model=DataResponseModel[TushareDownloadTaskModel],
    dependencies=[UserInterfaceAuthDependency('tushare:downloadTask:query')],
)
async def query_detail_tushare_download_task(
    request: Request,
    task_id: Annotated[int, Path(description='任务ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    download_task_detail_result = await TushareDownloadTaskService.task_detail_services(query_db, task_id)
    logger.info(f'获取task_id为{task_id}的信息成功')

    return ResponseUtil.success(data=download_task_detail_result)


@tushare_controller.post(
    '/downloadTask/execute/{task_id}',
    summary='执行Tushare下载任务接口',
    description='用于手动执行指定的Tushare下载任务',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('tushare:downloadTask:execute')],
)
@Log(title='Tushare下载任务', business_type=BusinessType.OTHER)
async def execute_tushare_download_task(
    request: Request,
    task_id: Annotated[int, Path(description='任务ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    execute_task_result = await TushareDownloadTaskService.execute_task_services(query_db, task_id)
    logger.info(execute_task_result.message)

    return ResponseUtil.success(msg=execute_task_result.message)


# ==================== Tushare下载日志管理 ====================

@tushare_controller.get(
    '/downloadLog/list',
    summary='获取Tushare下载日志分页列表接口',
    description='用于获取Tushare下载日志分页列表',
    response_model=PageResponseModel,
    dependencies=[UserInterfaceAuthDependency('tushare:downloadLog:list')],
)
async def get_tushare_download_log_list(
    request: Request,
    download_log_page_query: Annotated[TushareDownloadLogPageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    # 获取分页数据
    download_log_page_query_result = await TushareDownloadLogService.get_log_list_services(
        query_db, download_log_page_query, is_page=True
    )
    logger.info('获取成功')

    return ResponseUtil.success(model_content=download_log_page_query_result)


@tushare_controller.delete(
    '/downloadLog/clean',
    summary='清空Tushare下载日志接口',
    description='用于清空所有Tushare下载日志',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('tushare:downloadLog:remove')],
)
@Log(title='Tushare下载日志', business_type=BusinessType.CLEAN)
async def clear_tushare_download_log(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    clear_download_log_result = await TushareDownloadLogService.clear_log_services(query_db)
    logger.info(clear_download_log_result.message)

    return ResponseUtil.success(msg=clear_download_log_result.message)


@tushare_controller.delete(
    '/downloadLog/{log_ids}',
    summary='删除Tushare下载日志接口',
    description='用于删除Tushare下载日志',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('tushare:downloadLog:remove')],
)
@Log(title='Tushare下载日志', business_type=BusinessType.DELETE)
async def delete_tushare_download_log(
    request: Request,
    log_ids: Annotated[str, Path(description='需要删除的下载日志ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    delete_download_log = DeleteTushareDownloadLogModel(logIds=log_ids)
    delete_download_log_result = await TushareDownloadLogService.delete_log_services(query_db, delete_download_log)
    logger.info(delete_download_log_result.message)

    return ResponseUtil.success(msg=delete_download_log_result.message)
