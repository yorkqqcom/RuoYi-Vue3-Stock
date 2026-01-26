# Tushare下载任务配置和调度管理细化改进总结

## 一、改进概述

根据单个接口和流程配置下载任务的差异分析，对下载任务配置和调度管理功能进行了细化改进，主要包括：

1. **任务配置细化**：区分单个接口和流程配置的配置项
2. **调度管理增强**：提供针对性的监控和管理功能
3. **日志记录优化**：区分单个接口和流程配置的日志
4. **统计功能增强**：提供任务执行统计信息

## 二、具体改进内容

### 1. 任务模型增强

#### 1.1 添加任务类型字段
- 在 `TushareDownloadTaskModel` 中添加 `task_type` 字段（`single`/`workflow`）
- 通过 `model_post_init` 方法自动根据 `workflow_id` 判断任务类型

#### 1.2 新增任务详情模型
- 创建 `TushareDownloadTaskDetailModel`，包含：
  - 任务基本信息
  - 任务类型
  - 关联接口信息（单个接口任务）
  - 关联流程信息（流程配置任务）
  - 步骤列表（流程配置任务）

#### 1.3 查询模型增强
- `TushareDownloadTaskPageQueryModel` 添加 `task_type` 筛选字段
- `TushareDownloadLogPageQueryModel` 添加 `task_type` 筛选字段

### 2. 服务层增强

#### 2.1 任务详情服务增强
- `task_detail_services` 方法增强，返回任务详情模型：
  - 自动判断任务类型
  - 单个接口任务：返回接口名称和代码
  - 流程配置任务：返回流程名称、描述、步骤列表

#### 2.2 任务列表服务增强
- `get_task_list_services` 方法增强：
  - 为每个任务自动添加 `task_type` 字段
  - 支持按任务类型筛选

#### 2.3 日志列表服务增强
- `get_log_list_services` 方法增强：
  - 为每个日志自动添加 `task_type` 字段
  - 流程配置任务的日志自动提取步骤名称
  - 支持按任务类型筛选

#### 2.4 新增任务统计服务
- `get_task_statistics_services` 方法：
  - 获取任务执行统计信息
  - 区分单个接口和流程配置的统计
  - 流程配置任务提供步骤级统计

### 3. DAO层增强

#### 3.1 任务查询增强
- `get_task_list` 方法支持按任务类型筛选：
  - `single`：`workflow_id` 为 `None`
  - `workflow`：`workflow_id` 不为 `None`

#### 3.2 日志查询增强
- `get_log_list` 方法支持按任务类型筛选：
  - `single`：`task_name` 不包含 `[`
  - `workflow`：`task_name` 包含 `[`

### 4. 调度管理增强

#### 4.1 调度器服务增强
- `TushareSchedulerService` 类添加新方法：
  - `get_task_scheduler_status`：获取任务在调度器中的状态
  - `get_all_scheduled_tasks`：获取所有已调度的任务信息

### 5. 控制器增强

#### 5.1 任务详情接口
- 返回类型改为 `TushareDownloadTaskDetailModel`
- 接口描述更新，说明返回任务类型和关联信息

#### 5.2 新增任务统计接口
- `/downloadTask/statistics/{task_id}`：获取任务执行统计信息

## 三、使用说明

### 1. 任务类型识别

任务类型通过 `workflow_id` 自动判断：
- `workflow_id` 为 `None` → `task_type = 'single'`（单个接口任务）
- `workflow_id` 不为 `None` → `task_type = 'workflow'`（流程配置任务）

### 2. 任务查询

#### 2.1 按任务类型筛选
```python
# 查询单个接口任务
query = TushareDownloadTaskPageQueryModel(task_type='single')

# 查询流程配置任务
query = TushareDownloadTaskPageQueryModel(task_type='workflow')
```

#### 2.2 获取任务详情
```python
# 返回详细信息，包含任务类型和关联信息
task_detail = await TushareDownloadTaskService.task_detail_services(db, task_id)
# task_detail.task_type: 'single' 或 'workflow'
# task_detail.api_name: 单个接口任务的接口名称
# task_detail.workflow_name: 流程配置任务的流程名称
# task_detail.steps: 流程配置任务的步骤列表
```

### 3. 日志查询

#### 3.1 按任务类型筛选日志
```python
# 查询单个接口任务的日志
query = TushareDownloadLogPageQueryModel(task_type='single')

# 查询流程配置任务的日志
query = TushareDownloadLogPageQueryModel(task_type='workflow')
```

#### 3.2 日志中的任务类型
- 日志列表自动添加 `task_type` 字段
- 流程配置任务的日志自动提取 `step_name` 字段

### 4. 任务统计

#### 4.1 获取任务统计信息
```python
# 获取任务执行统计
statistics = await TushareDownloadTaskService.get_task_statistics_services(db, task_id)

# 统计信息包含：
# - task_type: 任务类型
# - run_count: 运行次数
# - success_count: 成功次数
# - fail_count: 失败次数
# - log_statistics: 日志统计（总数、成功数、失败数、总记录数、平均耗时）
# - step_statistics: 步骤统计（仅流程配置任务，包含每个步骤的执行情况）
```

### 5. 调度管理

#### 5.1 获取任务调度状态
```python
# 获取任务在调度器中的状态
status = TushareSchedulerService.get_task_scheduler_status(task_id)
# 返回：job_id, name, next_run_time, trigger
```

#### 5.2 获取所有已调度任务
```python
# 获取所有已调度的任务
tasks = TushareSchedulerService.get_all_scheduled_tasks()
# 返回：任务ID、名称、下次执行时间、触发器信息列表
```

## 四、API接口

### 1. 任务详情接口
- **路径**：`GET /tushare/downloadTask/{task_id}`
- **返回**：`TushareDownloadTaskDetailModel`
- **说明**：返回任务详情，包含任务类型和关联信息

### 2. 任务统计接口
- **路径**：`GET /tushare/downloadTask/statistics/{task_id}`
- **返回**：任务执行统计信息
- **说明**：返回任务执行统计，区分单个接口和流程配置

### 3. 任务列表接口
- **路径**：`GET /tushare/downloadTask/list`
- **参数**：`task_type`（可选，筛选任务类型）
- **返回**：任务列表，每个任务包含 `task_type` 字段

### 4. 日志列表接口
- **路径**：`GET /tushare/downloadLog/list`
- **参数**：`task_type`（可选，筛选任务类型）
- **返回**：日志列表，每个日志包含 `task_type` 和 `step_name`（流程配置任务）字段

## 五、数据库变更

本次改进**不需要**修改数据库表结构，所有功能通过代码逻辑实现：
- 任务类型通过 `workflow_id` 判断
- 日志中的任务类型通过 `task_name` 格式判断（包含 `[` 表示流程配置任务）

## 六、后续优化建议

1. **前端展示优化**：
   - 任务列表区分显示任务类型图标
   - 流程配置任务显示步骤信息
   - 日志查询支持按任务类型筛选

2. **统计报表**：
   - 提供任务执行统计报表
   - 流程配置任务提供步骤执行分析

3. **监控告警**：
   - 根据任务类型设置不同的告警规则
   - 流程配置任务提供步骤级告警

4. **性能优化**：
   - 任务列表查询优化（添加索引）
   - 日志查询优化（按任务类型分区）
