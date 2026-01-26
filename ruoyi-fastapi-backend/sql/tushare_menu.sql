-- ----------------------------
-- Tushare数据下载模块菜单配置
-- ----------------------------

-- 主菜单：Tushare数据管理
insert into sys_menu values('2000', 'Tushare数据管理', '0', '5', 'tushare', null, '', '', 1, 0, 'M', '0', '0', '', 'guide', 'admin', sysdate(), '', null, 'Tushare数据管理目录');

-- 二级菜单：接口配置管理
insert into sys_menu values('2001', '接口配置', '2000', '1', 'apiconfig', 'tushare/apiconfig/index', '', '', 1, 0, 'C', '0', '0', 'tushare:apiConfig:list', 'list', 'admin', sysdate(), '', null, 'Tushare接口配置菜单');

-- 二级菜单：下载任务管理
insert into sys_menu values('2002', '下载任务', '2000', '2', 'downloadTask', 'tushare/downloadTask/index', '', '', 1, 0, 'C', '0', '0', 'tushare:downloadTask:list', 'job', 'admin', sysdate(), '', null, 'Tushare下载任务菜单');

-- 二级菜单：下载日志
insert into sys_menu values('2003', '下载日志', '2000', '3', 'downloadLog', 'tushare/downloadLog/index', '', '', 1, 0, 'C', '0', '0', 'tushare:downloadLog:list', 'log', 'admin', sysdate(), '', null, 'Tushare下载日志菜单');

-- 接口配置按钮
insert into sys_menu values('2100', '接口配置查询', '2001', '1', '', '', '', '', 1, 0, 'F', '0', '0', 'tushare:apiConfig:query', '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('2101', '接口配置新增', '2001', '2', '', '', '', '', 1, 0, 'F', '0', '0', 'tushare:apiConfig:add', '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('2102', '接口配置修改', '2001', '3', '', '', '', '', 1, 0, 'F', '0', '0', 'tushare:apiConfig:edit', '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('2103', '接口配置删除', '2001', '4', '', '', '', '', 1, 0, 'F', '0', '0', 'tushare:apiConfig:remove', '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('2104', '接口配置导出', '2001', '5', '', '', '', '', 1, 0, 'F', '0', '0', 'tushare:apiConfig:export', '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('2105', '接口配置状态修改', '2001', '6', '', '', '', '', 1, 0, 'F', '0', '0', 'tushare:apiConfig:changeStatus', '#', 'admin', sysdate(), '', null, '');

-- 下载任务按钮
insert into sys_menu values('2110', '下载任务查询', '2002', '1', '', '', '', '', 1, 0, 'F', '0', '0', 'tushare:downloadTask:query', '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('2111', '下载任务新增', '2002', '2', '', '', '', '', 1, 0, 'F', '0', '0', 'tushare:downloadTask:add', '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('2112', '下载任务修改', '2002', '3', '', '', '', '', 1, 0, 'F', '0', '0', 'tushare:downloadTask:edit', '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('2113', '下载任务删除', '2002', '4', '', '', '', '', 1, 0, 'F', '0', '0', 'tushare:downloadTask:remove', '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('2114', '下载任务状态修改', '2002', '5', '', '', '', '', 1, 0, 'F', '0', '0', 'tushare:downloadTask:changeStatus', '#', 'admin', sysdate(), '', null, '');

-- 下载日志按钮
insert into sys_menu values('2120', '下载日志查询', '2003', '1', '', '', '', '', 1, 0, 'F', '0', '0', 'tushare:downloadLog:list', '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('2121', '下载日志删除', '2003', '2', '', '', '', '', 1, 0, 'F', '0', '0', 'tushare:downloadLog:remove', '#', 'admin', sysdate(), '', null, '');

-- 二级菜单：流程配置管理
insert into sys_menu values('2004', '流程配置', '2000', '4', 'workflowConfig', 'tushare/workflowConfig/index', '', '', 1, 0, 'C', '0', '0', 'tushare:workflowConfig:list', 'tree', 'admin', sysdate(), '', null, 'Tushare流程配置菜单');

-- 二级菜单：流程步骤管理
insert into sys_menu values('2005', '流程步骤', '2000', '5', 'workflowStep', 'tushare/workflowStep/index', '', '', 1, 0, 'C', '0', '0', 'tushare:workflowStep:list', 'tree-table', 'admin', sysdate(), '', null, 'Tushare流程步骤菜单');

-- 流程配置按钮
insert into sys_menu values('2130', '流程配置查询', '2004', '1', '', '', '', '', 1, 0, 'F', '0', '0', 'tushare:workflowConfig:query', '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('2131', '流程配置新增', '2004', '2', '', '', '', '', 1, 0, 'F', '0', '0', 'tushare:workflowConfig:add', '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('2132', '流程配置修改', '2004', '3', '', '', '', '', 1, 0, 'F', '0', '0', 'tushare:workflowConfig:edit', '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('2133', '流程配置删除', '2004', '4', '', '', '', '', 1, 0, 'F', '0', '0', 'tushare:workflowConfig:remove', '#', 'admin', sysdate(), '', null, '');

-- 流程步骤按钮
insert into sys_menu values('2140', '流程步骤查询', '2005', '1', '', '', '', '', 1, 0, 'F', '0', '0', 'tushare:workflowStep:list', '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('2141', '流程步骤新增', '2005', '2', '', '', '', '', 1, 0, 'F', '0', '0', 'tushare:workflowStep:add', '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('2142', '流程步骤修改', '2005', '3', '', '', '', '', 1, 0, 'F', '0', '0', 'tushare:workflowStep:edit', '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('2143', '流程步骤删除', '2005', '4', '', '', '', '', 1, 0, 'F', '0', '0', 'tushare:workflowStep:remove', '#', 'admin', sysdate(), '', null, '');

-- 下载任务执行按钮（补充）
insert into sys_menu values('2115', '下载任务执行', '2002', '6', '', '', '', '', 1, 0, 'F', '0', '0', 'tushare:downloadTask:execute', '#', 'admin', sysdate(), '', null, '');
