# Plugins

Plugin-oriented architecture keeps the core SDK stable while enabling domain specialization.

## Plugin surfaces

- Model adapters (`ModelAdapter`)
- Data connectors (`DataSource`)
- Ranking strategies (`ranking_strategy`)

## Registry

Use `PluginRegistry` to register and instantiate plugin factories by name.

```python
registry.register_model_adapter("openai", lambda: OpenAIModelAdapter())
registry.register_data_source("crm_connector", lambda: CRMConnector())
registry.register_ranking_strategy("cost_aware", lambda: cost_aware_strategy)
```
