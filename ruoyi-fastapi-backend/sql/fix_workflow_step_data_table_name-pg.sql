-- ----------------------------
-- 修复脚本：为 tushare_workflow_step 表添加 data_table_name 字段
-- 如果字段已存在，则跳过
-- ----------------------------

DO $$
BEGIN
    -- 检查字段是否存在，如果不存在则添加
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'tushare_workflow_step' 
        AND column_name = 'data_table_name'
    ) THEN
        ALTER TABLE tushare_workflow_step ADD COLUMN data_table_name varchar(100);
        COMMENT ON COLUMN tushare_workflow_step.data_table_name IS '数据存储表名（为空则使用任务配置的表名或默认表名）';
        RAISE NOTICE '字段 data_table_name 已成功添加到 tushare_workflow_step 表';
    ELSE
        RAISE NOTICE '字段 data_table_name 已存在，跳过添加';
    END IF;
END $$;
