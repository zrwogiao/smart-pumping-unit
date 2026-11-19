# 03 API 接口文档

后端启动后，可直接访问 **http://localhost:8000/docs**（Swagger UI）查看并在线调试所有接口。本文为文字速查，统一前缀 `/api/v1`，统一响应包装 `{ code, message, data }`（`code=0` 表示成功）。前端 Axios 拦截器会自动解包 `data`。

## 认证 `/auth`
| 方法 | 路径 | 作用 |
|---|---|---|
| POST | `/auth/login` | 登录，返回 token 与用户信息 |
| GET | `/auth/me` | 当前用户信息 |

## 设备管理 `/devices`
| 方法 | 路径 | 作用 |
|---|---|---|
| GET / POST | `/devices` | 列表 / 新增 |
| GET / PUT / DELETE | `/devices/{device_id}` | 详情 / 修改 / 删除 |

## 实时监测 `/monitoring`
| 方法 | 路径 | 作用 |
|---|---|---|
| GET | `/monitoring/latest/{device_id}` | 最新一条实时数据 |
| GET | `/monitoring/series/{device_id}?limit=100` | 历史序列 |
| POST | `/monitoring/simulate/start\|stop` | 启动/停止模拟采集 |
| GET | `/monitoring/simulate/status` | 模拟采集状态 |
| WS | `/ws/monitoring/{device_id}` | 实时推送（device_id=0 订阅全部，大屏用） |

## 示功图与诊断 `/dynamo` `/diagnosis`
| 方法 | 路径 | 作用 |
|---|---|---|
| POST | `/dynamo/generate` | 生成示功图，body: `{device_id, condition}` |
| GET | `/dynamo/latest/{device_id}` | 最新示功图 |
| GET | `/dynamo/conditions/list` | 工况字典 |
| POST | `/diagnosis/analyze` | 诊断，body: `{device_id, method, dynamo_id?}`，method=rule/template/ml/all |
| GET | `/diagnosis/results/{device_id}` | 历史诊断结果 |
| GET | `/diagnosis/conditions` | 工况字典 |

## 历史与报表 `/history`
| 方法 | 路径 | 作用 |
|---|---|---|
| GET | `/history/query` | 多条件查询（device_id/start/end/limit） |
| GET | `/history/trend` | 趋势数据（device_id/metric/start/end/limit） |
| GET | `/history/reports/summary` | 统计汇总（记录数、平均载荷、工况分布等） |
| GET | `/history/reports/export` | 导出（device_id/start/end/format=csv\|excel），返回文件流 |

## 远程控制 `/control`
| 方法 | 路径 | 作用 |
|---|---|---|
| POST | `/control/{device_id}/start\|stop` | 远程启停 |
| PUT | `/control/{device_id}/params` | 参数调节（冲次/冲程/载荷上限/电流上限） |
| GET | `/control/{device_id}/logs` | 控制日志 |

## 告警 `/alarms`
| 方法 | 路径 | 作用 |
|---|---|---|
| GET | `/alarms?status=&level=&limit=` | 告警列表 |
| PUT | `/alarms/{alarm_id}/ack` | 确认告警 |
| PUT | `/alarms/{alarm_id}/clear` | 清除告警 |

## 其他
| 方法 | 路径 | 作用 |
|---|---|---|
| GET | `/` | 应用信息 |
| GET | `/health` | 健康检查 |
