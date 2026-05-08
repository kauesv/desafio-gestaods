# Template de Implementação

## Suas Decisões de Design

### 1. Esquema do Banco de Dados

Explique a estrutura do seu modelo e por que você a escolheu.

- Escolhi uma estrutura de banco de dados flexível e desacoplada das regras de negócio, permitindo que a lógica de troca de pontos seja alterada com facilidade. Dessa forma, novas regras ou ajustes podem ser implementados sem a necessidade de modificar o código da aplicação, tornando o sistema mais escalável, de fácil manutenção e adaptável a futuras mudanças de requisitos.

### 2. Arquitetura

Descreva como você organizou o código.

- Qual foi a sua maior preocupação ao implementar a feature?

. Minha principal preocupação foi garantir a consistência no cálculo dos pontos em cenários de concorrência. Por exemplo, caso o cliente finalize um aluguel e imediatamente realize outro, o sistema pode ainda estar processando os cálculos anteriores, o que poderia gerar inconsistências na pontuação, como perda ou duplicidade de pontos. Para mitigar esse tipo de problema, considerei estratégias como utilização de cache, filas de processamento assíncrono ou até regras de bloqueio temporário para novos aluguéis até a finalização completa do processamento anterior. Essas abordagens ajudam a garantir integridade e confiabilidade nos dados.

- Como você lidou com os cálculos de pontos?

. Os cálculos de pontos foram organizados de forma centralizada e desacoplada das demais regras da aplicação. Como as regras de pontuação estão bem estruturadas e os relacionamentos entre as entidades foram modelados de forma consistente, consigo navegar facilmente pelos dados necessários para realizar os cálculos. Além disso, com as informações iniciais do aluguel já disponíveis, o sistema consegue processar os pontos de forma clara, previsível e com facilidade para futuras adaptações nas regras de negócio.

###3. Abordagem de Integração

Explique como você integrou com o código existente.

- Como você manteve retrocompatibilidade?

. A integração foi construída em torno da entidade principal do sistema, que é o aluguel. Antes de iniciar a implementação, foi necessário compreender o fluxo já existente, identificar como as regras atuais funcionavam e entender os impactos que a nova feature poderia causar na aplicação. Com esse entendimento, desenvolvi a solução de forma integrada ao fluxo atual, evitando alterações desnecessárias na estrutura já consolidada do sistema.

## Estratégia de Testes

Descreva sua abordagem de testes:

- Quais casos e tipos de teste você implementou?

- Testes relacionados ao negócio principal é que é gamificação e o aluguél

## Como Testar

Forneça instruções passo a passo para testar sua funcionalidade:

```bash
python manage.py test rentals
python manage.py test core
python manage.py test gamifications
python manage.py test users
python manage.py test
```

## Suposições (assumptions) Feitas

Liste quaisquer suposições que você fez sobre requisitos não claros:

1. A lógica de aplicação de pontos na locação foi adaptada para funcionar automaticamente no momento da devolução do veículo. Assim que o aluguel é finalizado, o processo de cálculo e aplicação dos pontos é iniciado automaticamente. Com essa abordagem, entendi que não seria necessário implementar separadamente a funcionalidade de resgate manual de pontos.
2. A estrutura das rotas da API foi reorganizada para utilizar versionamento através do prefixo /v1/, removendo o /api/ existente anteriormente. Essa alteração foi feita pensando em padronização, organização e facilidade de evolução futura da API.
3. 

## O Que Eu Melhoraria Com Mais Tempo

Seja honesto sobre o que você faria diferente ou adicionaria:

- Implementaria um sistema de filas e cache para evitar problemas de concorrência durante o cálculo de pontos, garantindo maior consistência e confiabilidade nos processos executados simultaneamente.
- Utilizaria um banco de dados mais robusto, como o PostgreSQL, que possui excelente integração com o Django e oferece melhores recursos de performance, integridade e escalabilidade para aplicações maiores.
- Otimizaria o processo de exportação de CSV, reduzindo a quantidade de consultas ao banco de dados e melhorando a eficiência da geração dos arquivos.
- Melhoraria a organização dos dados exportados, deixando os arquivos CSV mais estruturados, legíveis e fáceis de consumir.
- Implementaria uma rotina de limpeza automática para remover arquivos exportados quando o objeto relacionado fosse excluído, evitando acúmulo de arquivos desnecessários e reduzindo lixo no armazenamento.

## Notas

Quaisquer notas adicionais, avaliações, desafios enfrentados ou decisões interessantes:

- O desafio foi muito interessante, bem estruturado e com requisitos claros, o que facilitou o entendimento da proposta e permitiu focar mais na qualidade da implementação.
- O principal desafio foi definir e implementar corretamente a lógica de cálculo dos pontos, garantindo que os resultados fossem retornados exatamente conforme esperado pelos requisitos. Apesar da complexidade das regras, a modelagem adotada ajudou a tornar a implementação mais organizada e previsível.
- Uma decisão importante de arquitetura foi tornar o modelo de usuário mais flexível, permitindo que o mesmo sistema suportasse diferentes tipos de usuários, como funcionários e clientes, utilizando uma única entidade diferenciada apenas por permissões ou flags de controle. Isso reduz duplicação de estrutura, simplifica manutenção e facilita futuras expansões do sistema.
