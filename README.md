# 智能抽油机系统

> 《智慧油气田应用开发》课程小组项目 —— 全栈 Web 应用

一个面向教学演示的智能抽油机监控系统，涵盖**实时监测、示功图智能诊断、历史数据报表、远程控制与告警**四大模块。系统内置数据模拟引擎，无需真实设备即可运行演示，并提供规则的、基于模板的、基于机器学习的三种工况诊断方法。

## 技术栈

| 层次 | 技术 |
|---|---|
| 前端 | Vue 3 + TypeScript + Vite + Element Plus + ECharts + Pinia |
| 后端 | Python 3.11 + FastAPI + SQLAlchemy + APScheduler + WebSocket |
| 算法 | NumPy + SciPy + scikit-learn |
| 数据库 | SQLite（零配置，随项目拷贝即可运行） |

## 快速启动

### 1. 后端

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env          # 可选，已有默认配置
python run.py                 # 启动于 http://localhost:8000
```

- Swagger 接口文档：http://localhost:8000/docs
- ReDoc 文档：http://localhost:8000/redoc
- 启动时自动建表并写入种子数据（4 台设备 + 管理员账号），并自动启动数据模拟采集。

### 2. 前端

```bash
cd frontend
npm install
npm run dev                   # 启动于 http://localhost:5173
```

浏览器打开 http://localhost:5173 即可使用。

### 演示账号

| 用户名 | 密码 | 角色 |
|---|---|---|
| admin | admin123 | 管理员 |
| operator | 123456 | 操作员 |

## 功能模块

| 模块 | 页面 | 说明 |
|---|---|---|
| 监控大屏 | `/dashboard` | 暗色科技风，实时参数仪表盘、动态示功图、载荷趋势、告警滚动 |
| 实时监测 | `/realtime` | WebSocket 推送的载荷/位移/电流/冲次等实时数据 |
| 示功图诊断 | `/dynamo` | 6 类工况示功图生成、特征提取、三法诊断对比 |
| 历史数据 | `/history` | 多条件查询历史监测数据 |
| 统计报表 | `/reports` | 工况分布、载荷趋势、CSV/Excel 导出 |
| 远程控制 | `/control` | 设备启停、参数调节、操作日志 |
| 设备管理 | `/devices` | 设备台账增删改查 |
| 告警中心 | `/alarms` | 告警查看、确认、清除 |

## 六种典型工况

正常、泵漏失、供液不足、气体影响、结蜡、抽油杆断脱。每种工况由数学模型生成具有典型几何特征的示功图。

## 演示流程（答辩用）

详见 [docs/07-答辩演示脚本.md](docs/07-答辩演示脚本.md)。

## 目录结构

```
smart-pumping-unit/
├── backend/      # FastAPI 后端（app/core、models、schemas、api、services、tasks、ws、utils）
├── frontend/     # Vue3 前端（src/views、components、stores、api、composables）
└── docs/         # 技术文档与答辩脚本
```

## 文档

- [01-技术栈与架构](docs/01-技术栈与架构.md)
- [02-数据库设计](docs/02-数据库设计.md)
- [03-API接口文档](docs/03-API接口文档.md)
- [04-示功图模拟与诊断算法](docs/04-示功图模拟与诊断算法.md)
- [05-前端页面设计](docs/05-前端页面设计.md)
- [06-分工与里程碑](docs/06-分工与里程碑.md)
- [07-答辩演示脚本](docs/07-答辩演示脚本.md)
