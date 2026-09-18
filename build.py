"""Convert supplied PDF text to a static reading page. No network requests."""
import re, sys, html, subprocess
from pathlib import Path

ROOT = Path(__file__).parent
raw = subprocess.check_output(['pdftotext', '-layout', sys.argv[1], '-']).decode()
# Remove identifying samples before creating ANY public artifact.
raw = re.sub(r'appl_[A-Za-z0-9]+', '[API_KEY_REDACTED]', raw)
raw = re.sub(r'\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b', '[ACCOUNT_ID_REDACTED]', raw, flags=re.I)
raw = re.sub(r'(?<!\d)\d{14,}(?!\d)', '[TRANSACTION_ID_REDACTED]', raw)
pages = raw.split('\f')
lines = []
for page in pages[3:]:
    for line in page.splitlines():
        if re.search(r'iOS ChatGPT 订阅拦截与转移分析\s+第', line):
            continue
        if '@@' in line:
            continue
        lines.append(line.rstrip())
content = '\n'.join(lines).strip()
content = re.sub(r'(?m)^\s*(\d+\.\s+(?:前置条件|网络环境配置|iOS 越狱设备配置|订阅流程详解|关键请求字段参考|流程架构图|核心原理概述|拦截：屏蔽回调请求|转移：修改 User ID 实现跨账号激活|关键请求详解|响应数据结构))\s*$', r'\n\n\1\n\n', content)
# Page breaks may split a paragraph or table, but must not remove source text.
blocks = re.split(r'\n\s*\n+', content)
body, toc, section = [], [], 0
for block in blocks:
    block = block.strip('\n')
    stripped = block.strip()
    if not stripped:
        continue
    compact = re.sub(r'\s+', '', stripped)
    if compact in ('TEXT', 'HTTP', 'JSON'):
        continue
    if re.match(r'^第[一二]部分：', stripped):
        body.append('<div class="part">'+html.escape(stripped)+'</div>')
    elif re.match(r'^\d+\.\s+[^\n]+$', stripped):
        num = re.match(r'^(\d+)\.', stripped).group(1)
        # Numbered procedural list items have a following line or are kept as source text.
        known = ['前置条件', '网络环境配置', 'iOS 越狱设备配置', '订阅流程详解', '关键请求字段参考', '流程架构图', '核心原理概述', '拦截：屏蔽回调请求', '转移：修改 User ID 实现跨账号激活', '关键请求详解', '响应数据结构']
        if any(x in stripped for x in known):
            section += 1
            title = html.escape(re.sub(r'^\d+\.\s*', '', stripped))
            body.append(f'<h2 id="section-{num}"><span>{num.zfill(2)}</span>{title}</h2>')
            toc.append(f'<a href="#section-{num}"><span>{num.zfill(2)}</span>{title}</a>')
        else:
            body.append('<p>'+html.escape(stripped)+'</p>')
    elif re.match(r'^\d+\.\d+\s', stripped) and '\n' not in stripped:
        body.append('<h3>'+html.escape(stripped)+'</h3>')
    elif re.match(r'^Step \d', stripped) and '\n' not in stripped:
        body.append('<h4>'+html.escape(stripped)+'</h4>')
    elif any(x in stripped for x in ('⚠', '💡', '📌')):
        body.append('<aside class="note">'+html.escape(re.sub(r'\n\s*', '', stripped))+'</aside>')
    elif re.search(r'\S[ \t]{3,}\S', block) or any(x in block for x in ('──', '│', '┌', '└', 'POST https:', '"subscriber"', '"entitlements"', '"request_date"')):
        # Preserve spacing in source tables and diagrams; allow local horizontal scrolling.
        body.append('<div class="source-block" tabindex="0" role="region" aria-label="原文表格或示意"><pre>'+html.escape(block)+'</pre></div>')
    else:
        # Original line breaks are retained for steps; prose reflows on mobile.
        body.append('<p>'+html.escape(stripped).replace('\n', '<br>')+'</p>')

article = '\n'.join(body)
source_open = '<div class="source-block" tabindex="0" role="region" aria-label="原文表格或示意"><pre>'
article = article.replace('</pre></div>\n'+source_open, '\n\n')
def simple_table(match):
    text = html.unescape(match.group(1))
    chunks = text.split('\n\n')
    if len(chunks) < 2 or any('\n' in x for x in chunks):
        return match.group(0)
    cells = [re.split(r'\s{2,}', x.strip()) for x in chunks]
    if len(cells[0]) < 2 or any(len(row) != len(cells[0]) for row in cells):
        return match.group(0)
    result = '<div class="table-scroll" tabindex="0"><table><thead><tr>'
    result += ''.join('<th>'+html.escape(c)+'</th>' for c in cells[0]) + '</tr></thead><tbody>'
    result += ''.join('<tr>'+''.join('<td>'+html.escape(c)+'</td>' for c in row)+'</tr>' for row in cells[1:])
    return result+'</tbody></table></div>'
article = re.sub(re.escape(source_open)+r'(.*?)</pre></div>', simple_table, article, flags=re.S)
article = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', article)
template = (ROOT/'template.html').read_text()
template = template.replace('{{BODY}}', article).replace('{{TOC}}', '\n'.join(toc))
# Never publish made-up QR codes or unfinished contact placeholders.
if not (ROOT/'assets/wechat.png').exists() or not (ROOT/'assets/twitter.png').exists():
    template = re.sub(r'<section class="contact".*?</section>', '', template, flags=re.S)
    template = re.sub(r'<a class="(?:contact-link|side-contact)".*?</a>', '', template, flags=re.S)
(ROOT/'index.html').write_text(template)
print(f'Converted {len(pages)-1} pages; {section} chapters; {len(blocks)} source blocks. Identifying samples redacted.')
