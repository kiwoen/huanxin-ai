# GPT + Codex + MiniMind 目标架构

```text
用户 / CLI / Dashboard / Obsidian
              |
              v
      Huanxin Harness Runtime
  Task -> Session -> Loop -> Audit
              |
       +------+------+
       |             |
       v             v
  Decision       Model Router
 MiniMind       MiniMind/GPT/
  本地决策       其他 Provider
       |             |
       +------+------+
              v
       Tool / Skill Registry
 GitHub / Files / RAG / Sandbox
              |
              v
      Approval + Policy + Audit
```

## 组件职责

| 组件 | 职责 |
|---|---|
| MiniMind | 本地分类、路由、工具选择、风险初筛和轻量生成 |
| GPT | 复杂推理、代码理解、教师数据、评测和最终表达 |
| Codex | 修改代码、运行测试、审查 diff、维护部署和文档 |
| Harness | 会话、任务循环、状态、重试、停止和恢复 |
| Tools | GitHub、文件、知识库、浏览器和受限执行环境 |
| Governance | 权限、审批、限流、沙箱和审计 |
| RAG/Memory | 个人知识、项目资料、任务轨迹和长期记忆 |

## 运行原则

- MiniMind 只能从允许的动作集合中选择动作，不能扩大权限。
- 工具执行必须经过策略校验；高风险操作必须人工批准。
- 任务循环必须有最大步数、超时、费用和重试上限。
- 模型替换必须通过统一 Provider，不让业务代码依赖具体模型实现。
- 模型训练和自进化只产生候选版本，经过评测后才能发布。
