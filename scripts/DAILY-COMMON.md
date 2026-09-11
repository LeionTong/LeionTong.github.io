# DAILY-COMMON.md — 三个 Daily 栏目（AI / GitHub / Terminal）共享规范

> 各栏目 prompt 只保留差异化逻辑（检索 / 评分 / 扇区 / 输出格式），跨栏目硬约束全部在本文件。
> 本文件随站点仓库 `LeionTong.github.io-hugo` 走 git 备份（公开仓库），故正文不含任何内部代号；
> 具体的内部示例由各栏目 prompt（本地私有）自行补充，以 prompt 为准。
> **执行前必须读取本文件并严格遵守；文件缺失或读取失败则中止并在摘要中报告，不得凭记忆套用样式或红线。**
> 2026-09-11 规整：共享数据在 `scripts\`（见第零节变量）；单期 md 归档为临时目录 `<TEMPMD>`，同步成功即删，不入 git；`daily-shared` 目录已废除。

## 零、路径与环境约定（全文通用变量）

- `<HUGO>` = `C:\Users\Leion\T\LeionTong.github.io-hugo` — 站点仓库根（`scripts\` 随其 git 备份）
- `<COMMON>` = `<HUGO>\scripts\DAILY-COMMON.md` — 本文件
- `<TEMPMD>` = `C:\Users\Leion\AppData\Local\Temp\daily-md\` — 单期干净 md 临时归档（ima 同步源）：同步成功即删，失败保留重试，不入 git
- `<DATA>` = `<HUGO>\scripts\<栏目>-daily\` — 去重日志与工作档案（pushed-*.md、Terminal 月度 md、sector-cursor.md）
- `<IMA>` = `<HUGO>\scripts\ima\sync-to-ima.cjs` — ima 同步脚本（`ima\` 目录自包含，可整体搬移）
- 解释器与工具一律用 PATH 上的通用命令：`python`（≥3.11）、`node`（≥20）、`hugo`、`git`、`gh`。**禁止**绑定任何捆绑解释器或特定应用私有目录的绝对路径。
- 「今天」一律按本机本地时区 Asia/Shanghai（UTC+8）判定。

## 一、署名红线（最高优先级，公开发布物）

- 所有成品署名一律使用 `Leion`；品牌头保持大写（如 `LEION · DAILY AI` / `LEION DAILY BRIEF`）。
- 允许形态：`Leion` / `LEION · DAILY AI` / `LEION DAILY BRIEF` / `Leion · NO.XX` / `整理：Leion` / `编制 Leion` / `reviewer → Leion`。
- 禁止形态：任何昵称或内部称呼（具体清单以各栏目 prompt 本地版为准）、占位式签名（自动化推送、AUTOMATED BRIEF）、AI 自称、emoji 署名。
- 页脚时间格式：`· YYYY-MM-DD HH:MM GMT+8`，不加除 Leion 以外的个人信息。

## 二、内容红线（最高优先级，公开物零泄漏）

成品是公开发布内容（公共网站 + 公开知识库 + 公众号草稿），严禁任何内部视角：

- 禁止任何阶段代号、内部评估框架及其缩写（具体代号与框架名以各栏目 prompt 本地版为准）。
- 禁止内部在评估 / 接触的公司标的（具体清单以各栏目 prompt 本地版为准）带「我方评估 / 候选 / 对比」视角；可客观陈述事实，不得带内部判定。
- 禁止自家未公开产品代号、客户清单与打法、个人称谓与身份信息、内部日程与工作内容。
- 禁止「对内部阶段框架的映射 / 意义」「我方应如何应对」等句式；改写为第三人称中性行业判断（「这意味着…」「对行业的含义是…」），只基于公开信息推理。
- 禁止「仅供内部参阅」这类内部分发措辞，改用「仅供参考」或不写。
- 凡带内部视角一律禁止；剥离后无话可说就不写，不硬凑。

## 三、文风红线（禁止 AI 腔套话）

成品读起来像人写给人看的行业笔记，不是模板自媒体。生成后自查四类禁止：

1. 数量概括式起句 / 收句（「今天五条信号…」「今日 N 仓…」）→ 直接说判断本身，不用「N 条信号」架空主语。
2. 标题党式主标题（冒号总起 / 对仗 / 造词）→ 平实陈述短语。
3. 强行升华的排比对仗金句（「稀缺的从来不是 X，而是 Y」）→ 说完即停，不加人生感悟。
4. 比喻性小标题 / 拟人包装（「XX 的老账 / 地基 / 账单」）→ 直接陈述事实对象。

判断标准：删掉一句只损失「气势」、不损失具体信息，就该删。宁可平淡，不要漂亮。

## 四、墨水瓶（E-Ink）页面样式（硬性）

生成单期 HTML 时，`<style>` 必须**原样读取并套用**基线文件 `<HUGO>\scripts\eink-base.css` 全部内容，不得改写已有规则；只允许在正文区增补结构 class；**严禁**复制历史页面 `<style>` 来复用。

基线已覆盖的 class（按栏目取用，不限于）：`sheet` / `masthead` / `mh-top` / `mh-sub` / `spec-strip` / `spec-cell` / `spec-k` / `spec-v` / `lede` / `lede-title` / `sec-head` / `card` / `c-num` / `c-title` / `c-tags` / `chip` / `blk` / `blk-k` / `why` / `datum` / `figure` / `fig-cap` / `cross` / `verdict` / `risk` / `footer` / `entry` / `entry-no` / `e-head` / `e-name` / `e-meta` / `tag` / `e-line` / `scores` / `sc` / `bar` / `sc-v` / `wsum` / `tail` / `colophon`。Terminal 用 `.entry` 条目式（非宽表格，避免墨水屏横向溢出）。

禁止出现（墨水屏糊成脏块 / 残影）：

- `linear-gradient` / `radial-gradient` / `repeating-linear-gradient`
- `box-shadow` / `text-shadow` / `filter` / `backdrop-filter`
- `animation` / `transition` / `@keyframes`
- `alpha < 1` 的半透明叠层（如 `rgba(255,255,255,.5)`）
- `position: fixed`
- 装饰性 `transform`（如胶带 rotate）
- 外部字体（`fonts.googleapis.com` 等），一律系统字体栈
- `prefers-color-scheme: dark` 分支（站点只保留浅色）

必须满足：

- 底色纯白 `#ffffff`，正文 `#000000`，不出现深色背景块
- 正文字号 ≥ 17px，最小字号 ≥ 13px，行高 ≥ 1.8
- 正文对比度 ≥ 7:1，次要文字（日期 / 标签 / 脚注）≥ 4.5:1
- 层级靠边框粗细 / 字重 / 留白 / 实虚线区分，不靠颜色；用色则各色转灰后明度差必须明显

## 五、Hugo 发布流程（幂等，三栏目通用）

1. 单期 HTML 写入对应 static 目录（文件名 `YYYY-MM-DD-HHMM.html`，HHMM 用实际生成时间）：
   - Daily-AI → `<HUGO>\static\daily-ai\`
   - Daily-Github → `<HUGO>\static\daily-github\`
   - Daily-Terminal → `<HUGO>\static\daily-terminal\`
2. 重建栏目索引（幂等，可反复执行）：
   - AI：`python <HUGO>\scripts\publish_daily_ai.py --all`
   - Github：`python <HUGO>\scripts\publish_daily_github.py --all`
   - Terminal：`python <HUGO>\scripts\publish_daily_terminal.py --all`
   - 注意：`publish_daily_ai.py` 默认从 `<TEMPMD>` 取源报告（可用环境变量 `DAILY_AI_SRC_DIR` 覆盖，一般无需理会——新流程 HTML 直写 static，索引由 static 回填）；若对 static 下页面做过手工修订，勿直接跑该脚本覆盖，改手工编辑 `content/daily-ai/_index.md`。其余两个脚本只扫描 static 重建索引，无此问题。
3. 本地构建校验（必须零 ERROR）：先 cd 到 `<HUGO>`，再执行 `hugo --minify`。
   （PaperMod 的 `.Language.LanguageCode` / `.Language.LanguageDirection` deprecation WARN 属已知噪音，忽略。）
4. 校验通过后提交并推送（gh-pages 由 Actions 自动构建，`public/` 不入库）：
   `git add -A && git commit -m "<栏目>: <期次与一句话主题>" && git push origin master`
   - 推送必须免交互：远程优先 SSH（`git@github.com:LeionTong/LeionTong.github.io.git`），未配置 SSH 时用 gh 提供的凭据助手，二者取其一，不得弹 credential helper 卡住。
   - 任一环节失败：已完成的 ima 同步不受影响，简报照常输出，末尾注明失败环节。

## 六、IMA 知识库同步（通用命令）

同步脚本三栏目共用，一律走脚本，不得自行拆解 ima 底层 API：

```
node <IMA> --file "<当日归档 md 绝对路径>" --kb "<知识库名>"
```

- `<知识库名>`：Daily-AI / Daily-Github / Daily-Terminal（按栏目）
- 凭证：`~/.config/ima/client_id` 与 `api_key`，或环境变量 `IMA_OPENAPI_CLIENTID` / `IMA_OPENAPI_APIKEY`
- 同步前须生成一份**干净 Markdown 归档**（纯文本、不含内联 CSS，供知识库检索），写入 `<TEMPMD>`（目录不存在则创建）；文件名以各栏目 prompt 为准（如 `GitHub每日优质项目-YYYY-MM-DD.md` / `Daily-AI-YYYY-MM-DD.md`）。同步成功后删除该文件；失败或跳过则保留，供重试与排查。临时目录不入 git。
- 成功判定：退出码 0 且 stdout 含 `{"ok":true,...}`
- 失败（非 0 或 ok=false）最多重试 1 次；仍失败在摘要末尾追加 `ima 同步失败：<message>`，不中断主流程
- 知识库不存在（脚本报「未找到知识库」）则跳过同步，摘要末尾追加 `ima 同步跳过：知识库「<名>」不存在，需在 ima 侧手动创建`
- Daily-Terminal 知识库截至 2026-09-11 尚未在 ima 创建，属预期降级，不影响其余环节

## 七、降级通则

- 任何单环节失败不得影响其余环节，也不得省略对话摘要。
- 外部依赖（gh / 网络 / ima / 代理）不可用时，明确标注失败原因与降级动作，**禁止编造数据**（stars / 日期 / License 等必须来自当天实测）。
