# Verificação da entrega

## Dados

- 99.441 pedidos, 112.650 itens e 103.886 pagamentos processados.
- Receita dos itens reconciliada entre fato, mart de pedidos e mart de linhas.
- Chaves de pedidos, itens e pagamentos únicas.
- Nenhum órfão entre itens/pagamentos e pedidos.
- Nenhuma coluna de nome, email, telefone, CPF ou identificador original do cliente no banco publicado.
- Hashes de clientes são únicos e campos críticos de pedidos/itens estão preenchidos.
- Datas operacionais permanecem limitadas ao período histórico original.
- Datas históricas apresentadas por meio de uma data operacional explícita.

## Aplicação

- As cinco áreas foram abertas e verificadas no navegador.
- A busca por `adf327` encontrou o identificador anônimo `adf327cc8269` e seu histórico.
- A janela de 30 para 7 dias alterou a receita de R$ 814.133 para R$ 29.236 no snapshot validado.
- O clique em uma barra de categoria aplicou `alimentos` ao contexto global.
- Carregamento local medido em aproximadamente 1,0 segundo.
- Interação aquecida medida em aproximadamente 526 ms.

## Automação

- `python -m compileall`: aprovado.
- `pytest`: 16 aprovados e 1 teste de navegador ignorado por padrão.
- O cenário de navegador usa o servidor `dash.testing` e pode ser ativado com `RUN_BROWSER_E2E=1` em uma máquina que permita sessões headless.
- Navegação, filtros, cliques e busca foram adicionalmente validados no navegador integrado.

## Capturas

- Português: [Command Center](images/pt/command.png), [Revenue Explorer](images/pt/revenue.png), [Retention](images/pt/retention.png), [Customer Explorer](images/pt/customers.png) e [Data Trust](images/pt/trust.png).
- Inglês: [Command Center](images/en/command.png), [Revenue Explorer](images/en/revenue.png), [Retention](images/en/retention.png), [Customer Explorer](images/en/customers.png) e [Data Trust](images/en/trust.png).
