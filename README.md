# Musiq+ – Sistema de recomendação por conteúdo (Músicas)

## Objetivo

Desenvolver um sistema de recomendação de músicas usando **filtragem baseada em conteúdo**, com:

- Backend em **FastAPI**
- Frontend em **Streamlit**
- Avaliação por **Precision, Recall e F1-score**

## Como rodar o backend e o frontend

### 1. Pré-requisitos

- Python 3.10+  
- `pip` instalado  
- (Opcional) Ambiente virtual (`venv`)

### 2. Instalar dependências

``pip install -r requirements.txt``

### 3. Gerar os arquivos CSV

A partir da raiz do projeto:

``python backend/data/setup_data.py``

Execute o script de setup para criar:

- **itens.csv** – catálogo de músicas e seus atributos;
- **avaliacoes.csv**: gabarito com usuários simulados (não interativos)
- **usuarios.csv**: avaliações reais feitas na interface (inicialmente vazio)

### 4. Rodar o backend (FastAPI)

A partir da raiz do projeto:

``uvicorn backend.app:app --reload``

Backend disponível em: http://localhost:8000

Endpoints principais:

- GET /itens
- GET /usuarios
- POST /usuarios
- POST /avaliar
- POST /recomendar
- GET /metricas/{usuario_id}
- GET /analise_usuario/{usuario_id}

### 5. Rodar o frontend (Streamlit)

Em outro terminal, na raiz do projeto:

``streamlit run frontend/streamlit_app.py``

## Como foi feita a vetorização

A vetorização dos itens é feita no arquivo **backend/recommender.py** usando **TF-IDF**.

Cada música do itens.csv possui atributos de conteúdo, como:

- gênero (genero)
- tags (tags)
- palavra-chave (palavra_chave)
- humor (humor)
- instrumentação (instrumentacao)
- idioma (idioma)
- descrição (descricao)

Esses campos são concatenados em um campo textual único:

```
feature_text = genero + tags + palavra_chave + humor + instrumentacao + idioma + descricao
```

Aplicamos TfidfVectorizer (scikit-learn) sobre feature_text, com stopwords em português, gerando um vetor numérico para cada música:

```
_vectorizer = TfidfVectorizer(stop_words=stopwords_pt)
_item_matrix = _vectorizer.fit_transform(itens["feature_text"])
```

O resultado é uma **matriz TF-IDF**, onde cada linha representa um item e cada coluna representa um termo.

As avaliações de usuários não entram nesse processo: a vetorização é feita somente a partir dos atributos de conteúdo das músicas, conforme exigido no trabalho.

## Como o perfil do usuário é construído

O perfil de um usuário é construído a partir das músicas que ele curtiu (likes) no sistema.

As interações dos usuários reais são salvas em usuarios.csv, com colunas:

- usuario_id
- nome
- item_id
- gostou (1 para like, 0 para dislike)
- origem ("inicio", "recomendador" ou "outro")

Para um usuário específico, selecionamos todos os item_id onde gostou == 1 (independente da origem):

```
liked_ids = usuarios_df[
    (usuarios_df["usuario_id"] == usuario_id) & (usuarios_df["gostou"] == 1)
]["item_id"].unique()
```

Recuperamos os **vetores TF-IDF** desses itens na **matriz _item_matrix**.

O perfil do usuário é calculado como a média desses vetores:

```
profile = mean(vetores_dos_itens_curtidos)
```

Esse vetor médio representa o “gosto” do usuário em termos de gêneros, tags, humor, idioma etc. Assim, o perfil é totalmente baseado em conteúdo dos itens curtidos, não nas notas em si.

## Métrica de similaridade escolhida

A métrica de similaridade escolhida foi a **similaridade do cosseno (cosine_similarity)**.

Para cada item candidato:

Temos:

- vetor do perfil do usuário (profile)
- vetor TF-IDF da música candidata (v_item)

A similaridade é calculada como:

```
sim = cosine_similarity(profile.reshape(1, -1), v_item.reshape(1, -1))[0, 0]
```

As músicas são ordenadas em ordem decrescente de similaridade, e as top_k são retornadas como recomendações.

## Cálculo de Precision, Recall e F1-score

As métricas são calculadas usando:

- **avaliacoes.csv**: gabarito com usuários simulados (não interativos)
- **usuarios.csv**: avaliações reais feitas na interface (apenas as da aba Recomendador)

### 1. Definição de itens relevantes (gabarito)

A partir de **avaliacoes.csv**, o sistema calcula a média de gostou por item.

Um item é considerado relevante globalmente se:

``média(gostou) >= 0.5``

O conjunto relevantes é o conjunto de todos os itens considerados relevantes pelo gabarito.

### 2. Itens recomendados e hits

Para cada usuário real (usuario_id em usuarios.csv):

São consideradas apenas as avaliações com origem == "recomendador":

```
regs_rec = regs_usuario[regs_usuario["origem"] == "recomendador"]
```

**recomendados** = conjunto de item_id avaliados na aba Recomendador.

Um hit é uma linha em regs_rec que satisfaz:

- item_id está em relevantes e
- gostou == 1.

### 3. Fórmulas

- n_recomendados = número de itens recomendados avaliados na aba Recomendador
- n_relevantes = total de itens relevantes no gabarito

**hits** = número de itens relevantes que o usuário gostou entre os recomendados

Então:

- Precision

$$
Precision = \frac{hits}{n\_recomendados}
$$

- Recall

$$
Recall = \frac{hits}{n\_relevantes}
$$

- F1-Score

$$
F1 = \frac{2 . Precision . Recall}{Precision + Recall}
$$

## Interpretação dos resultados

Em testes com o dataset atual (30 músicas e 10 usuários de gabarito), os valores de F1-score típicos ficaram, por usuário, na faixa de aproximadamente **0,18 a 0,35**.

Já era esperado considerando:

- **Catálogo pequeno**: poucas músicas disponíveis limitam o número de recomendações e hits possíveis.
- **Gabarito global**: os itens relevantes são definidos globalmente (com base em vários usuários simulados), o que torna a lista de relevantes relativamente grande e o recall mais difícil.
- **Poucas avaliações na aba Recomendador**: cada usuário real avalia um número pequeno de recomendações, o que torna as métricas sensíveis a poucos acertos/erros.