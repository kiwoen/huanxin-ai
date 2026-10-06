---
title: 网络资料与依据
tags: [warehouse, references, research]
---

# 网络资料与依据

**检索日期：2026-10-06。** 项目书模板用于组织章节；产品官方文档用于核对功能线索；最终选型仍应在朋友的实际流程和授权范围内验证。

## 项目书与项目管理结构

- [欧盟委员会 PM² Artefacts](https://pm2.europa.eu/pm2-artefacts_en)：列有项目启动请求、商业论证、项目章程、工作计划、风险计划、质量计划、交付验收和项目结束报告等模板。本项目书按小型试点缩编这些章节。
- [英国 Defra 项目启动经验](https://www.gov.uk/government/publications/defra-project-initiation-lessons-learned-report/defra-project-initiation-lessons-learned-report-accessible-version)：强调项目启动文件要让目的、范围、受众、风险、假设、问题和依赖清楚，并指出内容比模板形式更重要。
- [英国政府项目战略与交付计划指南](https://www.gov.uk/government/publications/strategy-and-delivery-plan-guidance-mega-projects/strategy-and-delivery-plan-guidance-mega-projects)：项目快照、范围、成果、时间阶段、成本和风险结构为本页导航与实施计划提供参考；该指南主要面向大型项目，本项目仅借用结构，不照搬审批规模。

## 仓储系统与条码

- [InvenTree 官方库存文档](https://docs.inventree.org/en/stable/stock/)：库存项可关联商品/零件、货位、数量、供应商、批次/序列号和库存追踪；货位支持层级结构。
- [InvenTree 官方扫码操作文档](https://docs.inventree.org/en/latest/app/barcode/)：介绍扫描库存项和货位、扫描入库、移库、盘点等操作。
- [InvenTree GitHub 仓库与许可证](https://github.com/inventree/inventree)：项目定位为开源库存管理系统；仓库页面标示 MIT 许可证。部署时仍需检查依赖、插件和商标使用条件。
- [ERPNext 官方 Stock Entry 文档](https://docs.frappe.io/erpnext/stock-entry)：记录物料收货、发料、仓间移动等库存交易。
- [ERPNext 官方 Pick List 文档](https://docs.frappe.io/erpnext/pick-list)：包含扫描模式以核对拣货商品。
- [ERPNext 项目许可与品牌说明](https://github.com/frappe/erpnext)：官方仓库说明代码采用 GNU GPL v3，并另行说明商标规则；若修改或分发需做许可证审查。
- [Odoo 18 官方收货与发货条码文档](https://www.odoo.com/documentation/18.0/applications/inventory_and_mrp/barcode/operations/receipts_deliveries.html)：说明通过扫码器或手机实时处理收货、发货，并可选择货位。
- [Odoo 19 官方许可证说明](https://www.odoo.com/documentation/19.0/ro/legal/licenses.html)：说明 Community 与 Enterprise 使用不同授权；具体条码功能和可用版本应逐项确认。
- [GS1 条码标准概览](https://www.gs1.org/standards/barcodes)：介绍条码承载商品、物流单元、地点等识别信息及追溯用途。

## 使用限制

- 上述资料说明产品具备某些功能，不等于这些功能在所有版本、部署方式和授权条件下都可免费使用。
- 开源许可证、插件依赖和商用分发条件须在具体选型时重新核对。
- 本页来源不构成市场规模、报价、法律适用或项目成功的证明；这些结论需要本地试点与专业意见支持。
