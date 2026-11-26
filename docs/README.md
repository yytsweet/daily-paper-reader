<div class="dpr-home-notice-card dpr-home-panel">
  <div class="dpr-home-notice-header dpr-home-panel-header">
    <h3 class="dpr-home-notice-title">公告与更新</h3>
    <a class="dpr-home-notice-tutorial" href="#/tutorial/README">使用教程 <span aria-hidden="true">›</span></a>
  </div>
  <div class="dpr-home-notice-entry">
    <time class="dpr-home-notice-date" datetime="2026-10-05">10.05</time>
    <div>
      <strong class="dpr-home-notice-entry-title">medRxiv 自动更新已恢复</strong>
      <span class="dpr-home-notice-entry-summary">修复超长摘要导致的向量生成失败，维护任务现会限制单条 embedding 文本长度并分片写入。受影响范围已重新同步，公开读取、关键词检索与语义检索均已验证。</span>
    </div>
  </div>
  <div class="dpr-home-notice-entry">
    <time class="dpr-home-notice-date" datetime="2026-09-16">09.16</time>
    <div>
      <strong class="dpr-home-notice-entry-title">日报跨日重复推荐已修复</strong>
      <span class="dpr-home-notice-entry-summary">历史推荐现按原始召回标签与 arXiv 论文标识去重，暂停词条不再参与评分；同一专题次日不会重复推荐相同论文。已有历史页面保留，不自动删除。</span>
    </div>
  </div>
  <div class="dpr-home-notice-entry">
    <time class="dpr-home-notice-date" datetime="2026-09-09">09.09</time>
    <div>
      <strong class="dpr-home-notice-entry-title">90天/365天 arXiv 专题回溯</strong>
      <span class="dpr-home-notice-entry-summary">支持分片召回、断点评审与分页查看，核心论文与待复核结果分开展示。DeepSeek 费用按实际用量计算，不下载全量 PDF。</span>
    </div>
  </div>
  <div class="dpr-home-site-stats" data-dpr-site-stats hidden aria-live="polite">
    <span>今天有 <strong class="dpr-home-site-stat-value" data-dpr-daily-readers>--</strong> 人在看论文</span>
    <span class="dpr-home-site-stat-separator" aria-hidden="true">·</span>
    <span>昨天有 <strong class="dpr-home-site-stat-value" data-dpr-yesterday-readers>--</strong> 人在看论文</span>
    <span class="dpr-home-site-stat-separator" aria-hidden="true">·</span>
    <span>已有 <strong class="dpr-home-site-stat-value" data-dpr-fork-count>--</strong> 人加入 Daily Paper Reader</span>
    <span class="dpr-home-history">
      <button type="button" class="dpr-home-history-trigger" data-dpr-history-trigger aria-label="查看最近 14 天阅读趋势"><span aria-hidden="true">🔍</span></button>
      <span class="dpr-home-history-popover" data-dpr-history-popover role="tooltip">
        <span class="dpr-home-history-header">近 14 天阅读趋势</span>
        <span class="dpr-home-history-meta">
          <span data-dpr-history-range>--</span>
          <span>峰值 <strong data-dpr-history-peak>--</strong></span>
        </span>
        <span class="dpr-home-history-chart" data-dpr-history-chart></span>
      </span>
    </span>
  </div>
</div>

<div class="dpr-home-dashboard-grid">
<section class="dpr-home-dashboard-card dpr-home-report-card">
  <div class="dpr-home-dashboard-header">
    <div>
      <span class="dpr-home-dashboard-kicker">2026-11-26</span>
      <h3 class="dpr-home-dashboard-title">今日汇总</h3>
    </div>
    <strong class="dpr-home-dashboard-count">共 19 篇</strong>
  </div>
  <dl class="dpr-home-dashboard-stats">
    <div class="dpr-home-dashboard-stat"><dt>累计更新</dt><dd>1 次</dd></div>
    <div class="dpr-home-dashboard-stat"><dt>精读</dt><dd>7</dd></div>
    <div class="dpr-home-dashboard-stat"><dt>速读</dt><dd>12</dd></div>
  </dl>
  <p class="dpr-home-dashboard-body">最近更新：2026-11-26 19:03:05 UTC<br>状态：成功</p>
</section>
<section class="dpr-home-dashboard-card dpr-home-brief-card">
  <div class="dpr-home-dashboard-header">
    <div>
      <span class="dpr-home-dashboard-kicker">合并后生成</span>
      <h3 class="dpr-home-dashboard-title">今日简报</h3>
    </div>
    <strong class="dpr-home-dashboard-count">AI</strong>
  </div>
  <div class="dpr-home-dashboard-body">
<p>今日精选19篇，精读7篇，重点聚焦LLM量化与视觉-语言-动作（VLA）模型。最值得看的是《Any-Rate》以10.0分提出的半比特多精度量化与编码比特平面方法，以及9.0分的自主叉车卸货VLA落地研究。普通读者可先读这两篇精读，再顺着JEPA-Tuner、ζ₀等速读条目把握VLA从预测微调到异步执行、世界动作模型的最新动向。</p>
  </div>
</section>
<section class="dpr-home-dashboard-card dpr-home-deep-card">
  <div class="dpr-home-dashboard-header">
    <div>
      <span class="dpr-home-dashboard-kicker">今日累计</span>
      <h3 class="dpr-home-dashboard-title">精读推荐</h3>
    </div>
    <strong class="dpr-home-dashboard-count">7 篇</strong>
  </div>
  <div class="dpr-home-dashboard-body">
<ul class="dpr-home-dashboard-paper-list"><li><span class="dpr-home-dashboard-paper-title" title="Any-Rate: Half-Bit Multi-Precision LLM Quantization with Coded Bit-Planes">Any-Rate: Half-Bit Multi-Precision LLM Quantization with Coded Bit-Planes</span></li><li><span class="dpr-home-dashboard-paper-title" title="Integration of Vision-Language-Action Control for Autonomous Forklift Unloading with Limited Real-World Data">Integration of Vision-Language-Action Control for Autonomous Forklift Unloading with Limited Real-World Data</span></li><li><span class="dpr-home-dashboard-paper-title" title="Aegis-VLA: Reliability-Gated Action Refinement via a Trajectory World Model for Dynamic Object Manipulation">Aegis-VLA: Reliability-Gated Action Refinement via a Trajectory World Model for Dynamic Object Manipulation</span></li></ul>
  </div>
  <div class="dpr-home-dashboard-tags"><span class="dpr-home-dashboard-tag">vla-control <strong>6</strong></span><span class="dpr-home-dashboard-tag">quantization <strong>1</strong></span></div>
</section>
<section class="dpr-home-dashboard-card dpr-home-skim-card">
  <div class="dpr-home-dashboard-header">
    <div>
      <span class="dpr-home-dashboard-kicker">今日累计</span>
      <h3 class="dpr-home-dashboard-title">速读推荐</h3>
    </div>
    <strong class="dpr-home-dashboard-count">12 篇</strong>
  </div>
  <div class="dpr-home-dashboard-body">
<ul class="dpr-home-dashboard-paper-list"><li><span class="dpr-home-dashboard-paper-title" title="JEPA-Tuner: From Predictive Fine-Tuning to Asynchronous Execution of Vision-Language-Action Models">JEPA-Tuner: From Predictive Fine-Tuning to Asynchronous Execution of Vision-Language-Action Models</span></li><li><span class="dpr-home-dashboard-paper-title" title="$ζ_0$: A Framework for World Action Models with Joint Scene and Body Foresight in Humanoid Control">$ζ_0$: A Framework for World Action Models with Joint Scene and Body Foresight in Humanoid Control</span></li><li><span class="dpr-home-dashboard-paper-title" title="A2I-VLA: A Two-Stage Vision-Language-Action model with Semantic-Physical Alignment and Integration">A2I-VLA: A Two-Stage Vision-Language-Action model with Semantic-Physical Alignment and Integration</span></li></ul>
  </div>
  <div class="dpr-home-dashboard-tags"><span class="dpr-home-dashboard-tag">vla-control <strong>11</strong></span><span class="dpr-home-dashboard-tag">quantization <strong>1</strong></span></div>
</section>
</div>

<div class="dpr-home-promo-card dpr-home-panel">
  <div class="dpr-home-panel-header">
    <h3 class="dpr-home-promo-title">社区与支持</h3>
  </div>
  <p class="dpr-home-promo-copy">欢迎通过 Star、Fork、Issue 或 PR 一起完善 Daily Paper Reader。</p>
  <div class="dpr-home-promo-meta">
    <span>QQ群 <strong>583867967</strong></span>
    <span class="dpr-home-promo-separator" aria-hidden="true">·</span>
    <span>已有 <strong>1,491</strong> 人参与交流</span>
  </div>
</div>
