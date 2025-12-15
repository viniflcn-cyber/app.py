import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date
import time
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Clínica-Escola Psicologia", layout="wide")

# --- CREDENCIAIS DE ACESSO ---
USUARIOS = {
    "admin": "admin123",
    "recepcao": "ufcat123"
}

# --- LISTAS PADRÃO ---
LISTA_RACA = ["Não Declarada", "Preta", "Parda", "Branca", "Amarela", "Indígena", "Quilombola"]
LISTA_EST_CIVIL = ["Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)", "União Estável"]
LISTA_RELIGIAO = ["Católico", "Evangélico", "Espírita", "Ateu", "Outra"]
LISTA_ESCOLARIDADE = ["Ensino Fundamental Incompleto", "Ensino Fundamental Completo", "Ensino Médio Incompleto", "Ensino Médio Completo", "Ensino Superior Incompleto", "Ensino Superior Completo", "Especialização", "Mestrado", "Doutorado", "Pós-Doutorado"]
LISTA_RENDA = ["Até R$ 1.520,00", "De R$ 1.521,00 a R$ 4.560,00", "De R$ 4.561,00 a R$ 7.600,00", "De R$ 7.601,00 a R$ 22.800,00", "Acima de R$ 22.800,00", "Prefiro não informar"]
LISTA_DISPO = ["Segunda-Feira de manhã.", "Segunda-Feira à tarde.", "Segunda-Feira à noite.", 
               "Terça-Feira de manhã.", "Terça-Feira à tarde.", "Terça-Feira à noite",
               "Quarta-Feira de manhã.", "Quarta-Feira à tarde", " Quarta-Feira à noite.",
               "Quinta-Feira de manhã.", "Quinta-Feira à tarde.", "Quinta-Feira à noite.",
               "Sexta-Feira de manhã.", "Sexta-Feira à tarde.", "Sexta-Feira à noite."]

# --- GERENCIAMENTO DE ESTADO ---
def inicializar_session_state():
    if 'logado' not in st.session_state: st.session_state['logado'] = False
    if 'usuario_atual' not in st.session_state: st.session_state['usuario_atual'] = ""
    campos_inscricao = ['nome_inscr', 'cpf_inscr', 'end_inscr', 'tel_inscr', 'resp_inscr']
    for campo in campos_inscricao:
        if campo not in st.session_state: st.session_state[campo] = ""

def limpar_chaves_inscricao():
    campos = ['nome_inscr', 'cpf_inscr', 'end_inscr', 'tel_inscr', 'resp_inscr']
    for campo in campos:
        if campo in st.session_state: st.session_state[campo] = ""

# --- BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect('dados_clinica.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS pacientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_cadastro TEXT,
                    nome TEXT,
                    cpf TEXT,
                    data_nascimento TEXT,
                    raca_cor TEXT,
                    endereco TEXT,
                    bairro TEXT,
                    cidade_estado TEXT,
                    telefone TEXT,
                    tel_emergencia TEXT,
                    falar_com TEXT,
                    naturalidade TEXT,
                    estado_civil TEXT,
                    escolaridade TEXT,
                    ocupacao TEXT,
                    renda TEXT,
                    aluno_ufcat TEXT,
                    curso_ufcat TEXT,
                    encaminhador TEXT,
                    religiao TEXT,
                    responsavel_nome TEXT,
                    responsavel_cpf TEXT,
                    disponibilidade TEXT,
                    status TEXT,
                    status_info TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS acolhimentos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paciente_id INTEGER,
                    data_acolhimento TEXT,
                    modo_atendimento TEXT,
                    estagiario_resp TEXT,
                    motivo_procura TEXT,
                    desenv_queixa TEXT,
                    tratamento_anterior TEXT,
                    uso_medicacao TEXT,
                    avaliacao_necessidade TEXT,
                    encaminhamento TEXT,
                    FOREIGN KEY(paciente_id) REFERENCES pacientes(id)
                )''')
    try: c.execute("ALTER TABLE acolhimentos ADD COLUMN modo_atendimento TEXT")
    except: pass
    try: c.execute("ALTER TABLE pacientes ADD COLUMN status TEXT")
    except: pass
    try: c.execute("ALTER TABLE pacientes ADD COLUMN status_info TEXT")
    except: pass
    conn.commit()
    conn.close()

# --- FUNÇÕES CRUD E RELATÓRIOS ---
def add_paciente(dados):
    try:
        conn = sqlite3.connect('dados_clinica.db')
        c = conn.cursor()
        c.execute('''INSERT INTO pacientes (data_cadastro, nome, cpf, data_nascimento, raca_cor, 
                     endereco, bairro, cidade_estado, telefone, tel_emergencia, falar_com, 
                     naturalidade, estado_civil, escolaridade, ocupacao, renda, aluno_ufcat, 
                     curso_ufcat, encaminhador, religiao, responsavel_nome, responsavel_cpf, disponibilidade, status, status_info)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', dados)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        return False

def update_paciente(id_paciente, dados):
    try:
        conn = sqlite3.connect('dados_clinica.db')
        c = conn.cursor()
        c.execute('''UPDATE pacientes SET 
                     nome=?, cpf=?, data_nascimento=?, raca_cor=?, endereco=?, bairro=?, cidade_estado=?, 
                     telefone=?, tel_emergencia=?, falar_com=?, naturalidade=?, estado_civil=?, 
                     escolaridade=?, ocupacao=?, renda=?, aluno_ufcat=?, curso_ufcat=?, encaminhador=?, 
                     religiao=?, responsavel_nome=?, responsavel_cpf=?, disponibilidade=?, status=?, status_info=?
                     WHERE id=?''', dados + (id_paciente,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro: {e}")
        return False

def add_acolhimento(dados):
    try:
        conn = sqlite3.connect('dados_clinica.db')
        c = conn.cursor()
        c.execute('''INSERT INTO acolhimentos (paciente_id, data_acolhimento, modo_atendimento, estagiario_resp, 
                     motivo_procura, desenv_queixa, tratamento_anterior, uso_medicacao, 
                     avaliacao_necessidade, encaminhamento)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', dados)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro: {e}")
        return False

def get_pacientes():
    conn = sqlite3.connect('dados_clinica.db')
    try: df = pd.read_sql_query("SELECT id, nome, cpf, telefone, data_cadastro, status FROM pacientes", conn)
    except: df = pd.read_sql_query("SELECT id, nome, cpf, telefone, data_cadastro FROM pacientes", conn)
    conn.close()
    return df

def get_dados_paciente(id_paciente):
    conn = sqlite3.connect('dados_clinica.db')
    df = pd.read_sql_query("SELECT * FROM pacientes WHERE id = ?", conn, params=(str(id_paciente),))
    conn.close()
    return df

def get_detalhes_clinicos(id_paciente):
    conn = sqlite3.connect('dados_clinica.db')
    # ATUALIZADO: Agora busca também tratamento_anterior e uso_medicacao
    df = pd.read_sql_query("SELECT data_acolhimento, modo_atendimento, estagiario_resp, motivo_procura, desenv_queixa, tratamento_anterior, uso_medicacao, avaliacao_necessidade, encaminhamento FROM acolhimentos WHERE paciente_id = ?", conn, params=(str(id_paciente),))
    conn.close()
    return df

def get_relatorio_geral_pacientes():
    conn = sqlite3.connect('dados_clinica.db')
    df = pd.read_sql_query("SELECT * FROM pacientes", conn)
    conn.close()
    return df

def get_relatorio_geral_acolhimentos():
    conn = sqlite3.connect('dados_clinica.db')
    query = '''
    SELECT acolhimentos.*, pacientes.nome as nome_paciente, pacientes.cpf as cpf_paciente
    FROM acolhimentos
    LEFT JOIN pacientes ON acolhimentos.paciente_id = pacientes.id
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# --- INICIALIZAÇÃO ---
init_db()
inicializar_session_state()

# --- LOGIN ---
def login_tela():
    st.markdown("<h1 style='text-align: center;'>🔒 Acesso Restrito - CEAPSI</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login_form"):
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar no Sistema"):
                if usuario in USUARIOS and USUARIOS[usuario] == senha:
                    st.session_state['logado'] = True
                    st.session_state['usuario_atual'] = usuario
                    st.success("Login realizado!")
                    time.sleep(1)
                    st.rerun()
                else: st.error("Dados incorretos.")

# --- SISTEMA PRINCIPAL ---
def sistema_principal():
    st.sidebar.write(f"👤 Usuário: **{st.session_state['usuario_atual'].upper()}**")
    if st.sidebar.button("🚪 Sair"):
        st.session_state['logado'] = False
        st.session_state['usuario_atual'] = ""
        limpar_chaves_inscricao()
        st.rerun()
    st.sidebar.markdown("---")

    col_titulo, col_logo = st.columns([0.8, 0.2])
    with col_titulo: st.title("Ψ Sistema de Manejo CEAPSI")
    with col_logo:
        try: st.image("logo_ufcat.png", use_container_width=True) 
        except: st.warning("Sem Logo")
    st.markdown("---")

    menu = st.sidebar.selectbox("Menu Principal", ["Ficha de Inscrição", "Ficha de Acolhimento", "Consultar Prontuários", "Atualizar Cadastro", "Gerar Relatórios", "Backup do Sistema"])

    # === MÓDULO 1: FICHA DE INSCRIÇÃO ===
    if menu == "Ficha de Inscrição":
        st.header("📋 Ficha de Inscrição (Recepção)")
        if st.session_state.get('limpar_ficha_agora'):
            limpar_chaves_inscricao()
            st.success("Paciente cadastrado com sucesso! ✅")
            st.session_state['limpar_ficha_agora'] = False
        if st.session_state.get('nome_inscr', ''):
            st.warning("⚠️ **Atenção:** Existem dados preenchidos abaixo que ainda não foram salvos!")
        if st.button("🧹 Limpar Campos / Cancelar"):
            st.session_state['limpar_ficha_agora'] = True
            st.rerun()

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Dados Pessoais")
            nome = st.text_input("Nome:", key="nome_inscr")
            cpf = st.text_input("CPF:", key="cpf_inscr")
            data_nasc = st.date_input("Data de Nascimento:", min_value=datetime(1920, 1, 1), format="DD/MM/YYYY")
            raca = st.selectbox("Cor/Raça:", LISTA_RACA)
            naturalidade = st.text_input("Naturalidade:")
            est_civil = st.selectbox("Estado Civil:", LISTA_EST_CIVIL)
            religiao = st.selectbox("Religião:", LISTA_RELIGIAO)
        with col2:
            st.subheader("Contato e Endereço:")
            endereco = st.text_input("Endereço (Rua, Nº): ", key="end_inscr")
            bairro = st.text_input("Bairro: ")
            cidade = st.text_input("Cidade/UF: ", value="Catalão/GO")
            tel = st.text_input("Contato Principal: ", key="tel_inscr")
            tel_emerg = st.text_input("Contato de Emergência: ")
            falar_com = st.text_input("Falar com (Nome do contato de emergência): ", key="resp_inscr")
        st.markdown("---")
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("Socioeconômico & Institucional")
            escolaridade = st.selectbox("Escolaridade: ", LISTA_ESCOLARIDADE)
            ocupacao = st.text_input("Ocupação Atual: ")
            renda = st.multiselect("Renda Familiar Aproximada:", LISTA_RENDA)
            aluno_ufcat = st.radio("Aluno da UFCAT?:", ["Não", "Sim"])
            curso_ufcat = st.text_input("Qual curso? (Se aluno): ")
            encaminhador = st.text_input("Quem indicou/encaminhou?:")
        with col4:
            st.subheader("Responsável (se menor de 18): ")
            resp_nome = st.text_input("Nome do Responsável:")
            resp_cpf = st.text_input("CPF do Responsável:")
            st.divider()
            st.subheader("Disponibilidade")
            dispo = st.multiselect("Horários Disponíveis", LISTA_DISPO)
        st.divider()
        st.caption("Administrativo")
        status_inicial = st.selectbox("Status Inicial do Prontuário:", ["Ativo", "Arquivado"])
        status_info = st.text_area("Informações sobre o Status (Opcional):")

        if st.button("💾 SALVAR INSCRIÇÃO", type="primary"):
            if nome:
                renda_str = ", ".join(renda)
                dispo_str = ", ".join(dispo)
                curso_save = curso_ufcat if aluno_ufcat == "Sim" else "Não"
                dados = (datetime.now().strftime("%Y-%m-%d"), nome, cpf, str(data_nasc), raca, 
                         endereco, bairro, cidade, tel, tel_emerg, falar_com, 
                         naturalidade, est_civil, escolaridade, ocupacao, renda_str, aluno_ufcat, 
                         curso_save, encaminhador, religiao, resp_nome, resp_cpf, dispo_str, status_inicial, status_info)
                if add_paciente(dados):
                    st.session_state['limpar_ficha_agora'] = True
                    st.rerun()
            else: st.error("O campo Nome é obrigatório.")

    # === MÓDULO 2: FICHA DE ACOLHIMENTO ===
    elif menu == "Ficha de Acolhimento":
        st.header("🩺 Ficha de Acolhimento (Triagem)")
        df_pacientes = get_pacientes()
        if not df_pacientes.empty:
            busca_rapida = st.text_input("🔍 Pesquisar paciente (Nome/CPF) para Acolhimento:", "")
            df_filtrado = df_pacientes.copy()
            if busca_rapida:
                df_filtrado = df_pacientes[df_pacientes['nome'].str.contains(busca_rapida, case=False, na=False) | df_pacientes['cpf'].str.contains(busca_rapida, case=False, na=False)]
            if not df_filtrado.empty:
                paciente_option = st.selectbox("Selecione o Paciente", df_filtrado['id'].astype(str) + " - " + df_filtrado['nome'])
                id_paciente = int(paciente_option.split(" - ")[0])
                st.markdown("---")
                st.info("💡 Preencha os dados abaixo.")
                with st.form("form_acolhimento", clear_on_submit=True):
                    modo_atend = st.text_input("Usuário Atendido em (Disciplina ou Plantão):", placeholder="Ex: Plantão Psicológico, Estágio I...")
                    estagiario = st.text_input("Estagiário - Orientador Responsável: ")
                    motivo = st.text_area("Motivo da Procura (Queixa Principal): ")
                    desenv = st.text_area("Desenvolvimento da Queixa (Histórico): ")
                    col1, col2 = st.columns(2)
                    with col1:
                        tratamento = st.text_area("Tratamentos Anteriores/Atuais (Médico/Psi): ")
                        medicacao = st.text_area("Uso de Medicação (Qual/Tempo): ")
                    with col2:
                        urgencia = st.radio("Avaliação de Necessidade: ", ["Não Urgente (Fila de Espera)", "Urgente (Crise)"])
                        encaminhamento = st.selectbox("Encaminhamento: ", ["Não houve", "Interno (Mesmo Estagiário)", "Interno (Fila de Espera)", "Externo"])
                    if st.form_submit_button("💾 Salvar Acolhimento"):
                        dados_acolhimento = (id_paciente, datetime.now().strftime("%Y-%m-%d"), modo_atend, estagiario, 
                                             motivo, desenv, tratamento, medicacao, urgencia, encaminhamento)
                        if add_acolhimento(dados_acolhimento): st.success("Acolhimento registrado no prontuário!")
            else: st.warning("Paciente não encontrado.")
        else: st.warning("Nenhum paciente cadastrado.")

    # === MÓDULO 3: CONSULTAR (ATUALIZADO COM TUDO!) ===
    elif menu == "Consultar Prontuários":
        st.header("📂 Prontuário Eletrônico")
        df = get_pacientes()
        if not df.empty:
            termo = st.text_input("🔍 Digite Nome ou CPF:", placeholder="Pesquisa...")
            df_filtrado = df[df['nome'].str.contains(termo, case=False, na=False) | df['cpf'].str.contains(termo, case=False, na=False)] if termo else df
            
            if not df_filtrado.empty:
                paciente_selecionado = st.selectbox("Selecione:", df_filtrado['id'].astype(str) + " - " + df_filtrado['nome'])
                if st.button("👁️ Abrir Prontuário"):
                    id_sel = int(paciente_selecionado.split(" - ")[0])
                    p = get_dados_paciente(id_sel).iloc[0]
                    
                    # Cabeçalho do Prontuário
                    status_cor = "⚠️" if p['status'] == "Arquivado" else "✅"
                    st.markdown(f"### {status_cor} {p['nome']} (ID: {p['id']})")
                    st.caption(f"Status: {p['status'] or 'Ativo'}")
                    if p['status'] == "Arquivado": st.error(f"Local do Arquivo: {p['status_info']}")
                    
                    # --- FICHA DE INSCRIÇÃO COMPLETA ---
                    with st.expander("📋 Dados Cadastrais Completos (Inscrição)", expanded=True):
                        st.markdown("#### 1. Dados Pessoais")
                        c1, c2, c3 = st.columns(3)
                        c1.write(f"**CPF:** {p['cpf']}")
                        c1.write(f"**Nascimento:** {p['data_nascimento']}")
                        c1.write(f"**Naturalidade:** {p['naturalidade']}")
                        c2.write(f"**Raça/Cor:** {p['raca_cor']}")
                        c2.write(f"**Estado Civil:** {p['estado_civil']}")
                        c2.write(f"**Religião:** {p['religiao']}")
                        c3.write(f"**Data Cadastro:** {p['data_cadastro']}")
                        
                        st.markdown("#### 2. Contato e Endereço")
                        c4, c5 = st.columns(2)
                        c4.write(f"**Endereço:** {p['endereco']}, {p['bairro']}")
                        c4.write(f"**Cidade:** {p['cidade_estado']}")
                        c5.write(f"**Telefone Principal:** {p['telefone']}")
                        c5.write(f"**Emergência:** {p['tel_emergencia']} (Falar com: {p['falar_com']})")
                        
                        st.markdown("#### 3. Socioeconômico e Institucional")
                        c6, c7 = st.columns(2)
                        c6.write(f"**Escolaridade:** {p['escolaridade']}")
                        c6.write(f"**Ocupação:** {p['ocupacao']}")
                        c6.write(f"**Renda Familiar:** {p['renda']}")
                        c7.write(f"**Aluno UFCAT?** {p['aluno_ufcat']} ({p['curso_ufcat']})")
                        c7.write(f"**Encaminhador:** {p['encaminhador']}")
                        
                        st.markdown("#### 4. Outros")
                        st.write(f"**Responsável (se menor):** {p['responsavel_nome']} (CPF: {p['responsavel_cpf']})")
                        st.write(f"**Disponibilidade:** {p['disponibilidade']}")

                    # --- HISTÓRICO CLÍNICO COMPLETO ---
                    st.markdown("---")
                    st.markdown("### 🩺 Histórico Clínico (Acolhimentos e Evoluções)")
                    clinico = get_detalhes_clinicos(id_sel)
                    
                    if not clinico.empty:
                        for _, row in clinico.iterrows():
                            with st.expander(f"📅 {row['data_acolhimento']} | {row['modo_atendimento']} | Resp: {row['estagiario_resp']}"):
                                st.markdown(f"**Contexto:** {row['modo_atendimento']}")
                                st.markdown(f"**Queixa Principal:** {row['motivo_procura']}")
                                st.markdown(f"**Histórico/Desenvolvimento:** {row['desenv_queixa']}")
                                
                                # Novos campos agora visíveis
                                c_med1, c_med2 = st.columns(2)
                                c_med1.markdown(f"**💊 Medicação:** {row['uso_medicacao']}")
                                c_med2.markdown(f"**🏥 Tratamento Anterior:** {row['tratamento_anterior']}")
                                
                                st.divider()
                                st.markdown(f"**Avaliação:** {row['avaliacao_necessidade']}")
                                st.markdown(f"**Encaminhamento:** {row['encaminhamento']}")
                    else:
                        st.info("Nenhum registro de acolhimento encontrado.")
            else: st.warning("Nenhum resultado.")
        else: st.warning("Banco de dados vazio.")

    # === MÓDULO 4: ATUALIZAR ===
    elif menu == "Atualizar Cadastro":
        st.header("✏️ Atualizar Dados")
        df = get_pacientes()
        if not df.empty:
            termo = st.text_input("Busque para editar:", "")
            df = df[df['nome'].str.contains(termo, case=False, na=False) | df['cpf'].str.contains(termo, case=False, na=False)] if termo else df
            paciente_option = st.selectbox("Selecione para editar:", df['id'].astype(str) + " - " + df['nome'])
            id_editar = int(paciente_option.split(" - ")[0])
            p = get_dados_paciente(id_editar).iloc[0]
            with st.form("form_edicao"):
                st.info(f"Editando: {p['nome']}")
                st.markdown("### 🗂️ Status")
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    status_db = p['status'] if p['status'] else "Ativo"
                    novo_status = st.selectbox("Status:", ["Ativo", "Arquivado"], index=0 if status_db == "Ativo" else 1)
                with col_s2:
                    novo_status_info = st.text_area("Info Arquivo:", value=p['status_info'] if p['status_info'] else "")
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    novo_nome = st.text_input("Nome:", value=p['nome'])
                    novo_cpf = st.text_input("CPF:", value=p['cpf'])
                    try: data_obj = datetime.strptime(p['data_nascimento'], "%Y-%m-%d").date()
                    except: data_obj = datetime(2000, 1, 1)
                    nova_data = st.date_input("Nascimento:", value=data_obj, format="DD/MM/YYYY")
                    try: idx_raca = LISTA_RACA.index(p['raca_cor'])
                    except: idx_raca = 0
                    nova_raca = st.selectbox("Raça:", LISTA_RACA, index=idx_raca)
                    nova_naturalidade = st.text_input("Naturalidade:", value=p['naturalidade'])
                    try: idx_civil = LISTA_EST_CIVIL.index(p['estado_civil'])
                    except: idx_civil = 0
                    novo_est_civil = st.selectbox("Est. Civil:", LISTA_EST_CIVIL, index=idx_civil)
                    try: idx_religiao = LISTA_RELIGIAO.index(p['religiao'])
                    except: idx_religiao = 0
                    nova_religiao = st.selectbox("Religião:", LISTA_RELIGIAO, index=idx_religiao)
                with col2:
                    novo_endereco = st.text_input("Endereço:", value=p['endereco'])
                    novo_bairro = st.text_input("Bairro:", value=p['bairro'])
                    novo_cidade = st.text_input("Cidade:", value=p['cidade_estado'])
                    novo_tel = st.text_input("Tel:", value=p['telefone'])
                    novo_emerg = st.text_input("Emergência:", value=p['tel_emergencia'])
                    novo_falar_com = st.text_input("Falar com:", value=p['falar_com'])
                st.markdown("---")
                col3, col4 = st.columns(2)
                with col3:
                    try: idx_esc = LISTA_ESCOLARIDADE.index(p['escolaridade'])
                    except: idx_esc = 0
                    nova_escolaridade = st.selectbox("Escolaridade:", LISTA_ESCOLARIDADE, index=idx_esc)
                    nova_ocupacao = st.text_input("Ocupação:", value=p['ocupacao'])
                    lista_renda_valida = [x for x in (p['renda'].split(", ") if p['renda'] else []) if x in LISTA_RENDA]
                    nova_renda = st.multiselect("Renda:", LISTA_RENDA, default=lista_renda_valida)
                    novo_aluno = st.radio("Aluno UFCAT?", ["Não", "Sim"], index=1 if p['aluno_ufcat'] == "Sim" else 0)
                    novo_curso = st.text_input("Curso:", value=p['curso_ufcat'])
                    novo_encaminhador = st.text_input("Encaminhador:", value=p['encaminhador'])
                with col4:
                    novo_resp_nome = st.text_input("Resp. Nome:", value=p['responsavel_nome'])
                    novo_resp_cpf = st.text_input("Resp. CPF:", value=p['responsavel_cpf'])
                    lista_dispo_valida = [x for x in (p['disponibilidade'].split(", ") if p['disponibilidade'] else []) if x in LISTA_DISPO]
                    nova_dispo = st.multiselect("Disponibilidade:", LISTA_DISPO, default=lista_dispo_valida)
                
                if st.form_submit_button("🔄 Atualizar Cadastro"):
                    dados_novos = (novo_nome, novo_cpf, str(nova_data), nova_raca, novo_endereco, 
                                   novo_bairro, novo_cidade, novo_tel, novo_emerg, novo_falar_com, 
                                   nova_naturalidade, novo_est_civil, nova_escolaridade, nova_ocupacao, 
                                   ", ".join(nova_renda), novo_aluno, novo_curso, novo_encaminhador, nova_religiao, 
                                   novo_resp_nome, novo_resp_cpf, ", ".join(nova_dispo), novo_status, novo_status_info)
                    if update_paciente(id_editar, dados_novos):
                        st.success("✅ Cadastro atualizado com sucesso!")
                        time.sleep(1.5)
                        st.rerun()
        else: st.warning("Sem pacientes.")

    # === MÓDULO 5: RELATÓRIOS ===
    elif menu == "Gerar Relatórios":
        st.header("📊 Exportação de Dados para Excel")
        st.info("Aqui você pode baixar os dados completos para gerar relatórios anuais.")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("1. Base Geral de Pacientes")
            df_pacientes = get_relatorio_geral_pacientes()
            if not df_pacientes.empty:
                csv_pacientes = df_pacientes.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Baixar Planilha de Pacientes (.csv)", csv_pacientes, f"Relatorio_Pacientes_{date.today()}.csv", "text/csv", key='dl_pac')
            else: st.warning("Sem dados.")
        with col2:
            st.subheader("2. Histórico de Atendimentos")
            df_acolhimentos = get_relatorio_geral_acolhimentos()
            if not df_acolhimentos.empty:
                csv_acolhimentos = df_acolhimentos.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Baixar Histórico (.csv)", csv_acolhimentos, f"Relatorio_Atendimentos_{date.today()}.csv", "text/csv", key='dl_acol')
            else: st.warning("Sem dados.")

    # === MÓDULO 6: BACKUP ===
    elif menu == "Backup do Sistema":
        st.header("💾 Backup de Segurança")
        st.markdown("### Como fazer o backup?")
        st.info("1. Clique no botão abaixo.\n2. Salve o arquivo em um **Pen Drive** ou no **Google Drive**.")
        if os.path.exists("dados_clinica.db"):
            with open("dados_clinica.db", "rb") as fp:
                st.download_button(label="📥 FAZER BACKUP AGORA", data=fp, file_name=f"backup_clinica_ceapsi_{datetime.now().strftime('%Y-%m-%d')}.db", mime="application/x-sqlite3", type="primary")
        else: st.error("Erro crítico: Banco de dados não encontrado.")

if st.session_state['logado']:
    sistema_principal()
else:
    login_tela()