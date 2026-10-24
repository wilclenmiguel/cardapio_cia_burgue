"""
Cardápio online - Na Chapa & Cia (Streamlit)

Fluxo: cardápio -> dados do cliente -> confirmação (botão que abre o WhatsApp do restaurante
com o resumo do pedido).

Requer Streamlit >= 1.29 (st.link_button).
"""
from urllib.parse import quote

import pandas as pd
import streamlit as st

# ======================= CONFIGURAÇÃO =======================
# Número do WhatsApp do restaurante: DDI + DDD + número, só dígitos (ex.: 5531999999999)
NUMERO_RESTAURANTE = "5531973328780"
NOME_RESTAURANTE = "Na Chapa & Cia"
# ============================================================

PLACEHOLDER_BAIRRO = "Selecione o bairro"
PLACEHOLDER_PAGAMENTO = "Selecione"
VALORES_VAZIOS = {"", PLACEHOLDER_BAIRRO, PLACEHOLDER_PAGAMENTO}


# ---------------------- funções auxiliares ----------------------
def brl(valor):
    """Formata um número como moeda brasileira: 1234.5 -> 'R$ 1234,50'."""
    return f"R$ {valor:.2f}".replace(".", ",")


def adicionar_ao_carrinho(produto):  # função para adicionar produtos ao carrinho de compras
    produto_encontrado = False
    for item in st.session_state.carrinho:
        if item["Produto"] == produto["Produto"]:
            item["quantidade"] += 1
            produto_encontrado = True
            break
    if produto_encontrado == False:
        st.session_state.carrinho.append(
            {"Produto": produto["Produto"],
             "Preço": produto["Preço (R$)"],
             "quantidade": 1}
        )


def total_itens():
    """Soma dos itens do carrinho (sem a taxa de entrega)."""
    return sum(p["Preço"] * p["quantidade"] for p in st.session_state.carrinho)


def campos_faltando(dados):
    """Retorna a lista de campos obrigatórios que ainda não foram preenchidos."""
    obrigatorios = ["Nome", "Telefone", "Rua", "Numero", "Bairro", "Cidade", "Forma de pagamento"]
    faltando = []
    for campo in obrigatorios:
        if str(dados.get(campo, "")).strip() in VALORES_VAZIOS:
            faltando.append(campo)
    return faltando


def montar_mensagem(dados, carrinho, taxa_entrega):
    """Monta o texto do pedido que será enviado ao WhatsApp do restaurante."""
    subtotal = sum(p["Preço"] * p["quantidade"] for p in carrinho)
    total = subtotal + taxa_entrega

    linhas = [f"*Novo pedido - {NOME_RESTAURANTE}*", ""]
    linhas.append(f"*Cliente:* {dados['Nome']}")
    linhas.append(f"*Telefone:* {dados['Telefone']}")
    linhas.append(
        f"*Endereço:* {dados['Rua']}, {dados['Numero']} - {dados['Bairro']}, {dados['Cidade']}"
    )
    linhas.append("")
    linhas.append("*Itens:*")
    for p in carrinho:
        linhas.append(f"• {p['quantidade']}x {p['Produto']} - {brl(p['Preço'] * p['quantidade'])}")
    linhas.append("")
    linhas.append(f"Subtotal: {brl(subtotal)}")
    linhas.append(f"Taxa de entrega ({dados['Bairro']}): {brl(taxa_entrega)}")
    linhas.append(f"*Total: {brl(total)}*")
    linhas.append("")
    linhas.append(f"*Pagamento:* {dados['Forma de pagamento']}")
    if dados["Forma de pagamento"] == "Dinheiro" and str(dados.get("Troco", "")).strip():
        linhas.append(f"*Troco para:* R$ {str(dados['Troco']).strip()}")
    if str(dados.get("Observação", "")).strip():
        linhas.append(f"*Observação:* {dados['Observação'].strip()}")
    return "\n".join(linhas)


def link_whatsapp(mensagem):
    """Link que abre a conversa com o restaurante já com a mensagem escrita."""
    return f"https://wa.me/{NUMERO_RESTAURANTE}?text={quote(mensagem)}"


# ---------------------- dados e estado ----------------------
df_bairros = pd.read_excel("frete_bairros.xlsx")
df_bairros.columns = df_bairros.columns.str.strip()
# Cria um dicionário no formato { "Nome do Bairro": Valor_da_Taxa }
taxas_bairros = dict(zip(df_bairros["bairros"], df_bairros["frete"]))

# Lista para a caixa de seleção
lista_bairros = [PLACEHOLDER_BAIRRO] + list(taxas_bairros.keys())

if "carrinho" not in st.session_state:
    st.session_state.carrinho = []  # inicializa o carrinho de compras como uma lista vazia e nao e deixa o cliente perder os itens selecionados ao atualizar a página

# dados do cliente
if "dados_cliente" not in st.session_state:
    st.session_state.dados_cliente = {
        "Nome": "",
        "Telefone": "",
        "Rua": "",
        "Numero": "",
        "Bairro": "",
        "Cidade": "",
        "Forma de pagamento": "",
        "Observação": "",
        "Troco": ""
    }

# pagina atual do cardapio: "cardapio" -> "dados" -> "confirmacao"
if "pagina" not in st.session_state:
    st.session_state.pagina = "cardapio"

cardapio = pd.read_excel("cardapio_online.xlsx", sheet_name="Cardapio")  # abre a planilha e carrega os dados do cardápio

# ====================== PÁGINA 1: CARDÁPIO ======================
if st.session_state.pagina == "cardapio":
    st.title("🍔 Na Chapa & Cia")
    st.write("Bem-vindo ao nosso cardapio online!")
    st.write("Escolha seus produtos e faça seu pedido.")

    # sanduíches
    st.header("🍔 Sanduíches")
    sanduiches = cardapio[cardapio["Categoria"] == "Sanduíches"]
    for indice, produto in sanduiches.iterrows():
        st.image(produto["fotos"], width=100)
        st.subheader(produto["Produto"])
        st.write(produto["Descrição / Opções"])
        st.write(f'R$ {produto["Preço (R$)"]:.2f}')
        if st.button("Adicionar ao carrinho", key=f"sanduiche_{indice}"):  # ao clicar no botão, o produto é adicionado ao carrinho de compras
            adicionar_ao_carrinho(produto)
            st.success("Produto adicionado ao carrinho!")
    st.divider()

    # BATATA FRITA
    st.header("🍟 Batata Frita")
    batatas = cardapio[cardapio["Categoria"] == "Batata Frita"]
    for indice, produto in batatas.iterrows():
        st.image(produto["fotos"], width=100)
        st.subheader(produto["Produto"])
        st.write(produto["Descrição / Opções"])
        st.write(f'R$ {produto["Preço (R$)"]:.2f}')
        if st.button("Adicionar ao carrinho", key=f"batata_{indice}"):
            adicionar_ao_carrinho(produto)
            st.success("Produto adicionado ao carrinho!")
    st.divider()

    # ACRÉSCIMOS
    st.header("➕ Acréscimos")
    acrescimos = cardapio[cardapio["Categoria"] == "Acréscimos"]
    for indice, produto in acrescimos.iterrows():
        st.image(produto["fotos"], width=100)
        st.subheader(produto["Produto"])
        st.write(produto["Descrição / Opções"])
        st.write(f'R$ {produto["Preço (R$)"]:.2f}')
        if st.button("Adicionar ao carrinho", key=f"acrescimo_{indice}"):
            adicionar_ao_carrinho(produto)
            st.success("Produto adicionado ao carrinho!")
    st.divider()

    # BEBIDAS
    st.header("🥤 Bebidas")
    bebidas = cardapio[cardapio["Categoria"] == "Bebidas"]
    for indice, produto in bebidas.iterrows():
        st.image(produto["fotos"], width=100)
        st.subheader(produto["Produto"])
        st.write(produto["Descrição / Opções"])
        st.write(f'R$ {produto["Preço (R$)"]:.2f}')
        if st.button("Adicionar ao carrinho", key=f"bebida_{indice}"):
            adicionar_ao_carrinho(produto)
            st.success("Produto adicionado ao carrinho!")
    st.divider()

    # CERVEJAS
    st.header("🍺 Cervejas")
    cervejas = cardapio[cardapio["Categoria"] == "Cervejas"]
    for indice, produto in cervejas.iterrows():
        st.image(produto["fotos"], width=100)
        st.subheader(produto["Produto"])
        st.write(produto["Descrição / Opções"])
        st.write(f'R$ {produto["Preço (R$)"]:.2f}')
        if st.button("Adicionar ao carrinho", key=f"cerveja_{indice}"):
            adicionar_ao_carrinho(produto)
            st.success("Produto adicionado ao carrinho!")
    st.divider()

    # CARRINHO DE COMPRAS
    st.sidebar.header("🛒 Seu pedido")
    for indice, produto in enumerate(st.session_state.carrinho):
        st.sidebar.write(f"{produto['quantidade']} x {produto['Produto']}")
        subtotal = produto["Preço"] * produto["quantidade"]
        st.sidebar.write(brl(subtotal))
        if st.sidebar.button("➖ Remover", key=f"remover_{indice}"):  # ao clicar no botão, o produto é removido do carrinho de compras
            produto["quantidade"] -= 1
            if produto["quantidade"] == 0:
                st.session_state.carrinho.pop(indice)  # remove o produto do carrinho se a quantidade for igual a zero
            st.rerun()
    st.sidebar.divider()
    st.sidebar.subheader(f"Total: {brl(total_itens())}")
    if len(st.session_state.carrinho) > 0:
        if st.sidebar.button("➡️ Avançar para os dados", type="primary"):
            st.session_state.pagina = "dados"
            st.rerun()

# ====================== PÁGINA 2: DADOS DO CLIENTE ======================
elif st.session_state.pagina == "dados":
    st.title("👤 Dados do cliente")
    st.write("Preencha seus dados para continuar com o pedido.")
    col1, col2 = st.columns(2)

    with col1:
        st.session_state.dados_cliente["Nome"] = st.text_input(
            "Nome",
            value=st.session_state.dados_cliente["Nome"])
        telefone = st.text_input(
            "Telefone (com DDD)",
            value=st.session_state.dados_cliente["Telefone"])
        if telefone.isdigit() or telefone == "":
            st.session_state.dados_cliente["Telefone"] = telefone
        else:
            st.warning("Digite somente numeros no campo telefone")

        st.session_state.dados_cliente["Rua"] = st.text_input(
            "Rua",
            value=st.session_state.dados_cliente["Rua"])

        st.session_state.dados_cliente["Numero"] = st.text_input(
            "Número",
            value=st.session_state.dados_cliente["Numero"])

        bairro_atual = st.session_state.dados_cliente["Bairro"]
        index_bairro = lista_bairros.index(bairro_atual) if bairro_atual in lista_bairros else 0

        bairro_selecionado = st.selectbox(
            "Bairro",
            options=lista_bairros,
            index=index_bairro
        )
        # CORREÇÃO: antes era salvo em "bairros" (minúsculo), então o campo obrigatório "Bairro" nunca era preenchido
        st.session_state.dados_cliente["Bairro"] = (
            "" if bairro_selecionado == PLACEHOLDER_BAIRRO else bairro_selecionado
        )

        # Busca o valor da taxa de entrega conforme o bairro selecionado
        taxa_entrega = float(taxas_bairros.get(bairro_selecionado, 0.0))

        # Exibe um aviso informativo sobre o valor da taxa abaixo do campo do bairro
        if bairro_selecionado != PLACEHOLDER_BAIRRO:
            st.info(f"🛵 Taxa de entrega para **{bairro_selecionado}**: {brl(taxa_entrega)}")

        st.session_state.dados_cliente["Cidade"] = st.text_input(
            "Cidade", value=st.session_state.dados_cliente["Cidade"]
        )

        st.session_state.dados_cliente["Observação"] = st.text_area(
            "Observação",
            value=st.session_state.dados_cliente["Observação"],
            placeholder="Ex.: Sem cebola, entregar na portaria..."
        )

        st.session_state.dados_cliente["Forma de pagamento"] = st.selectbox(
            "Forma de pagamento",
            [PLACEHOLDER_PAGAMENTO, "Pix", "Dinheiro", "Cartão de crédito", "Cartão de débito"],
            index=0,
            key="forma_pagamento")

        if st.session_state.dados_cliente["Forma de pagamento"] == "Dinheiro":
            troco = st.text_input("Troco para quanto? :",
                                  key="valor_troco")
            st.session_state.dados_cliente["Troco"] = troco
        else:
            st.session_state.dados_cliente["Troco"] = ""

    with col2:
        st.subheader("🛒 Resumo do pedido")
        # CORREÇÃO: a taxa de entrega era somada a CADA item; agora é somada uma única vez ao total
        for produto in st.session_state.carrinho:
            st.write(f'{produto["quantidade"]}x {produto["Produto"]}')
            st.write(brl(produto["Preço"] * produto["quantidade"]))
            st.divider()
        st.write(f"Subtotal: {brl(total_itens())}")
        st.write(f"Entrega: {brl(taxa_entrega)}")
        st.subheader(f"Total: {brl(total_itens() + taxa_entrega)}")
        if st.session_state.dados_cliente["Forma de pagamento"] == "Dinheiro":
            st.write(f"pagamento em dinheiro: R$ {st.session_state.dados_cliente['Troco']}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Voltar para o cardápio"):
            st.session_state.pagina = "cardapio"
            st.rerun()
    with col2:
        if st.button("✅ Continuar pedido", type="primary"):
            dados = st.session_state.dados_cliente
            erros = campos_faltando(dados)
            if erros:
                st.warning("Você precisa preencher os campos obrigatórios: " + ", ".join(erros))
            elif not (10 <= len(dados["Telefone"]) <= 11):
                st.warning("Informe o telefone com DDD (10 ou 11 dígitos).")
            else:
                # Tudo preenchido: monta o pedido e vai para a página com o botão do WhatsApp
                mensagem = montar_mensagem(dados, st.session_state.carrinho, taxa_entrega)
                st.session_state.pedido = {
                    "mensagem": mensagem,
                    "url": link_whatsapp(mensagem),
                }
                st.session_state.pagina = "confirmacao"
                st.rerun()

# ====================== PÁGINA 3: CONFIRMAÇÃO / WHATSAPP ======================
elif st.session_state.pagina == "confirmacao":
    pedido = st.session_state.get("pedido")
    if not pedido:  # abriu direto nesta página sem pedido pronto
        st.session_state.pagina = "cardapio"
        st.rerun()

    st.title("✅ Pedido pronto para enviar")
    st.write("Confira o resumo abaixo e toque no botão para enviar o pedido ao restaurante pelo WhatsApp.")
    st.code(pedido["mensagem"], language=None)

    st.link_button("📲 Enviar pedido pelo WhatsApp", pedido["url"], type="primary")
    st.caption("O WhatsApp vai abrir com a mensagem pronta. Basta tocar em enviar.")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Corrigir dados"):
            st.session_state.pagina = "dados"
            st.rerun()
    with col2:
        if st.button("🆕 Fazer novo pedido"):
            st.session_state.carrinho = []
            st.session_state.pop("pedido", None)
            st.session_state.pagina = "cardapio"
            st.rerun()
