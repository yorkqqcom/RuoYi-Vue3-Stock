from typing import Any

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from common.constant import CommonConstant
from common.vo import CrudResponseModel
from exceptions.exception import ServiceException
from module_tushare.dao.tushare_dao import (
    TushareApiConfigDao,
    TushareDownloadLogDao,
    TushareDownloadTaskDao,
)
from module_tushare.entity.do.tushare_do import TushareDownloadLog
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
from utils.common_util import CamelCaseUtil
from utils.excel_util import ExcelUtil
from utils.log_util import logger


class TushareApiConfigService:
    """
    Tushare接口配置管理模块服务层
    """

    @classmethod
    async def get_config_list_services(
        cls, query_db: AsyncSession, query_object: TushareApiConfigPageQueryModel, is_page: bool = False
    ) -> Any:
        """
        获取接口配置列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 接口配置列表信息对象
        """
        config_list_result = await TushareApiConfigDao.get_config_list(query_db, query_object, is_page)

        return config_list_result

    @classmethod
    async def check_config_unique_services(
        cls, query_db: AsyncSession, page_object: TushareApiConfigModel
    ) -> bool:
        """
        校验接口配置是否存在service

        :param query_db: orm对象
        :param page_object: 接口配置对象
        :return: 校验结果
        """
        config_id = -1 if page_object.config_id is None else page_object.config_id
        config = await TushareApiConfigDao.get_config_detail_by_info(query_db, page_object)
        if config and config.config_id != config_id:
            return CommonConstant.NOT_UNIQUE
        return CommonConstant.UNIQUE

    @classmethod
    async def add_config_services(
        cls, query_db: AsyncSession, page_object: TushareApiConfigModel
    ) -> CrudResponseModel:
        """
        新增接口配置信息service

        :param query_db: orm对象
        :param page_object: 新增接口配置对象
        :return: 新增接口配置校验结果
        """
        if not await cls.check_config_unique_services(query_db, page_object):
            raise ServiceException(message=f'新增接口配置{page_object.api_name}失败，接口代码已存在')
        try:
            add_config = await TushareApiConfigDao.add_config_dao(query_db, page_object)
            await query_db.commit()
            result = {'is_success': True, 'message': '新增成功'}
        except Exception as e:
            await query_db.rollback()
            raise e

        return CrudResponseModel(**result)

    @classmethod
    def _deal_edit_config(cls, page_object: EditTushareApiConfigModel, edit_config: dict[str, Any]) -> None:
        """
        处理编辑接口配置字典

        :param page_object: 编辑接口配置对象
        :param edit_config: 编辑接口配置字典
        """
        if page_object.type == 'status':
            edit_config['status'] = page_object.status
        else:
            edit_config['api_name'] = page_object.api_name
            edit_config['api_code'] = page_object.api_code
            edit_config['api_desc'] = page_object.api_desc
            edit_config['api_params'] = page_object.api_params
            edit_config['data_fields'] = page_object.data_fields
            edit_config['status'] = page_object.status
            edit_config['remark'] = page_object.remark

    @classmethod
    async def edit_config_services(
        cls, query_db: AsyncSession, page_object: EditTushareApiConfigModel
    ) -> CrudResponseModel:
        """
        编辑接口配置信息service

        :param query_db: orm对象
        :param page_object: 编辑接口配置对象
        :return: 编辑接口配置校验结果
        """
        old_config = await TushareApiConfigDao.get_config_detail_by_id(query_db, page_object.config_id)
        if not old_config:
            raise ServiceException(message='接口配置不存在')
        if page_object.type != 'status':
            check_config = TushareApiConfigModel(
                config_id=page_object.config_id,
                api_code=page_object.api_code,
            )
            if not await cls.check_config_unique_services(query_db, check_config):
                raise ServiceException(message=f'编辑接口配置{page_object.api_name}失败，接口代码已存在')
        try:
            edit_config_dict = page_object.model_dump(exclude={'config_id', 'type'}, exclude_none=True)
            cls._deal_edit_config(page_object, edit_config_dict)
            await TushareApiConfigDao.edit_config_dao(query_db, TushareApiConfigModel(**edit_config_dict))
            await query_db.commit()
            result = {'is_success': True, 'message': '编辑成功'}
        except Exception as e:
            await query_db.rollback()
            raise e

        return CrudResponseModel(**result)

    @classmethod
    async def delete_config_services(
        cls, query_db: AsyncSession, page_object: DeleteTushareApiConfigModel
    ) -> CrudResponseModel:
        """
        删除接口配置信息service

        :param query_db: orm对象
        :param page_object: 删除接口配置对象
        :return: 删除接口配置校验结果
        """
        config_ids = [int(config_id) for config_id in page_object.config_ids.split(',')]
        try:
            await TushareApiConfigDao.delete_config_dao(query_db, config_ids)
            await query_db.commit()
            result = {'is_success': True, 'message': '删除成功'}
        except Exception as e:
            await query_db.rollback()
            raise e

        return CrudResponseModel(**result)

    @classmethod
    async def config_detail_services(cls, query_db: AsyncSession, config_id: int) -> TushareApiConfigModel:
        """
        获取接口配置详细信息service

        :param query_db: orm对象
        :param config_id: 接口配置id
        :return: 接口配置详细信息对象
        """
        config = await TushareApiConfigDao.get_config_detail_by_id(query_db, config_id)
        result = TushareApiConfigModel(**CamelCaseUtil.transform_result(config)) if config else TushareApiConfigModel()

        return result

    @classmethod
    async def export_config_list_services(cls, request: Request, config_list: list) -> bytes:
        """
        导出接口配置列表信息service

        :param request: Request对象
        :param config_list: 接口配置列表信息
        :return: 接口配置列表excel文件流
        """
        excel_data = [
            ['配置ID', '接口名称', '接口代码', '接口描述', '状态', '创建时间', '备注'],
        ]
        for config_item in config_list:
            excel_data.append(
                [
                    config_item.get('config_id'),
                    config_item.get('api_name'),
                    config_item.get('api_code'),
                    config_item.get('api_desc'),
                    '正常' if config_item.get('status') == '0' else '停用',
                    config_item.get('create_time'),
                    config_item.get('remark'),
                ]
            )
        excel_stream = ExcelUtil.create_excel(excel_data=excel_data, sheet_name='接口配置列表')

        return excel_stream


class TushareDownloadTaskService:
    """
    Tushare下载任务管理模块服务层
    """

    @classmethod
    async def get_task_list_services(
        cls, query_db: AsyncSession, query_object: TushareDownloadTaskPageQueryModel, is_page: bool = False
    ) -> Any:
        """
        获取下载任务列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 下载任务列表信息对象
        """
        task_list_result = await TushareDownloadTaskDao.get_task_list(query_db, query_object, is_page)

        return task_list_result

    @classmethod
    async def check_task_unique_services(
        cls, query_db: AsyncSession, page_object: TushareDownloadTaskModel
    ) -> bool:
        """
        校验下载任务是否存在service

        :param query_db: orm对象
        :param page_object: 下载任务对象
        :return: 校验结果
        """
        task_id = -1 if page_object.task_id is None else page_object.task_id
        task = await TushareDownloadTaskDao.get_task_detail_by_info(query_db, page_object)
        if task and task.task_id != task_id:
            return CommonConstant.NOT_UNIQUE
        return CommonConstant.UNIQUE

    @classmethod
    async def add_task_services(
        cls, query_db: AsyncSession, page_object: TushareDownloadTaskModel
    ) -> CrudResponseModel:
        """
        新增下载任务信息service

        :param query_db: orm对象
        :param page_object: 新增下载任务对象
        :return: 新增下载任务校验结果
        """
        if not await cls.check_task_unique_services(query_db, page_object):
            raise ServiceException(message=f'新增下载任务{page_object.task_name}失败，任务名称已存在')
        try:
            # 处理cron_expression：空字符串转换为None，使用by_alias=False确保使用snake_case键名
            task_dict = page_object.model_dump(exclude={'task_id'}, by_alias=False)
            if 'cron_expression' in task_dict:
                task_dict['cron_expression'] = (
                    task_dict['cron_expression'].strip()
                    if task_dict['cron_expression'] and task_dict['cron_expression'].strip()
                    else None
                )
            add_task = await TushareDownloadTaskDao.add_task_dao(query_db, TushareDownloadTaskModel(**task_dict))
            await query_db.commit()
            result = {'is_success': True, 'message': '新增成功'}
        except Exception as e:
            await query_db.rollback()
            raise e

        return CrudResponseModel(**result)

    @classmethod
    def _deal_edit_task(cls, page_object: EditTushareDownloadTaskModel, edit_task: dict[str, Any]) -> None:
        """
        处理编辑下载任务字典

        :param page_object: 编辑下载任务对象
        :param edit_task: 编辑下载任务字典
        """
        logger.info(f'[_deal_edit_task] 开始处理，type: {page_object.type}')
        logger.info(f'[_deal_edit_task] page_object.cron_expression: {page_object.cron_expression}, 类型: {type(page_object.cron_expression)}')
        
        if page_object.type == 'status':
            edit_task['status'] = page_object.status
            logger.info(f'[_deal_edit_task] 只更新状态: {page_object.status}')
        else:
            edit_task['task_name'] = page_object.task_name
            edit_task['config_id'] = page_object.config_id
            # 处理cron_expression：空字符串转换为None
            original_cron = page_object.cron_expression
            if original_cron and isinstance(original_cron, str) and original_cron.strip():
                edit_task['cron_expression'] = original_cron.strip()
                logger.info(f'[_deal_edit_task] cron_expression处理: "{original_cron}" -> "{edit_task["cron_expression"]}"')
            else:
                edit_task['cron_expression'] = None
                logger.info(f'[_deal_edit_task] cron_expression处理: "{original_cron}" -> None')
            
            edit_task['start_date'] = page_object.start_date
            edit_task['end_date'] = page_object.end_date
            edit_task['task_params'] = page_object.task_params
            edit_task['save_path'] = page_object.save_path
            edit_task['save_format'] = page_object.save_format
            edit_task['save_to_db'] = page_object.save_to_db
            edit_task['data_table_name'] = page_object.data_table_name
            edit_task['status'] = page_object.status
            edit_task['remark'] = page_object.remark
            
            logger.info(f'[_deal_edit_task] 处理完成，cron_expression最终值: {edit_task.get("cron_expression")}')

    @classmethod
    async def edit_task_services(
        cls, query_db: AsyncSession, page_object: EditTushareDownloadTaskModel
    ) -> CrudResponseModel:
        """
        编辑下载任务信息service

        :param query_db: orm对象
        :param page_object: 编辑下载任务对象
        :return: 编辑下载任务校验结果
        """
        logger.info(f'[编辑任务] 开始编辑任务，task_id: {page_object.task_id}, type: {page_object.type}')
        logger.info(f'[编辑任务] 接收到的数据: {page_object.model_dump(by_alias=True)}')
        
        old_task = await TushareDownloadTaskDao.get_task_detail_by_id(query_db, page_object.task_id)
        if not old_task:
            logger.error(f'[编辑任务] 任务不存在，task_id: {page_object.task_id}')
            raise ServiceException(message='下载任务不存在')
        
        logger.info(f'[编辑任务] 原始任务数据: task_name={old_task.task_name}, cron_expression={old_task.cron_expression}')
        
        if page_object.type != 'status':
            check_task = TushareDownloadTaskModel(
                task_id=page_object.task_id,
                task_name=page_object.task_name,
            )
            if not await cls.check_task_unique_services(query_db, check_task):
                logger.error(f'[编辑任务] 任务名称已存在: {page_object.task_name}')
                raise ServiceException(message=f'编辑下载任务{page_object.task_name}失败，任务名称已存在')
        try:
            # 先获取所有字段（包括None值），使用by_alias=False确保使用snake_case键名
            # 排除不应该在编辑时更新的字段：统计字段和创建相关字段
            edit_task_dict = page_object.model_dump(
                exclude={
                    'task_id', 'type',
                    'last_run_time', 'next_run_time', 'run_count', 'success_count', 'fail_count',
                    'create_by', 'create_time'
                },
                exclude_none=False,
                by_alias=False
            )
            logger.info(f'[编辑任务] model_dump后的字典: {edit_task_dict}')
            
            cls._deal_edit_task(page_object, edit_task_dict)
            logger.info(f'[编辑任务] _deal_edit_task处理后的字典: {edit_task_dict}')
            
            # 添加 update_by 和 update_time 到字典中
            edit_task_dict['update_by'] = page_object.update_by
            edit_task_dict['update_time'] = page_object.update_time
            # 添加 task_id 用于更新条件
            edit_task_dict['task_id'] = page_object.task_id
            logger.info(f'[编辑任务] 最终更新字典: {edit_task_dict}')
            logger.info(f'[编辑任务] 准备直接使用字典更新，task_id: {page_object.task_id}')
            
            # 直接使用字典更新，避免模型转换时的字段名问题
            result_id = await TushareDownloadTaskDao.edit_task_dao(query_db, page_object.task_id, edit_task_dict)
            logger.info(f'[编辑任务] DAO更新返回的task_id: {result_id}')
            
            await query_db.commit()
            logger.info(f'[编辑任务] 事务提交成功')
            
            # 验证更新结果
            updated_task = await TushareDownloadTaskDao.get_task_detail_by_id(query_db, page_object.task_id)
            if updated_task:
                logger.info(f'[编辑任务] 更新后的任务数据: task_name={updated_task.task_name}, cron_expression={updated_task.cron_expression}')
            else:
                logger.warning(f'[编辑任务] 更新后无法获取任务数据，task_id: {page_object.task_id}')
            
            result = {'is_success': True, 'message': '编辑成功'}
        except Exception as e:
            logger.exception(f'[编辑任务] 编辑任务失败，task_id: {page_object.task_id}, 错误: {str(e)}')
            await query_db.rollback()
            raise e

        return CrudResponseModel(**result)

    @classmethod
    async def delete_task_services(
        cls, query_db: AsyncSession, page_object: DeleteTushareDownloadTaskModel
    ) -> CrudResponseModel:
        """
        删除下载任务信息service

        :param query_db: orm对象
        :param page_object: 删除下载任务对象
        :return: 删除下载任务校验结果
        """
        task_ids = [int(task_id) for task_id in page_object.task_ids.split(',')]
        try:
            await TushareDownloadTaskDao.delete_task_dao(query_db, task_ids)
            await query_db.commit()
            result = {'is_success': True, 'message': '删除成功'}
        except Exception as e:
            await query_db.rollback()
            raise e

        return CrudResponseModel(**result)

    @classmethod
    async def task_detail_services(cls, query_db: AsyncSession, task_id: int) -> TushareDownloadTaskModel:
        """
        获取下载任务详细信息service

        :param query_db: orm对象
        :param task_id: 下载任务id
        :return: 下载任务详细信息对象
        """
        task = await TushareDownloadTaskDao.get_task_detail_by_id(query_db, task_id)
        result = (
            TushareDownloadTaskModel(**CamelCaseUtil.transform_result(task)) if task else TushareDownloadTaskModel()
        )

        return result

    @classmethod
    async def execute_task_services(cls, query_db: AsyncSession, task_id: int) -> CrudResponseModel:
        """
        执行下载任务service

        :param query_db: orm对象
        :param task_id: 下载任务id
        :return: 执行任务结果
        """
        from fastapi import BackgroundTasks
        from module_tushare.task.tushare_download_task import download_tushare_data_sync
        
        # 检查任务是否存在
        task = await TushareDownloadTaskDao.get_task_detail_by_id(query_db, task_id)
        if not task:
            raise ServiceException(message='下载任务不存在')
        
        if task.status != '0':
            raise ServiceException(message='任务已暂停，无法执行')
        
        try:
            # 异步执行任务（使用同步包装函数，在后台线程中执行）
            import threading
            import traceback
            
            def run_task():
                try:
                    download_tushare_data_sync(task_id)
                except Exception as e:
                    error_traceback = traceback.format_exc()
                    logger.exception(f'执行任务 {task_id} 失败: {e}')
                    logger.error(f'任务执行异常堆栈:\n{error_traceback}')
            
            # 在后台线程中执行任务
            thread = threading.Thread(target=run_task, daemon=True)
            thread.start()
            
            result = {'is_success': True, 'message': '任务已提交执行，请稍后查看执行日志'}
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            logger.exception(f'提交任务执行失败: {e}')
            logger.error(f'提交任务异常堆栈:\n{error_traceback}')
            raise ServiceException(message=f'提交任务执行失败: {str(e)}')

        return CrudResponseModel(**result)


class TushareDownloadLogService:
    """
    Tushare下载日志管理模块服务层
    """

    @classmethod
    async def get_log_list_services(
        cls, query_db: AsyncSession, query_object: TushareDownloadLogPageQueryModel, is_page: bool = False
    ) -> Any:
        """
        获取下载日志列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 下载日志列表信息对象
        """
        log_list_result = await TushareDownloadLogDao.get_log_list(query_db, query_object, is_page)

        return log_list_result

    @classmethod
    async def add_log_services(cls, query_db: AsyncSession, log: TushareDownloadLog) -> CrudResponseModel:
        """
        新增下载日志信息service

        :param query_db: orm对象
        :param log: 下载日志对象
        :return: 新增下载日志校验结果
        """
        try:
            add_log = await TushareDownloadLogDao.add_log_dao(query_db, log)
            await query_db.commit()
            result = {'is_success': True, 'message': '新增成功'}
        except Exception as e:
            await query_db.rollback()
            raise e

        return CrudResponseModel(**result)

    @classmethod
    async def delete_log_services(
        cls, query_db: AsyncSession, page_object: DeleteTushareDownloadLogModel
    ) -> CrudResponseModel:
        """
        删除下载日志信息service

        :param query_db: orm对象
        :param page_object: 删除下载日志对象
        :return: 删除下载日志校验结果
        """
        log_ids = [int(log_id) for log_id in page_object.log_ids.split(',')]
        try:
            await TushareDownloadLogDao.delete_log_dao(query_db, log_ids)
            await query_db.commit()
            result = {'is_success': True, 'message': '删除成功'}
        except Exception as e:
            await query_db.rollback()
            raise e

        return CrudResponseModel(**result)

    @classmethod
    async def clear_log_services(cls, query_db: AsyncSession) -> CrudResponseModel:
        """
        清空下载日志信息service

        :param query_db: orm对象
        :return: 清空下载日志校验结果
        """
        try:
            await TushareDownloadLogDao.clear_log_dao(query_db)
            await query_db.commit()
            result = {'is_success': True, 'message': '清空成功'}
        except Exception as e:
            await query_db.rollback()
            raise e

        return CrudResponseModel(**result)
