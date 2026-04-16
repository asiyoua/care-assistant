# Setup 首次配置流程

当用户首次使用 CARE 助理时，自动检测配置并引导建表。

## 配置文件位置

```
~/.care-assistant/config.json
```

## 配置文件格式

```json
{
  "base_token": "<创建后填入>",
  "table_id": "<创建后填入>",
  "article_table_id": "<创建后填入>",
  "view_id": "<创建后填入>",
  "user_open_id": "<从 auth status 获取>",
  "created_at": "<当天日期>"
}
```

## 检测流程

1. 尝试读取 `~/.care-assistant/config.json`
2. 如果文件存在且 `base_token` 和 `table_id` 不为空 → 配置已就绪，跳过 setup
3. 如果文件不存在或缺少关键字段 → 进入 setup 流程

## Setup 流程

### Step 1: 获取用户信息

```bash
lark-cli auth status
```

从返回结果中提取 `userOpenId`。

### Step 2: 创建多维表格

```bash
lark-cli base +base-create \
  --name "CARE 助理" \
  --time-zone Asia/Shanghai
```

记录返回的 `base_token`。

### Step 3: 创建记录表

```bash
lark-cli base +table-create \
  --base-token <base_token> \
  --name "记录表" \
  --fields '[{"name":"记录标题","type":"text"},{"name":"来源","type":"select","multiple":false,"options":[{"name":"飞书对话"},{"name":"终端"},{"name":"录音"}]},{"name":"标签","type":"select","multiple":true,"options":[{"name":"待办"},{"name":"灵感"},{"name":"其他"},{"name":"AI"},{"name":"社群"},{"name":"内容创作"},{"name":"线下"}]},{"name":"详细内容","type":"text"},{"name":"创建日期","type":"datetime","style":{"format":"yyyy-MM-dd"}},{"name":"截止日期","type":"datetime","style":{"format":"yyyy-MM-dd"}},{"name":"完成状态","type":"select","multiple":false,"options":[{"name":"未完成"},{"name":"已完成"}]},{"name":"关联文档","type":"text","style":{"type":"url"}}]'
```

记录返回的 `table_id` 和默认视图 `view_id`。

### Step 4: 创建文章收藏表

```bash
lark-cli base +table-create \
  --base-token <base_token> \
  --name "文章收藏" \
  --fields '[{"name":"标题","type":"text"},{"name":"链接","type":"text","style":{"type":"url"}},{"name":"备注","type":"text"},{"name":"标签","type":"select","multiple":true,"options":[{"name":"AI"},{"name":"效率"},{"name":"产品"},{"name":"技术"},{"name":"商业"},{"name":"其他"}]},{"name":"来源","type":"select","multiple":false,"options":[{"name":"终端"},{"name":"飞书对话"},{"name":"浏览器"}]},{"name":"收藏时间","type":"datetime","style":{"format":"yyyy-MM-dd HH:mm"}}]'
```

记录返回的 `article_table_id`。

### Step 5: 创建录音文件目录

```bash
mkdir -p ~/.care-assistant/recordings
```

### Step 6: 保存配置

将配置写入 `~/.care-assistant/config.json`：

```bash
mkdir -p ~/.care-assistant
cat > ~/.care-assistant/config.json << 'EOF'
{
  "base_token": "<base_token>",
  "table_id": "<table_id>",
  "article_table_id": "<article_table_id>",
  "view_id": "<view_id>",
  "user_open_id": "<userOpenId>",
  "created_at": "<今天日期>"
}
EOF
```

### Step 7: 反馈

告知用户：
- 多维表格已创建，附上访问链接（`https://my.feishu.cn/base/<base_token>`）
- 可以在飞书中打开查看
- 建议将链接加入飞书收藏或侧边栏
