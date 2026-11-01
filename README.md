# 📚 Dashboard Interativo da Biblioteca Pessoal

Este projeto implementa a **Atividade #3** da disciplina de **Análise e Visualização de Dados (CESAR School - 2026.1)**.

O dashboard foi desenvolvido em **Streamlit** com **Plotly**, apresentando design escuro e moderno inspirado em interfaces analíticas de alta fidelidade (dark slate, neon cyan e hot pink).

---

## 🚀 Funcionalidades Principais

### 1. Visão Geral (Dashboard)
- **Caixa 1 (Total de Livros x Lidos)**: Exibe a quantidade total de livros e a proporção de livros lidos vs. não lidos. Reage dinamicamente às seleções feitas na Caixa 2.
- **Caixa 2 (Livros Físicos x E-books - Interativa)**: Exibe a distribuição entre formatos (Físicos e E-books). Contém um seletor embutido que permite alternar a visualização da **Caixa 1**, **Caixa 3** e dos gráficos para **Todos**, **Apenas Físicos** ou **Apenas E-books**.
- **Caixa 3 (Investimento Total x Livros Lidos)**: Mostra o valor total investido na biblioteca e o valor correspondente aos livros já lidos, calculados com base nos preços da Amazon Brasil.
- **Painel Lateral de Leitura**: Estatísticas de total de páginas, páginas já lidas, média de páginas por livro e avaliação média.
- **Gráfico de Barras por Categoria**: Gráfico interativo em Plotly comparando o total de livros vs. livros lidos para cada categoria literária.
- **Gráficos Complementares**:
  - Donut chart de status geral (% lido).
  - Ranking de investimento por categoria literária.
  - Distribuição das avaliações (notas) atribuídas aos livros lidos.

### 2. Roleta Virtual de Livros Não Lidos
- **Sorteio com 100% dos Livros Não Lidos**: Carrega todos os 121 títulos pendentes da biblioteca (ou filtrados por categoria/formato) com probabilidades idênticas.
- **Visual Limpo & Sem Sobreposição de Texto**: Slices com design estilo roleta de precisão com pinos luminosos, evitando texto amontoado e ilegível.
- **Painel de Destaque em Posição Favorável**: Ticker acima da roleta que acompanha em tempo real o livro que está passando sob o ponteiro a 60 FPS.
- **Física & Áudio**: Física realista de desaceleração (*ease-out*), cliques sonoros sintetizados (*Web Audio API* offline) e fanfarra com confetes ao parar.
- **Modal de Detalhes**: Exibe título, autor, categoria, formato, páginas e valor em reais (Amazon) do livro sorteado.
- **Tabela Transparente & Sorteio Rápido**: Expansor com a lista completa de todos os livros participantes.

### 3. Catálogo Completo & Busca
- Tabela interativa com busca e filtros combinados por categoria, status e tipo de livro.

---

## 🛠️ Como Executar Localmente

No terminal, navegue até a pasta do projeto e execute:

```bash
streamlit run app.py
```

Ou a partir da raiz do repositório:

```bash
streamlit run "c:\CesarSchool\04 - ANÁLISE E VISUALIZAÇÃO DE DADOS\Dashboard\dash_biblioteca\app.py"
```
