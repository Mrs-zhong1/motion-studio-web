# R46 — Responsive & accessibility hardening
- 日期：2026-11-19
- 触控目标最小高度：44px（关键导航/按钮）。
- 键盘焦点：统一 focus-visible 高对比轮廓。
- 动效：遵守 prefers-reduced-motion。
- 移动端：防横向溢出；章节画布使用动态视口高度；安全区适配。
- 编辑器预览和独立导出同步注入。
## 验收
- [ ] 360/390/768/1024/1440 宽度无横向滚动条。
- [ ] 键盘 Tab 焦点可见，按钮/标签可操作。
- [ ] 关键触控目标不小于 44px。
- [ ] 减少动态效果设置下无强制连续动画。
- [ ] Chromium、Firefox、WebKit 无控制台错误。