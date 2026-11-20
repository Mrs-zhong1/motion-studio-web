# R47 — 八套模板编辑、保存、重载与导出一致性
- 日期：2026-11-20
- 候选提交：`69fe128d6591b21d6b9d4756c79656909d1e0e12`
- CI： [Motion Studio Web Product E2E #1157](https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/44722111815)
- 覆盖模板：Editorial、Product 3D、Cinematic、Architecture、Creative Agency、Fashion、Gallery、SaaS。
- 自动化：逐套创建项目、下载项目 JSON、重置编辑器、重新导入 JSON、导出独立 HTML。
- 检查：模板 ID 与章节数据往返一致；导出包含 R45 场景构图 CSS 与 R46 响应式/无障碍 CSS；导出章节数与保存数据一致；无页面异常；无水平溢出。
- 浏览器：Chromium、Firefox、WebKit 三个独立矩阵 job 均已对八套模板执行完整往返测试；每个 job 的 R47 报告均为 `pass: true`，并与同一候选提交 SHA 绑定。
## 验收
- [x] Chromium、Firefox、WebKit 三个浏览器均逐一通过八套模板 JSON 保存/重载。
- [x] 八套导出包含与编辑器一致的 R45/R46 样式。
- [x] 导出章节数量与项目数据一致。
- [x] 导出页面无错误、无横向溢出。
- [x] 每个浏览器的测试结果均记录浏览器标识；汇总报告和 CI run 绑定同一候选 SHA。
## 边界
- 此结论仅关闭 R47 自动化往返一致性项，不代表 R48 发布验收通过。
- R48 仍需独立的 `cross-browser-acceptance` 与 `deployment-smoke` 证据；素材授权和人工视觉审批也不由 R47 覆盖。
