📌 O QUE CONTÉM NESTE ARQUIVO:

 - O QUE JÁ FOI FEITO FRONTEND.
 - O QUE O FRONTEND AGUARDA DO BACKEND.
 - MELHORIAS PARA O FRONTEND.
 ---------------------------------------------------------------------------------------------
                                O QUE JÁ FOI FEITO NO FRONTEND.

🟢 1. O que já foi feito

O frontend já está estruturado e funcional com as seguintes características:

🧱 Estrutura do projeto
Projeto criado com Next.js + TypeScript
Estilização com Tailwind CSS
Organização por pastas:
app/ → páginas
components/ → componentes reutilizáveis
data/ → dados mockados
types/ → tipagens
🎨 Interface implementada

O dashboard já possui:

Header (status + botão atualizar)
Cards de resumo (ilhas, tempo, etc.)
Navegação por abas
Lista de ilhas em atividade
Painel de Inteligência Artificial
Gráficos (Recharts)

👉 Ou seja: UI completa pronta

📊 Dados atuais
Está usando dados mockados
Simula o comportamento do sistema
Permite desenvolvimento independente do backend
🧠 Arquitetura (muito importante)

O frontend foi feito de forma:

Componentizada
Separada por responsabilidade
Preparada para consumir API

👉 Isso facilita integração depois

🟡 2. Estado atual do frontend
✔️ Funcionando
Interface completa
Layout responsivo
Componentes organizados
Dashboard renderizando corretamente
⚠️ Em desenvolvimento
Dados ainda não vêm do backend
Atualização em tempo real ainda não conectada
Tratamento de loading/erro ainda não implementado
---------------------------------------------------------------------------------------------
                                O QUE O FRONTEND AGUARDA DO BACKEND.

🔵 3. O frontend aguarda do backend
📩 Precisamos que o backend envie:
1. Endpoint principal

Exemplo:

GET /dashboard
2. URL base

Exemplo:

http://localhost:5000
3. Exemplo de resposta (JSON)

Idealmente nesse formato:

{
  "summary": {...},
  "ilhas": [...],
  "ia": {...}
}
4. Estrutura dos dados

Precisamos saber:

nomes dos campos
tipos
estrutura dos objetos
5. Atualização em tempo real

Pergunta:

vai usar WebSocket?
ou atualização por requisição (polling)?
6. Tratamento de erro

Exemplo:

status HTTP (200, 400, 500)
mensagens de erro
🔴 4. IMPORTANTE (decisão técnica)

👉 O backend deve seguir o formato do frontend atual

Por quê?

evita retrabalho
frontend já está pronto
acelera integração
---------------------------------------------------------------------------------------------
                                MELHORIAS PARA O FRONTEND.

🟣 5. Tarefas para dividir no grupo de frontend

Agora sim: dividir trabalho 👇

👤 Pessoa 1 — Integração com API
substituir mock por fetch
conectar endpoint do backend
tratar resposta
mapear dados
👤 Pessoa 2 — Loading e erro
tela de carregamento
mensagem de erro
botão “tentar novamente”
👤 Pessoa 3 — Atualização automática
atualizar dados a cada X segundos
controlar estado de refresh
evitar chamadas duplicadas
👤 Pessoa 4 — UX (melhorias)
filtro por editor
busca por projeto
status visual (livre/ocupado)
melhoria de responsividade
👤 Pessoa 5 (se tiver) — Gráficos
melhorar visual
adicionar métricas
ajustar warnings do Recharts
🟠 6. Melhorias planejadas (próximas)

Quando backend estiver pronto:

🔗 integração com API real
🔄 atualização em tempo real
⚠️ tratamento completo de erro
📊 mais dados nos gráficos
🔍 filtros e busca
🧠 7. Como explicar isso na apresentação


Observação:

“O frontend foi desenvolvido de forma desacoplada, utilizando dados mockados inicialmente, o que permitiu avançar na interface enquanto o backend era desenvolvido. A arquitetura foi pensada para facilitar a integração via API e suportar atualizações em tempo real.”