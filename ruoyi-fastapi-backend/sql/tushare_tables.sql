-- ----------------------------
-- Tushare数据下载模块相关表
-- ----------------------------

-- ----------------------------
-- 1、Tushare接口配置表
-- ----------------------------
drop table if exists tushare_api_config;
create table tushare_api_config (
  config_id           bigint(20)      not null auto_increment    comment '配置ID',
  api_name            varchar(100)    not null                    comment '接口名称',
  api_code            varchar(100)    not null                    comment '接口代码（如：stock_basic）',
  api_desc            text                                        comment '接口描述',
  api_params          text                                        comment '接口参数（JSON格式）',
  data_fields         text                                        comment '数据字段（JSON格式，用于指定需要下载的字段）',
  primary_key_fields  text                                        comment '主键字段配置（JSON格式，为空则使用默认data_id主键）',
  status              char(1)         default '0'                 comment '状态（0正常 1停用）',
  create_by           varchar(64)     default ''                  comment '创建者',
  create_time         datetime                                     comment '创建时间',
  update_by           varchar(64)     default ''                  comment '更新者',
  update_time         datetime                                     comment '更新时间',
  remark              varchar(500)    default ''                  comment '备注信息',
  primary key (config_id),
  unique key uk_api_code (api_code)
) engine=innodb auto_increment=1 comment = 'Tushare接口配置表';

-- ----------------------------
-- 2、Tushare下载任务表
-- ----------------------------
drop table if exists tushare_download_task;
create table tushare_download_task (
  task_id             bigint(20)      not null auto_increment    comment '任务ID',
  task_name           varchar(100)    not null                    comment '任务名称',
  config_id           bigint(20)      not null                    comment '接口配置ID',
  cron_expression     varchar(255)                                comment 'cron执行表达式',
  start_date          varchar(20)                                 comment '开始日期（YYYYMMDD）',
  end_date            varchar(20)                                 comment '结束日期（YYYYMMDD）',
  task_params         text                                        comment '任务参数（JSON格式，覆盖接口默认参数）',
  save_path           varchar(500)                                 comment '保存路径',
  save_format         varchar(20)     default 'csv'              comment '保存格式（csv/excel/json）',
  save_to_db          char(1)         default '0'                 comment '是否保存到数据库（0否 1是）',
  data_table_name     varchar(100)                                comment '数据存储表名（为空则使用默认表tushare_data）',
  status              char(1)         default '0'                 comment '状态（0正常 1暂停）',
  last_run_time       datetime                                     comment '最后运行时间',
  next_run_time       datetime                                     comment '下次运行时间',
  run_count           int(11)         default 0                   comment '运行次数',
  success_count       int(11)         default 0                   comment '成功次数',
  fail_count          int(11)         default 0                   comment '失败次数',
  create_by           varchar(64)     default ''                  comment '创建者',
  create_time         datetime                                     comment '创建时间',
  update_by           varchar(64)     default ''                  comment '更新者',
  update_time         datetime                                     comment '更新时间',
  remark              varchar(500)    default ''                  comment '备注信息',
  primary key (task_id),
  unique key uk_task_name (task_name),
  key idx_config_id (config_id)
) engine=innodb auto_increment=1 comment = 'Tushare下载任务表';

-- ----------------------------
-- 3、Tushare下载日志表
-- ----------------------------
drop table if exists tushare_download_log;
create table tushare_download_log (
  log_id              bigint(20)      not null auto_increment    comment '日志ID',
  task_id             bigint(20)      not null                    comment '任务ID',
  task_name           varchar(100)    not null                    comment '任务名称',
  config_id           bigint(20)      not null                    comment '接口配置ID',
  api_name            varchar(100)    not null                    comment '接口名称',
  download_date       varchar(20)                                 comment '下载日期（YYYYMMDD）',
  record_count        int(11)         default 0                   comment '记录数',
  file_path           varchar(500)                                 comment '文件路径',
  status              char(1)         default '0'                 comment '执行状态（0成功 1失败）',
  error_message       text                                        comment '错误信息',
  duration            int(11)                                     comment '执行时长（秒）',
  create_time         datetime                                     comment '创建时间',
  primary key (log_id),
  key idx_task_id (task_id),
  key idx_config_id (config_id),
  key idx_create_time (create_time)
) engine=innodb auto_increment=1 comment = 'Tushare下载日志表';

-- ----------------------------
-- 4、Tushare数据存储表（通用表，使用JSON存储灵活数据）
-- ----------------------------
drop table if exists tushare_data;
create table tushare_data (
  data_id             bigint(20)      not null auto_increment    comment '数据ID',
  task_id             bigint(20)      not null                    comment '任务ID',
  config_id           bigint(20)      not null                    comment '接口配置ID',
  api_code          varchar(100)    not null                    comment '接口代码',
  download_date       varchar(20)                                 comment '下载日期（YYYYMMDD）',
  data_content        json                                        comment '数据内容（JSON格式）',
  create_time         datetime        default current_timestamp  comment '创建时间',
  primary key (data_id),
  key idx_task_id_data (task_id),
  key idx_config_id_data (config_id),
  key idx_api_code_data (api_code),
  key idx_download_date_data (download_date),
  key idx_create_time_data (create_time)
) engine=innodb auto_increment=1 comment = 'Tushare数据存储表（通用表）';

-- ----------------------------
-- 5、Tushare流程配置表
-- ----------------------------
drop table if exists tushare_workflow_config;
create table tushare_workflow_config (
  workflow_id          bigint(20)      not null auto_increment    comment '流程ID',
  workflow_name        varchar(100)    not null                    comment '流程名称',
  workflow_desc        text                                        comment '流程描述',
  status               char(1)         default '0'                 comment '状态（0正常 1停用）',
  create_by            varchar(64)     default ''                  comment '创建者',
  create_time          datetime                                     comment '创建时间',
  update_by            varchar(64)     default ''                  comment '更新者',
  update_time          datetime                                     comment '更新时间',
  remark               varchar(500)    default ''                  comment '备注信息',
  primary key (workflow_id),
  unique key uk_workflow_name (workflow_name)
) engine=innodb auto_increment=1 comment = 'Tushare流程配置表';

-- ----------------------------
-- 6、Tushare流程步骤表
-- ----------------------------
drop table if exists tushare_workflow_step;
create table tushare_workflow_step (
  step_id              bigint(20)      not null auto_increment    comment '步骤ID',
  workflow_id          bigint(20)      not null                    comment '流程ID',
  step_order           int(11)         not null                    comment '步骤顺序（从1开始）',
  step_name            varchar(100)    not null                    comment '步骤名称',
  config_id            bigint(20)      not null                    comment '接口配置ID',
  step_params          text                                        comment '步骤参数（JSON格式，可从前一步获取数据）',
  condition_expr       text                                        comment '执行条件（JSON格式，可选）',
  status               char(1)         default '0'                 comment '状态（0正常 1停用）',
  create_by            varchar(64)     default ''                  comment '创建者',
  create_time          datetime                                     comment '创建时间',
  update_by            varchar(64)     default ''                  comment '更新者',
  update_time          datetime                                     comment '更新时间',
  remark               varchar(500)    default ''                  comment '备注信息',
  primary key (step_id),
  key idx_workflow_id (workflow_id),
  key idx_config_id (config_id),
  unique key uk_workflow_step_order (workflow_id, step_order)
) engine=innodb auto_increment=1 comment = 'Tushare流程步骤表';

-- ----------------------------
-- 修改下载任务表，添加流程配置支持
-- ----------------------------
alter table tushare_download_task add column workflow_id bigint(20) comment '流程配置ID（如果存在则执行流程，否则执行单个接口）';
create index idx_workflow_id_task on tushare_download_task(workflow_id);

-- ----------------------------
-- 修改下载任务表，添加任务类型字段
-- ----------------------------
alter table tushare_download_task add column task_type varchar(20) default 'single' comment '任务类型（single:单个接口 workflow:流程配置）';
create index idx_task_type on tushare_download_task(task_type);

-- ----------------------------
-- 修改下载任务表，允许config_id为空（流程配置模式下可以为空）
-- ----------------------------
alter table tushare_download_task modify column config_id bigint(20) null comment '接口配置ID';

-- ----------------------------
-- 扩展流程步骤表，添加可视化编辑器支持字段
-- ----------------------------
alter table tushare_workflow_step add column position_x int(11) comment '节点X坐标（用于可视化布局）';
alter table tushare_workflow_step add column position_y int(11) comment '节点Y坐标（用于可视化布局）';
alter table tushare_workflow_step add column node_type varchar(20) default 'task' comment '节点类型（start/end/task）';
alter table tushare_workflow_step add column source_step_ids text comment '前置步骤ID列表（JSON格式，支持多个前置节点）';
alter table tushare_workflow_step add column target_step_ids text comment '后置步骤ID列表（JSON格式，支持多个后置节点）';
alter table tushare_workflow_step add column layout_data json comment '完整的布局数据（JSON格式，存储节点位置、连接线等可视化信息）';
alter table tushare_workflow_step add column data_table_name varchar(100) comment '数据存储表名（为空则使用任务配置的表名或默认表名）';

-- ----------------------------
-- 扩展流程步骤表，添加遍历模式和数据更新方式字段
-- ----------------------------
alter table tushare_workflow_step add column loop_mode char(1) default '0' comment '遍历模式（0否 1是，开启后所有变量参数都会遍历）';
alter table tushare_workflow_step add column update_mode char(1) default '0' comment '数据更新方式（0仅插入 1忽略重复 2存在则更新 3先删除再插入）';
alter table tushare_workflow_step add column unique_key_fields text comment '唯一键字段配置（JSON格式，为空则自动检测）';
