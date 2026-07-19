# Paper2 LLM / 人工验证编码规则

## 目标

这个验证不是为了替代主模型，也不是为了证明词典法超过 LLM。

目标只有一个：回应主编关于 SOTA/LLM baseline 的意见，说明词典命中的 GenAI 片段是否真正涉及企业层面的 GenAI 采用、部署或应用。

## 输入文件

`LLM_validation_sample.csv`

样本构成：

- 140 条 MD&A 片段。
- 60 条原规则标签为 substantive。
- 60 条原规则标签为 generic。
- 20 条原规则标签为 strategic。

## 标注字段

### human_or_llm_label

只能填以下三类：

- `substantive_adoption`
- `generic_or_background`
- `unclear`

### confidence_1_5

置信度：

- 5 = 非常确定。
- 4 = 比较确定。
- 3 = 有一定不确定。
- 2 = 较不确定。
- 1 = 基本猜测。

### rationale_cn

用一句中文说明理由。

## 三类标签定义

### substantive_adoption

文本明确说明企业已经、正在或具体计划将 GenAI / 大模型 / AIGC / LLM 用于某个业务、产品、系统、平台或流程。

典型证据：

- 已开发大模型应用。
- 已上线 AI 平台。
- 已将 ChatGPT / 大模型 / AIGC 用于生产、运营、研发、客服、供应链、合同、预测等环节。
- 提到具体产品、系统、场景、客户、项目、专利、应用数量、效果数字。

### generic_or_background

文本只是讲行业趋势、政策背景、技术概念、市场机会，不能证明该企业自身已经采用或部署 GenAI。

典型情况：

- “随着人工智能快速发展……”
- “ChatGPT 引发行业关注……”
- “公司将关注人工智能趋势……”
- 只说宏观背景，没有企业自身应用动作。

### unclear

文本太短、信息不完整，无法判断是否属于企业真实采用。

## 判断原则

1. 只根据当前片段判断，不要脑补企业背景。
2. 企业自身动作优先于行业背景。
3. 有具体系统、平台、场景、项目、数量、效果时，倾向 `substantive_adoption`。
4. 只有“关注、探索、布局、趋势、政策、行业发展”时，倾向 `generic_or_background`。
5. 如果文本中只有传统 AI，没有生成式 AI、大模型、AIGC、LLM、ChatGPT、GPT、智能体等明确线索，要谨慎。

## 后续统计

标注完成后，至少统计：

- dictionary substantive 与 human/LLM substantive 的 agreement。
- dictionary generic 与 human/LLM generic 的 agreement。
- overall agreement。
- precision。
- recall。
- F1。

这些指标用于正文 validation，不用于改动主面板。
