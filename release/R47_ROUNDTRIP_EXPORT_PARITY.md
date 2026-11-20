# R47 — 八套模板编辑、保存、重载与导出一致性
- 日期：2026-11-19
- 覆盖模板：Editorial、Product 3D、Cinematic、Architecture、Creative Agency、Fashion、Gallery、SaaS。
- 自动化：逐套创建项目、下载项目 JSON、重置编辑器、重新导入 JSON、导出独立 HTML。
- 检查：模板 ID 与章节数据往返一致；导出包含 R45 场景构图 CSS 与 R46 响应式/无障碍 CSS；导出章节数与保存数据一致；无页面异常；无水平溢出。
- 浏览器：CI 矩阵为 Chromium、Firefox、WebKit；三者均执行八套模板逐一保存 JSON、重置、重载、导出 HTML 的完整往返测试，以及独立的编辑保存导出冒烟。R47 只有在三个矩阵 job 均通过且报告绑定同一 PR head SHA 时才算完成。
## 验收
- [ ] Chromium、Firefox、WebKit 三个浏览器均逐一通过八套模板 JSON 保存/重载。
- [ ] 八套导出包含与编辑器一致的 R45/R46 样式。
- [ ] 导出章节数量与项目数据一致。
- [ ] 导出页面无错误、无横向溢出。
- [ ] 每个浏览器的测试结果均记录浏览器标识；汇总报告和 CI run 绑定同一候选 SHA。