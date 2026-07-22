# Insights acionáveis

Os números abaixo são resultados reproduzíveis do snapshot Olist e não textos usados como KPIs estáticos na aplicação.

1. **Atraso está fortemente associado à avaliação.** Pedidos no prazo têm nota média de 4,29, contra 2,57 nos pedidos atrasados. A fila diária deve priorizar categorias com volume relevante e pior prazo antes de campanhas de aquisição.
2. **A recompra é a principal lacuna comercial.** Apenas 3,04% dos clientes fizeram mais de um pedido e o intervalo médio até a segunda compra é de 80,9 dias. Há espaço para jornadas pós-compra segmentadas por categoria e prazo de entrega.
3. **Receita é geograficamente concentrada.** São Paulo representa R$ 5,20 milhões no histórico, muito acima de Rio de Janeiro e Minas Gerais. Comparações operacionais devem separar escala de eficiência para não tratar volume como desempenho.
4. **Cinco categorias lideram o mix.** Beleza e saúde, relógios e presentes, cama/mesa/banho, esporte e lazer e informática/acessórios concentram a maior receita. Elas merecem monitoramento próprio de entrega, avaliação e recompra.
5. **Cartão domina o valor processado.** Aproximadamente R$ 12,54 milhões foram pagos por cartão de crédito, contra R$ 2,87 milhões por boleto. Falhas ou mudanças na experiência de cartão possuem maior impacto potencial, mas valores de pagamento não devem ser confundidos com receita de itens.

## Recomendações

- Criar alertas para categorias com alta receita, queda de pontualidade e avaliação abaixo do padrão.
- Testar comunicação de segunda compra entre 30 e 75 dias após a entrega.
- Comparar estados por ticket, pontualidade e avaliação, além de receita absoluta.
- Acompanhar separadamente mix de pagamento e receita para evitar decisões baseadas em conceitos contábeis diferentes.
- Recalcular os insights após cada reconstrução do pipeline; eles pertencem ao snapshot, não ao layout.
