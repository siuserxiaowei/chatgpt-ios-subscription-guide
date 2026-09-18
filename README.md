# iOS ChatGPT 订阅拦截与转移分析 · 网页阅读版

用户提供的 14 页 PDF 的静态网页转换。保留原文内容，未对技术主张进行验证，未补充操作步骤。原文中示例密钥、账号和交易标识已隐去，原始 PDF 不上传。

无框架、无构建依赖。支持手机阅读、章节导航、表格横向滚动、阅读进度和联系二维码。

`index.html`、`style.css`、`script.js` 和 `assets/` 可直接部署至 GitHub Pages。

如需重新从源 PDF 转换，安装 Poppler 后执行：

```sh
python3 build.py /path/to/source.pdf
```

`template.html` 是页面模板；联系信息在模板中维护。网页排版代码与文档内容的权利分别归其权利人。
