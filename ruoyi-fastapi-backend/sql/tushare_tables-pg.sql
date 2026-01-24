-- ----------------------------
-- Tushare数据下载模块相关表（PostgreSQL版本）
-- ----------------------------

-- ----------------------------
-- 1、Tushare接口配置表
-- ----------------------------
drop table if exists tushare_api_config;
create table tushare_api_config (
  config_id           bigserial      not null,
  api_name            varchar(100)   not null,
  api_code            varchar(100)   not null,
  api_desc            text,
  api_params          text,
  data_fields         text,
  status              char(1)        default '0',
  create_by           varchar(64)     default '',
  create_time         timestamp(0),
  update_by           varchar(64)     default '',
  update_time         timestamp(0),
  remark              varchar(500)   default '',
  primary key (config_id),
  constraint uk_api_code unique (api_code)
);
comment on column tushare_api_config.config_id is '配置ID';
comment on column tushare_api_config.api_name is '接口名称';
comment on column tushare_api_config.api_code is '接口代码（如：stock_basic）';
comment on column tushare_api_config.api_desc is '接口描述';
comment on column tushare_api_config.api_params is '接口参数（JSON格式）';
comment on column tushare_api_config.data_fields is '数据字段（JSON格式，用于指定需要下载的字段）';
comment on column tushare_api_config.status is '状态（0正常 1停用）';
comment on column tushare_api_config.create_by is '创建者';
comment on column tushare_api_config.create_time is '创建时间';
comment on column tushare_api_config.update_by is '更新者';
comment on column tushare_api_config.update_time is '更新时间';
comment on column tushare_api_config.remark is '备注信息';
comment on table tushare_api_config is 'Tushare接口配置表';

-- ----------------------------
-- 2、Tushare下载任务表
-- ----------------------------
drop table if exists tushare_download_task;
create table tushare_download_task (
  task_id             bigserial      not null,
  task_name           varchar(100)   not null,
  config_id           bigint         not null,
  cron_expression     varchar(255),
  start_date          varchar(20),
  end_date            varchar(20),
  task_params         text,
  save_path           varchar(500),
  save_format         varchar(20)    default 'csv',
  save_to_db          char(1)        default '0',
  data_table_name     varchar(100),
  status              char(1)        default '0',
  last_run_time       timestamp(0),
  next_run_time       timestamp(0),
  run_count           integer        default 0,
  success_count       integer        default 0,
  fail_count          integer        default 0,
  create_by           varchar(64)    default '',
  create_time         timestamp(0),
  update_by           varchar(64)    default '',
  update_time         timestamp(0),
  remark              varchar(500)   default '',
  primary key (task_id),
  constraint uk_task_name unique (task_name)
);
create index idx_config_id on tushare_download_task(config_id);
comment on column tushare_download_task.task_id is '任务ID';
comment on column tushare_download_task.task_name is '任务名称';
comment on column tushare_download_task.config_id is '接口配置ID';
comment on column tushare_download_task.cron_expression is 'cron执行表达式';
comment on column tushare_download_task.start_date is '开始日期（YYYYMMDD）';
comment on column tushare_download_task.end_date is '结束日期（YYYYMMDD）';
comment on column tushare_download_task.task_params is '任务参数（JSON格式，覆盖接口默认参数）';
comment on column tushare_download_task.save_path is '保存路径';
comment on column tushare_download_task.save_format is '保存格式（csv/excel/json）';
comment on column tushare_download_task.save_to_db is '是否保存到数据库（0否 1是）';
comment on column tushare_download_task.data_table_name is '数据存储表名（为空则使用默认表tushare_data）';
comment on column tushare_download_task.status is '状态（0正常 1暂停）';
comment on column tushare_download_task.last_run_time is '最后运行时间';
comment on column tushare_download_task.next_run_time is '下次运行时间';
comment on column tushare_download_task.run_count is '运行次数';
comment on column tushare_download_task.success_count is '成功次数';
comment on column tushare_download_task.fail_count is '失败次数';
comment on column tushare_download_task.create_by is '创建者';
comment on column tushare_download_task.create_time is '创建时间';
comment on column tushare_download_task.update_by is '更新者';
comment on column tushare_download_task.update_time is '更新时间';
comment on column tushare_download_task.remark is '备注信息';
comment on table tushare_download_task is 'Tushare下载任务表';

-- ----------------------------
-- 3、Tushare下载日志表
-- ----------------------------
drop table if exists tushare_download_log;
create table tushare_download_log (
  log_id              bigserial      not null,
  task_id             bigint         not null,
  task_name           varchar(100)   not null,
  config_id           bigint         not null,
  api_name            varchar(100)   not null,
  download_date       varchar(20),
  record_count        integer        default 0,
  file_path           varchar(500),
  status              char(1)        default '0',
  error_message       text,
  duration            integer,
  create_time         timestamp(0),
  primary key (log_id)
);
create index idx_task_id on tushare_download_log(task_id);
create index idx_config_id on tushare_download_log(config_id);
create index idx_create_time on tushare_download_log(create_time);
comment on column tushare_download_log.log_id is '日志ID';
comment on column tushare_download_log.task_id is '任务ID';
comment on column tushare_download_log.task_name is '任务名称';
comment on column tushare_download_log.config_id is '接口配置ID';
comment on column tushare_download_log.api_name is '接口名称';
comment on column tushare_download_log.download_date is '下载日期（YYYYMMDD）';
comment on column tushare_download_log.record_count is '记录数';
comment on column tushare_download_log.file_path is '文件路径';
comment on column tushare_download_log.status is '执行状态（0成功 1失败）';
comment on column tushare_download_log.error_message is '错误信息';
comment on column tushare_download_log.duration is '执行时长（秒）';
comment on column tushare_download_log.create_time is '创建时间';
comment on table tushare_download_log is 'Tushare下载日志表';

-- ----------------------------
-- 4、Tushare数据存储表（通用表，使用JSONB存储灵活数据）
-- ----------------------------
drop table if exists tushare_data;
create table tushare_data (
  data_id             bigserial      not null,
  task_id             bigint         not null,
  config_id           bigint         not null,
  api_code           varchar(100)    not null,
  download_date       varchar(20),
  data_content        jsonb,
  create_time         timestamp(0)   default current_timestamp,
  primary key (data_id)
);
create index idx_task_id_data on tushare_data(task_id);
create index idx_config_id_data on tushare_data(config_id);
create index idx_api_code_data on tushare_data(api_code);
create index idx_download_date_data on tushare_data(download_date);
create index idx_create_time_data on tushare_data(create_time);
-- 为JSONB字段创建GIN索引以支持高效查询
create index idx_data_content_gin on tushare_data using gin(data_content);
comment on column tushare_data.data_id is '数据ID';
comment on column tushare_data.task_id is '任务ID';
comment on column tushare_data.config_id is '接口配置ID';
comment on column tushare_data.api_code is '接口代码';
comment on column tushare_data.download_date is '下载日期（YYYYMMDD）';
comment on column tushare_data.data_content is '数据内容（JSONB格式）';
comment on column tushare_data.create_time is '创建时间';
comment on table tushare_data is 'Tushare数据存储表（通用表）';