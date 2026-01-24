<template>
   <div class="app-container">
      <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch">
         <el-form-item label="任务名称" prop="taskName">
            <el-input
               v-model="queryParams.taskName"
               placeholder="请输入任务名称"
               clearable
               style="width: 200px"
               @keyup.enter="handleQuery"
            />
         </el-form-item>
         <el-form-item label="接口配置" prop="configId">
            <el-select v-model="queryParams.configId" placeholder="请选择接口配置" clearable style="width: 200px">
               <el-option
                  v-for="config in apiConfigOptions"
                  :key="config.configId"
                  :label="config.apiName"
                  :value="config.configId"
               />
            </el-select>
         </el-form-item>
         <el-form-item label="状态" prop="status">
            <el-select v-model="queryParams.status" placeholder="请选择状态" clearable style="width: 200px">
               <el-option
                  v-for="dict in sys_normal_disable"
                  :key="dict.value"
                  :label="dict.label"
                  :value="dict.value"
               />
            </el-select>
         </el-form-item>
         <el-form-item>
            <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
            <el-button icon="Refresh" @click="resetQuery">重置</el-button>
         </el-form-item>
      </el-form>

      <el-row :gutter="10" class="mb8">
         <el-col :span="1.5">
            <el-button
               type="primary"
               plain
               icon="Plus"
               @click="handleAdd"
               v-hasPermi="['tushare:downloadTask:add']"
            >新增</el-button>
         </el-col>
         <el-col :span="1.5">
            <el-button
               type="success"
               plain
               icon="Edit"
               :disabled="single"
               @click="handleUpdate"
               v-hasPermi="['tushare:downloadTask:edit']"
            >修改</el-button>
         </el-col>
         <el-col :span="1.5">
            <el-button
               type="danger"
               plain
               icon="Delete"
               :disabled="multiple"
               @click="handleDelete"
               v-hasPermi="['tushare:downloadTask:remove']"
            >删除</el-button>
         </el-col>
         <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
      </el-row>

      <el-table v-loading="loading" :data="taskList" @selection-change="handleSelectionChange">
         <el-table-column type="selection" width="55" align="center" />
         <el-table-column label="任务ID" width="100" align="center" prop="taskId" />
         <el-table-column label="任务名称" align="center" prop="taskName" :show-overflow-tooltip="true" />
         <el-table-column label="接口配置" align="center" prop="configId" :show-overflow-tooltip="true">
            <template #default="scope">
               <span>{{ getApiConfigName(scope.row.configId) }}</span>
            </template>
         </el-table-column>
         <el-table-column label="日期范围" align="center" :show-overflow-tooltip="true">
            <template #default="scope">
               <span v-if="scope.row.startDate && scope.row.endDate">
                  {{ scope.row.startDate }} ~ {{ scope.row.endDate }}
               </span>
               <span v-else>当日</span>
            </template>
         </el-table-column>
         <el-table-column label="保存格式" align="center" prop="saveFormat" width="100" />
         <el-table-column label="保存到数据库" align="center" width="120">
            <template #default="scope">
               <el-tag :type="scope.row.saveToDb === '1' ? 'success' : 'info'">
                  {{ scope.row.saveToDb === '1' ? '是' : '否' }}
               </el-tag>
            </template>
         </el-table-column>
         <el-table-column label="运行次数" align="center" prop="runCount" width="100" />
         <el-table-column label="成功次数" align="center" prop="successCount" width="100" />
         <el-table-column label="失败次数" align="center" prop="failCount" width="100" />
         <el-table-column label="状态" align="center">
            <template #default="scope">
               <el-switch
                  v-model="scope.row.status"
                  active-value="0"
                  inactive-value="1"
                  @change="handleStatusChange(scope.row)"
               ></el-switch>
            </template>
         </el-table-column>
         <el-table-column label="最后运行" align="center" prop="lastRunTime" width="180">
            <template #default="scope">
               <span>{{ parseTime(scope.row.lastRunTime) }}</span>
            </template>
         </el-table-column>
         <el-table-column label="操作" align="center" width="250" class-name="small-padding fixed-width">
            <template #default="scope">
               <el-tooltip content="执行" placement="top">
                  <el-button link type="success" icon="VideoPlay" @click="handleExecute(scope.row)" v-hasPermi="['tushare:downloadTask:execute']"></el-button>
               </el-tooltip>
               <el-tooltip content="修改" placement="top">
                  <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['tushare:downloadTask:edit']"></el-button>
               </el-tooltip>
               <el-tooltip content="删除" placement="top">
                  <el-button link type="primary" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['tushare:downloadTask:remove']"></el-button>
               </el-tooltip>
            </template>
         </el-table-column>
      </el-table>

      <pagination
         v-show="total > 0"
         :total="total"
         v-model:page="queryParams.pageNum"
         v-model:limit="queryParams.pageSize"
         @pagination="getList"
      />

      <!-- 添加或修改下载任务对话框 -->
      <el-dialog :title="title" v-model="open" width="900px" append-to-body>
         <el-form ref="taskRef" :model="form" :rules="rules" label-width="120px">
            <el-row>
               <el-col :span="24">
                  <el-form-item label="任务名称" prop="taskName">
                     <el-input v-model="form.taskName" placeholder="请输入任务名称" />
                  </el-form-item>
               </el-col>
               <el-col :span="24">
                  <el-form-item label="接口配置" prop="configId">
                     <el-select v-model="form.configId" placeholder="请选择接口配置" style="width: 100%" @change="handleConfigChange">
                        <el-option
                           v-for="config in apiConfigOptions"
                           :key="config.configId"
                           :label="config.apiName + ' (' + config.apiCode + ')'"
                           :value="config.configId"
                        />
                     </el-select>
                  </el-form-item>
               </el-col>
               <el-col :span="12">
                  <el-form-item label="开始日期" prop="startDate">
                     <el-date-picker
                        v-model="form.startDate"
                        type="date"
                        format="YYYYMMDD"
                        value-format="YYYYMMDD"
                        placeholder="选择开始日期"
                        style="width: 100%"
                     />
                     <div style="color: #909399; font-size: 12px; margin-top: 5px;">
                        格式：YYYYMMDD，如：20240101，留空则下载当日数据
                     </div>
                  </el-form-item>
               </el-col>
               <el-col :span="12">
                  <el-form-item label="结束日期" prop="endDate">
                     <el-date-picker
                        v-model="form.endDate"
                        type="date"
                        format="YYYYMMDD"
                        value-format="YYYYMMDD"
                        placeholder="选择结束日期"
                        style="width: 100%"
                     />
                     <div style="color: #909399; font-size: 12px; margin-top: 5px;">
                        留空则下载当日数据
                     </div>
                  </el-form-item>
               </el-col>
               <el-col :span="24">
                  <el-form-item label="任务参数" prop="taskParams">
                     <el-input 
                        v-model="form.taskParams" 
                        type="textarea" 
                        :rows="4" 
                        placeholder='请输入JSON格式的任务参数，会覆盖接口默认参数，如：{"trade_date": "20240101"}'
                     />
                     <div style="color: #909399; font-size: 12px; margin-top: 5px;">
                        格式：JSON对象，会覆盖接口配置中的默认参数
                     </div>
                  </el-form-item>
               </el-col>
               <el-col :span="24">
                  <el-form-item label="保存到数据库" prop="saveToDb">
                     <el-switch
                        v-model="form.saveToDb"
                        active-value="1"
                        inactive-value="0"
                     ></el-switch>
                     <div style="color: #909399; font-size: 12px; margin-top: 5px;">
                        开启后，数据将保存到数据库表 tushare_data（使用JSONB格式存储）
                     </div>
                  </el-form-item>
               </el-col>
               <el-col :span="24" v-if="form.saveToDb === '0' || form.savePath">
                  <el-form-item label="保存路径" prop="savePath">
                     <el-input v-model="form.savePath" placeholder="请输入保存路径，如：./data/tushare" />
                     <div style="color: #909399; font-size: 12px; margin-top: 5px;">
                        留空则不保存到文件，默认：./data/tushare
                     </div>
                  </el-form-item>
               </el-col>
               <el-col :span="24" v-if="form.savePath">
                  <el-form-item label="保存格式" prop="saveFormat">
                     <el-radio-group v-model="form.saveFormat">
                        <el-radio value="csv">CSV</el-radio>
                        <el-radio value="excel">Excel</el-radio>
                        <el-radio value="json">JSON</el-radio>
                     </el-radio-group>
                     <div style="color: #909399; font-size: 12px; margin-top: 5px;">
                        仅在选择保存路径时生效
                     </div>
                  </el-form-item>
               </el-col>
               <el-col :span="24" v-if="form.saveToDb === '1'">
                  <el-form-item label="数据表名" prop="dataTableName">
                     <el-input v-model="form.dataTableName" placeholder="请输入数据存储表名（留空则使用默认表名：tushare_接口代码）" />
                     <div style="color: #909399; font-size: 12px; margin-top: 5px;">
                        留空则自动使用 tushare_接口代码 作为表名，表不存在时会自动创建
                     </div>
                  </el-form-item>
               </el-col>
               <el-col :span="24">
                  <el-form-item label="Cron表达式" prop="cronExpression">
                     <el-input v-model="form.cronExpression" placeholder="请输入cron执行表达式（可选，用于定时任务）" />
                     <div style="color: #909399; font-size: 12px; margin-top: 5px;">
                        可选，如果需要在系统定时任务中配置，请填写cron表达式
                     </div>
                  </el-form-item>
               </el-col>
               <el-col :span="24" v-if="form.taskId !== undefined">
                  <el-form-item label="状态">
                     <el-radio-group v-model="form.status">
                        <el-radio
                           v-for="dict in sys_normal_disable"
                           :key="dict.value"
                           :value="dict.value"
                        >{{ dict.label }}</el-radio>
                     </el-radio-group>
                  </el-form-item>
               </el-col>
               <el-col :span="24">
                  <el-form-item label="备注" prop="remark">
                     <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="请输入备注" />
                  </el-form-item>
               </el-col>
            </el-row>
         </el-form>
         <template #footer>
            <div class="dialog-footer">
               <el-button type="primary" @click="submitForm">确 定</el-button>
               <el-button @click="cancel">取 消</el-button>
            </div>
         </template>
      </el-dialog>
   </div>
</template>

<script setup name="DownloadTask">
import { watch } from "vue"
import { listDownloadTask, getDownloadTask, delDownloadTask, addDownloadTask, updateDownloadTask, changeDownloadTaskStatus, executeDownloadTask } from "@/api/tushare/downloadTask"
import { listApiConfig } from "@/api/tushare/apiConfig"

const { proxy } = getCurrentInstance();
const { sys_normal_disable } = proxy.useDict("sys_normal_disable");

const taskList = ref([]);
const apiConfigOptions = ref([]);
const open = ref(false);
const loading = ref(true);
const showSearch = ref(true);
const ids = ref([]);
const single = ref(true);
const multiple = ref(true);
const total = ref(0);
const title = ref("");

const data = reactive({
  form: {},
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    taskName: undefined,
    configId: undefined,
    status: undefined
  },
  rules: {
    taskName: [{ required: true, message: "任务名称不能为空", trigger: "blur" }],
    configId: [{ required: true, message: "接口配置不能为空", trigger: "change" }],
    taskParams: [
      {
        validator: (rule, value, callback) => {
          if (value && value.trim()) {
            try {
              JSON.parse(value);
              callback();
            } catch (e) {
              callback(new Error("任务参数必须是有效的JSON格式"));
            }
          } else {
            callback();
          }
        },
        trigger: "blur"
      }
    ]
  }
});

const { queryParams, form, rules } = toRefs(data);

/** 获取接口配置名称 */
function getApiConfigName(configId) {
  const config = apiConfigOptions.value.find(item => item.configId === configId);
  return config ? config.apiName : configId;
}

/** 查询下载任务列表 */
function getList() {
  loading.value = true;
  listDownloadTask(queryParams.value).then(response => {
    taskList.value = response.rows;
    total.value = response.total;
    loading.value = false;
  });
}

/** 查询接口配置列表 */
function getApiConfigList() {
  listApiConfig({ pageNum: 1, pageSize: 1000 }).then(response => {
    apiConfigOptions.value = response.rows || [];
  });
}

/** 接口配置改变时，自动填充数据表名 */
function handleConfigChange(configId) {
  if (configId && form.value.saveToDb === '1') {
    const config = apiConfigOptions.value.find(item => item.configId === configId);
    if (config && config.apiCode) {
      // 如果数据表名为空，则自动填充为 tushare_接口代码
      if (!form.value.dataTableName || form.value.dataTableName.trim() === '') {
        form.value.dataTableName = `tushare_${config.apiCode}`;
      }
    }
  }
}

// 监听保存到数据库开关变化
watch(() => form.value.saveToDb, (newVal) => {
  if (newVal === '1' && form.value.configId) {
    // 开启保存到数据库时，如果已选择接口配置，自动填充表名
    handleConfigChange(form.value.configId);
  }
});

/** 取消按钮 */
function cancel() {
  open.value = false;
  reset();
}

/** 表单重置 */
function reset() {
  form.value = {
    taskId: undefined,
    taskName: undefined,
    configId: undefined,
    cronExpression: undefined,
    startDate: undefined,
    endDate: undefined,
    taskParams: undefined,
    savePath: undefined,
    saveFormat: "csv",
    saveToDb: "0",
    dataTableName: undefined,
    status: "0",
    remark: undefined
  };
  proxy.resetForm("taskRef");
}

/** 搜索按钮操作 */
function handleQuery() {
  queryParams.value.pageNum = 1;
  getList();
}

/** 重置按钮操作 */
function resetQuery() {
  proxy.resetForm("queryRef");
  handleQuery();
}

// 多选框选中数据
function handleSelectionChange(selection) {
  ids.value = selection.map(item => item.taskId);
  single.value = selection.length != 1;
  multiple.value = !selection.length;
}

// 状态修改
function handleStatusChange(row) {
  let text = row.status === "0" ? "启用" : "停用";
  proxy.$modal.confirm('确认要"' + text + '""' + row.taskName + '"任务吗?').then(function () {
    return changeDownloadTaskStatus(row.taskId, row.status);
  }).then(() => {
    proxy.$modal.msgSuccess(text + "成功");
  }).catch(function () {
    row.status = row.status === "0" ? "1" : "0";
  });
}

/** 新增按钮操作 */
function handleAdd() {
  reset();
  open.value = true;
  title.value = "添加下载任务";
}

/** 修改按钮操作 */
function handleUpdate(row) {
  reset();
  const taskId = row.taskId || ids.value[0];
  getDownloadTask(taskId).then(response => {
    form.value = response.data;
    open.value = true;
    title.value = "修改下载任务";
  });
}

/** 提交按钮 */
function submitForm() {
  proxy.$refs["taskRef"].validate(valid => {
    if (valid) {
      if (form.value.taskId != undefined) {
        updateDownloadTask(form.value).then(response => {
          proxy.$modal.msgSuccess("修改成功");
          open.value = false;
          getList();
        });
      } else {
        addDownloadTask(form.value).then(response => {
          proxy.$modal.msgSuccess("新增成功");
          open.value = false;
          getList();
        });
      }
    }
  });
}

/** 执行按钮操作 */
function handleExecute(row) {
  const taskId = row.taskId;
  proxy.$modal.confirm('确认要立即执行任务"' + row.taskName + '"吗？').then(function () {
    return executeDownloadTask(taskId);
  }).then(() => {
    proxy.$modal.msgSuccess("任务已提交执行，请稍后查看执行日志");
    getList();
  }).catch(() => {});
}

/** 删除按钮操作 */
function handleDelete(row) {
  const taskIds = row.taskId || ids.value;
  proxy.$modal.confirm('是否确认删除下载任务编号为"' + taskIds + '"的数据项?').then(function () {
    return delDownloadTask(taskIds);
  }).then(() => {
    getList();
    proxy.$modal.msgSuccess("删除成功");
  }).catch(() => {});
}

getList();
getApiConfigList();
</script>
