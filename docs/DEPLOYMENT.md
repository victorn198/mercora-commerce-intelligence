# Publicação

## Execução local reproduzível

```powershell
run.cmd -m pipeline build
run.cmd -m pipeline validate
run.cmd -m pipeline package
run.cmd app.py
```

O endpoint `/health` confirma que a aplicação e o banco analítico estão disponíveis.

## Plotly Cloud

1. Crie uma conta gratuita no Plotly Cloud.
2. Execute `run.cmd -m pipeline validate` e `run.cmd -m pipeline package`.
3. Dentro de `deploy`, publique com `tool.cmd plotly app publish --project-path . --entrypoint-module wsgi:server`.
4. Configure `APP_ENV=production` e mantenha `DUCKDB_PATH=data/processed/commerce_app.duckdb`.
5. Publique sem autenticação e valide as cinco áreas, os dois idiomas e os links diretos em uma janela anônima.

O banco DuckDB e os marts compactados são derivados anônimos. Os CSVs brutos permanecem fora do repositório. A atribuição CC BY-NC-SA 4.0 deve continuar visível na aplicação e no README.

O comando `pipeline package` recria o diretório `deploy` a partir de uma lista permitida, sem bytecode ou cache. A publicação usa `commerce_app.duckdb`, com aproximadamente 42 MiB, e não inclui CSVs brutos.

## Publicação atual

A aplicação foi publicada e validada em 22/07/2026:

- URL pública: <https://ba9ba428-78e2-4e6e-ac79-8a6dfe44fc99.plotly.app/>
- acesso: público, sem login;
- validação: cinco áreas, links diretos, interface em português e inglês, filtros, drill-down e layout responsivo;
- ponto WSGI: `wsgi:server`.
