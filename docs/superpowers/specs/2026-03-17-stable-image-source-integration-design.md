# 稳定图片搜索源接入设计

## 目标

为当前图片抓取工具接入更稳定的官方图片搜索 API，替代完全依赖网页抓取的方案。优先级为：

1. `Pixabay API`
2. `Pexels API`
3. 现有 `DuckDuckGo + Wikimedia` 回退链

目标是提升整体候选图可获得性，特别是饮品相关类型，同时保持程序在未配置 API key 时仍可运行。

## 背景

当前程序虽然已经支持多查询回退，但实际 smoke test 结果表明，`beverage` 类型的所有查询层都返回 0 候选。这说明当前瓶颈更可能在网页抓取 provider 的稳定性，而不是查询词模板本身。

## 范围

### 包含

- 新增 `Pixabay` 查询 provider
- 新增 `Pexels` 查询 provider
- 用环境变量配置 API key
- 在主入口中将 provider 顺序改为 `Pixabay -> Pexels -> DuckDuckGo -> Wikimedia`
- 为 provider 启用条件和请求构造增加测试
- 更新 README，说明如何配置 API key

### 不包含

- 自动申请或管理 API key
- 新增数据库或缓存
- 调整下载和图片处理流程
- 删除旧搜索源

## 设计

### API key 配置

通过环境变量启用官方 API：

- `PIXABAY_API_KEY`
- `PEXELS_API_KEY`

行为规则：

- 有 key 才创建对应 provider
- 没有 key 则跳过该 provider
- 即使两个 key 都没配，程序也仍可回退到现有旧 provider

### Provider 接口

继续沿用当前单查询接口：

```python
def search(self, query: str, item_name: str, limit: int) -> list[CandidateImage]:
    ...
```

这样无需改动多查询回退聚合器。

### Pixabay Provider

- Endpoint: `https://pixabay.com/api/`
- 使用 `key`, `q`, `image_type=photo`, `lang=zh`, `per_page`
- 从响应 `hits[].largeImageURL` 或 `hits[].webformatURL` 中取图 URL

### Pexels Provider

- Endpoint: `https://api.pexels.com/v1/search`
- 使用 `Authorization: <API_KEY>` 请求头
- 使用 `query`, `per_page`
- 从响应 `photos[].src.large` 或 `photos[].src.original` 中取图 URL

### Provider 顺序

实际运行时的单查询 provider 链：

1. `PixabayImageSearchProvider`，如果配置了 key
2. `PexelsImageSearchProvider`，如果配置了 key
3. `DuckDuckGoImageSearchProvider`
4. `WikimediaImageSearchProvider`

### 错误策略

- 单个 provider 请求失败时，抛 `SearchProviderError`
- 外层 `EngineFallbackSearchProvider` 捕获异常并继续下一个 provider
- API 未配置时不报错，直接不启用

## 测试

- `Pixabay` provider 能正确从响应 JSON 提取图片 URL
- `Pexels` provider 能正确从响应 JSON 提取图片 URL
- `main` 在配置环境变量时会把新 provider 放到前面
- 未配置环境变量时不会创建官方 API provider

## 交付结果

完成后，程序应能在配置 API key 后优先使用更稳定的官方图库 API；未配置时仍自动回退到现有来源。
