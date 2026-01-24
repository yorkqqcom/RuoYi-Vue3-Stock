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
