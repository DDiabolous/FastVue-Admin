# 生产运维与容灾保障指南

本文档面向系统管理员与 DevOps 运维人员，提供 FastVue-Admin 在生产环境下的可观测性追踪、排障手段与数据库备份恢复实操规范。

---

## 1. 链路追踪与请求 ID (Request ID)

在分布式或高并发环境中，客户端请求可能经历 Nginx 反向代理、API 路由、数据库查询与审计记录等多个环节。

### 工作机制
- **前端生成/传递**：前端在请求拦截器中，可选择携带全局唯一的 `X-Request-ID` 请求头（UUIDv4）。
- **后端自动补齐与透传**：
  若请求未携带 `X-Request-ID`，后端全局中间件会自动生成一个唯一的 `request_id`。
  后端在返回的 HTTP Response Header 中必定附带：
  ```http
  X-Request-ID: c4b18f3a9e2d4081b23f8510a72d9b6e
  ```
- **异常排查联动**：
  当发生 500 意外错误或业务报警时，响应结果中或日志均能通过该 `X-Request-ID` 瞬间从海量日志中检索出当时触发该问题的精确调用链路与 Traceback。

---

## 2. 结构化日志规范

生产环境日志推荐使用 JSON 结构化格式输出，便于通过 Fluentd、Logstash 或 Vector 采集至 Elasticsearch 或 Grafana Loki。

### 结构化错误日志格式示例
```json
{
  "timestamp": "2026-10-22T02:00:00.123456Z",
  "level": "ERROR",
  "logger": "fastvue.error",
  "request_id": "c4b18f3a9e2d4081b23f8510a72d9b6e",
  "method": "POST",
  "path": "/api/v1/system/users",
  "client_ip": "192.168.1.100",
  "operator": "admin",
  "status_code": 500,
  "exception": "DatabaseError",
  "message": "Connection to PostgreSQL closed unexpectedly",
  "traceback": "Traceback (most recent call last):\n  ..."
}
```

---

## 3. PostgreSQL 数据库备份与恢复

FastVue-Admin 核心业务数据持久化于 PostgreSQL。建议配置定期自动逻辑备份及主备容灾。

### 3.1 数据库备份 (Backup)

#### 方案一：Docker 容器环境下一键备份（推荐）
在运行 Docker Compose 的宿主机上执行：

```bash
# 导出为压缩的自定义格式 (.dump，恢复速度最快、支持并行恢复)
docker compose exec -T db pg_dump -U fastvue -F c -b -v fastvue > /backup/fastvue_$(date +%Y%m%d_%H%M%S).dump

# 或导出为可读的 SQL 脚本 (.sql.gz)
docker compose exec -T db pg_dump -U fastvue fastvue | gzip > /backup/fastvue_$(date +%Y%m%d_%H%M%S).sql.gz
```

#### 方案二：定时自动备份脚本 (Crontab)
创建 `/opt/scripts/backup_fastvue.sh`：

```bash
#!/usr/bin/env bash
set -e

BACKUP_DIR="/var/backups/fastvue"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME="$BACKUP_DIR/fastvue_backup_$TIMESTAMP.dump"
KEEP_DAYS=14

mkdir -p "$BACKUP_DIR"

# 执行备份
docker compose -f /path/to/FastVue-Admin/compose.yaml exec -T db \
  pg_dump -U fastvue -F c -b fastvue > "$FILENAME"

# 自动清理 14 天前的旧备份
find "$BACKUP_DIR" -type f -name "fastvue_backup_*.dump" -mtime +$KEEP_DAYS -delete

echo "[$(date)] Backup successfully saved to $FILENAME"
```

配置 Crontab（每天凌晨 02:00 自动执行）：
```cron
0 2 * * * /bin/bash /opt/scripts/backup_fastvue.sh >> /var/log/fastvue_backup.log 2>&1
```

---

### 3.2 数据库恢复 (Restore)

#### 场景 A：从 `.dump` 自定义格式归档恢复

1. **若恢复至空数据库**：
   ```bash
   docker compose exec -T db pg_restore -U fastvue -d fastvue -v < /backup/fastvue_20261022_020000.dump
   ```
2. **若恢复并覆盖已有数据库**（需清空旧表结构）：
   ```bash
   docker compose exec -T db pg_restore -U fastvue -d fastvue --clean --if-exists -v < /backup/fastvue_20261022_020000.dump
   ```

#### 场景 B：从 `.sql.gz` 纯文本格式恢复

```bash
gunzip -c /backup/fastvue_20261022_020000.sql.gz | docker compose exec -T db psql -U fastvue -d fastvue
```

#### 恢复后验证步骤
1. 检查数据库连通性：
   ```bash
   curl -i http://localhost:8001/api/health
   ```
   返回状态码应当为 `200` 且 `{"code": 200, "message": "ok"}`。
2. 运行 Alembic 检查迁移版本是否一致：
   ```bash
   cd backend && uv run alembic current
   ```
3. 登录后台验证关键数据（用户、角色、字典配置）是否完整。
