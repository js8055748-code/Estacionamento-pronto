import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from PIL import Image, ImageTk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from cliente import Clientes
from movimentacao import Movimentacao
from relatorio import Relatorio
from database import criar_tabelas, conectar
from pdf_utils import gerar_cupom_pdf


def iniciar_sistema():
    criar_tabelas()

    janela = tk.Tk()
    janela.title("Sistema de Estacionamento")
    janela.geometry("800x600")

    try:
        janela.iconbitmap("estacionamento.ico")
    except Exception:
        pass

    # ===== TOPO =====
    topo = tk.Frame(janela, bg="#0d6efd", height=40)
    topo.pack(fill="x")

    tk.Label(
        topo,
        text="ESTACIONAMENTO J J",
        bg="#0d6efd",
        fg="white",
        font=("Arial", 20, "bold"),
    ).pack(expand=True)

    # ===== NOTEBOOK =====
    abas = ttk.Notebook(janela)
    abas.pack(expand=True, fill="both")

    # ================= ABA CLIENTES =================
    aba_clientes = tk.Frame(abas, bg="#c5ddcc")
    abas.add(aba_clientes, text="Clientes")

    # --- MARCA D'ÁGUA CLIENTES ---
    try:
        img_clientes = Image.open("bg_clientes.png").resize((800, 560))
        bg_img_clientes = ImageTk.PhotoImage(img_clientes)
        lbl_bg_clientes = tk.Label(aba_clientes, image=bg_img_clientes)
        lbl_bg_clientes.image = bg_img_clientes
        lbl_bg_clientes.place(x=0, y=0, relwidth=1, relheight=1)
    except Exception:
        pass
    # -----------------------------

    # Campos por cima da imagem (place para garantir que fiquem visíveis)
    tk.Label(aba_clientes, text="Nome", bg="#b5c4ba").place(x=50, y=40)
    entry_nome = tk.Entry(aba_clientes, width=40)
    entry_nome.place(x=150, y=40)

    tk.Label(aba_clientes, text="CPF", bg="#c5ddcc").place(x=50, y=80)
    entry_cpf = tk.Entry(aba_clientes, width=40)
    entry_cpf.place(x=150, y=80)

    tk.Label(aba_clientes, text="Placa", bg="#c5ddcc").place(x=50, y=120)
    entry_placa = tk.Entry(aba_clientes, width=20)
    entry_placa.place(x=150, y=120)

    tk.Label(aba_clientes, text="Tipo (carro/moto)", bg="#c5ddcc").place(x=50, y=160)
    entry_tipo = tk.Entry(aba_clientes, width=20)
    entry_tipo.place(x=200, y=160)

    # Novo: mensalista / valor mensalidade
    tk.Label(aba_clientes, text="É mensalista?", bg="#c5ddcc").place(x=50, y=200)
    combo_mensalista = ttk.Combobox(aba_clientes, values=["Não", "Sim"], state="readonly", width=17)
    combo_mensalista.place(x=200, y=200)
    combo_mensalista.set("Não")

    tk.Label(aba_clientes, text="Valor mensalidade (R$)", bg="#c5ddcc").place(x=50, y=240)
    entry_valor_mensal = tk.Entry(aba_clientes, width=10)
    entry_valor_mensal.place(x=200, y=240)

    def cadastrar():
        try:
            nome = entry_nome.get()
            cpf = entry_cpf.get()
            placa = entry_placa.get()
            tipo = entry_tipo.get()
            mensalista_str = combo_mensalista.get()
            valor_mensal_str = entry_valor_mensal.get().strip()

            mensalista = 1 if mensalista_str == "Sim" else 0

            if mensalista and not valor_mensal_str:
                messagebox.showwarning("Aviso", "Informe o valor da mensalidade para cliente mensalista.")
                return

            valor_mensalidade = float(valor_mensal_str) if valor_mensal_str else None

            Clientes.cadastrar(
                nome,
                cpf,
                placa,
                tipo,
                mensalista,
                valor_mensalidade
            )

            messagebox.showinfo("Sucesso", "Cliente cadastrado!")
            entry_nome.delete(0, tk.END)
            entry_cpf.delete(0, tk.END)
            entry_placa.delete(0, tk.END)
            entry_tipo.delete(0, tk.END)
            combo_mensalista.set("Não")
            entry_valor_mensal.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Erro", "Valor de mensalidade inválido.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar: {e}")

    tk.Button(aba_clientes, text="Cadastrar", command=cadastrar).place(x=200, y=280)

    def cadastrar():
        try:
            Clientes.cadastrar(
                entry_nome.get(),
                entry_cpf.get(),
                entry_placa.get(),
                entry_tipo.get(),
            )
            messagebox.showinfo("Sucesso", "Cliente cadastrado!")
            entry_nome.delete(0, tk.END)
            entry_cpf.delete(0, tk.END)
            entry_placa.delete(0, tk.END)
            entry_tipo.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar: {e}")

    # ================= ABA MOVIMENTAÇÃO =================
    aba_mov = tk.Frame(abas, bg="#C0C0C0")
    abas.add(aba_mov, text="Movimentação")

    # --- MARCA D'ÁGUA MOVIMENTAÇÃO ---
    try:
        img_mov = Image.open("bg_clientes.png").resize((800, 560))
        bg_img_mov = ImageTk.PhotoImage(img_mov)
        lbl_bg_mov = tk.Label(aba_mov, image=bg_img_mov)
        lbl_bg_mov.image = bg_img_mov
        lbl_bg_mov.place(x=0, y=0, relwidth=1, relheight=1)
    except Exception:
        pass
    # ---------------------------------

    tk.Label(aba_mov, text="Placa", bg="#C0C0C0").place(x=50, y=40)
    entry_mov = tk.Entry(aba_mov, width=20)
    entry_mov.place(x=150, y=40)

    tk.Button(
        aba_mov,
        text="Ver dados do cliente",
        command=lambda: ver_dados_cliente(entry_mov.get().strip()),
        bg="#CCCCCC"
    ).place(x=350, y=40)

    def ver_dados_cliente(placa):
        placa = placa.strip()
        if not placa:
            messagebox.showwarning("Aviso", "Informe a placa para visualizar os dados do cliente.")
            return

        try:
            conn = conectar()
            cur = conn.cursor()
            # Ajuste conforme sua tabela de clientes
            cur.execute("""
                SELECT nome, cpf, tipo, mensalista, valor_mensalidade
                FROM clientes
                WHERE placa = ?
            """, (placa,))
            row = cur.fetchone()
            conn.close()

            if row is None:
                messagebox.showwarning("Aviso", "Cliente não encontrado para esta placa.")
                return

            nome, cpf, tipo_veiculo, mensalista, valor_mensalidade = row
            status = "Mensalista" if mensalista == 1 else "Diarista"
            valor_txt = f"R$ {valor_mensalidade:.2f}" if valor_mensalidade is not None else "-"

            # Janela com os dados
            janela_cli = tk.Toplevel(janela)
            janela_cli.title(f"Dados do cliente - Placa {placa}")
            janela_cli.geometry("400x250")

            tk.Label(janela_cli, text=f"Nome: {nome}").pack(anchor="w", padx=10, pady=5)
            tk.Label(janela_cli, text=f"CPF: {cpf}").pack(anchor="w", padx=10, pady=5)
            tk.Label(janela_cli, text=f"Placa: {placa}").pack(anchor="w", padx=10, pady=5)
            tk.Label(janela_cli, text=f"Tipo veículo: {tipo_veiculo}").pack(anchor="w", padx=10, pady=5)
            tk.Label(janela_cli, text=f"Tipo de cliente: {status}").pack(anchor="w", padx=10, pady=5)
            tk.Label(janela_cli, text=f"Valor mensalidade: {valor_txt}").pack(anchor="w", padx=10, pady=5)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar dados do cliente:\n{e}")

    def entrada():
        try:
            placa = entry_mov.get().strip()
            if not placa:
                messagebox.showwarning("Aviso", "Informe a placa.")
                return

            # Registra a entrada (classe Movimentacao grava no banco)
            Movimentacao.registrar_entrada(placa)

            # Busca a última movimentação dessa placa (entrada recém-registrada)
            conn = conectar()
            cur = conn.cursor()
            cur.execute("""
                SELECT id, entrada FROM movimentacoes
                WHERE placa = ?
                ORDER BY id DESC LIMIT 1
            """, (placa,))
            mov = cur.fetchone()
            conn.close()

            if mov:
                mov_id, entrada_iso = mov
                entrada_br = datetime.fromisoformat(entrada_iso).strftime("%d/%m/%Y %H:%M:%S")

                # Texto do cupom de ENTRADA
                ticket_texto = (
                    f"*** TICKET DE ENTRADA ***\n"
                    f"ID: {mov_id}\n"
                    f"Placa: {placa}\n"
                    f"Data/Hora de Entrada: {entrada_br}\n"
                    "***************************"
                )

                # Mostra o ticket na tela
                messagebox.showinfo("Ticket de Entrada", ticket_texto)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao registrar entrada: {e}")

    def saida():
        try:
            placa = entry_mov.get().strip()
            if not placa:
                messagebox.showwarning("Aviso", "Informe a placa.")
                return

            resultado = Movimentacao.registrar_saida(placa)
            if resultado is None:
                messagebox.showwarning("Aviso", "Nenhuma entrada aberta para essa placa.")
                return

            valor, is_mensalista, valor_mensalidade = resultado

            # Busca a última movimentação dessa placa (já com saída e valor)
            conn = conectar()
            cur = conn.cursor()
            cur.execute("""
                SELECT id, entrada, saida, valor FROM movimentacoes
                WHERE placa = ?
                ORDER BY id DESC LIMIT 1
            """, (placa,))
            mov = cur.fetchone()
            conn.close()

            if mov:
                mov_id, ent, sai, val = mov
                entrada_br = datetime.fromisoformat(ent).strftime("%d/%m/%Y %H:%M:%S")
                saida_br = datetime.fromisoformat(sai).strftime("%d/%m/%Y %H:%M:%S")

                if is_mensalista:
                    # Ticket especial para mensalista
                    ticket_texto = (
                        f"*** TICKET DE SAÍDA (MENSALISTA) ***\n"
                        f"ID: {mov_id}\n"
                        f"Placa: {placa}\n"
                        f"Entrada: {entrada_br}\n"
                        f"Saída: {saida_br}\n"
                        f"Mensalidade: R$ {valor_mensalidade:.2f}\n"
                        f"Valor cobrado nesta saída: R$ 0,00\n"
                        "*************************************"
                    )
                else:
                    # Ticket normal rotativo
                    ticket_texto = (
                        f"*** TICKET DE SAÍDA ***\n"
                        f"ID: {mov_id}\n"
                        f"Placa: {placa}\n"
                        f"Entrada: {entrada_br}\n"
                        f"Saída: {saida_br}\n"
                        f"Valor a pagar: R$ {val:.2f}\n"
                        "*************************"
                    )

                # Mostra o ticket na tela
                messagebox.showinfo("Ticket de Saída", ticket_texto)

                # Geração de PDF
                caminho = gerar_cupom_pdf(
                    mov_id,
                    placa,
                    entrada_br,
                    saida_br,
                    valor if not is_mensalista else 0.0
                )

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao registrar saída: {e}")

    tk.Button(aba_mov, text="Registrar Entrada", bg="green", fg="white", command=entrada).place(x=150, y=120)
    tk.Button(aba_mov, text="Registrar Saída", bg="blue", fg="white", command=saida).place(x=300, y=120)

    # ======================================================
    # ABA MENSALISTA
    # =====================================================
    aba_mensalista = tk.Frame(abas, bg="#C0C0C0")
    abas.add(aba_mensalista, text="Mensalista")

    frame = tk.Frame(aba_mensalista, bg="#C0C0C0")
    frame.pack(pady=20)

    label_placa = tk.Label(frame, text="Placa:", bg="#C0C0C0")
    label_placa.grid(row=0, column=0, padx=5, pady=5)

    entry_placa = tk.Entry(frame)
    entry_placa.grid(row=0, column=1, padx=5, pady=5)

    label_nome = tk.Label(frame, text="Nome:", bg="#C0C0C0")
    label_nome.grid(row=1, column=0, padx=5, pady=5)

    entry_nome = tk.Entry(frame)
    entry_nome.grid(row=1, column=1, padx=5, pady=5)

    label_cpf = tk.Label(frame, text="CPF:", bg="#C0C0C0")
    label_cpf.grid(row=2, column=0, padx=5, pady=5)

    entry_cpf = tk.Entry(frame)
    entry_cpf.grid(row=2, column=1, padx=5, pady=5)

    label_tipo = tk.Label(frame, text="Tipo:", bg="#C0C0C0")
    label_tipo.grid(row=3, column=0, padx=5, pady=5)

    combo_tipo = ttk.Combobox(frame, values=["Mensalista", "Avulso"])
    combo_tipo.grid(row=3, column=1, padx=5, pady=5)

    def cadastrar_mensalista():
        placa = entry_placa.get()
        nome = entry_nome.get()
        cpf = entry_cpf.get()
        tipo = combo_tipo.get()

        if not (placa and nome and cpf and tipo):
            messagebox.showwarning("Aviso", "Todos os campos devem ser preenchidos.")
            return
        # Aqui você chamaria a função para cadastrar o mensalista no banco de dados
        # Exemplo: Mensalista.cadastrar(placa, nome, cpf, tipo)

        messagebox.showinfo("Sucesso", "Mensalista cadastrado com sucesso!")

    btn_cadastrar = tk.Button(frame, text="Cadastrar", command=cadastrar_mensalista)
    btn_cadastrar.grid(row=4, columnspan=2, pady=10)

    # ================= ABA RELATÓRIOS =================
    aba_rel = ttk.Frame(abas)
    abas.add(aba_rel, text="Relatórios")

    frame_botoes_rel = tk.Frame(aba_rel)
    frame_botoes_rel.pack(side="top", fill="x", pady=5)

    texto = tk.Text(aba_rel)
    texto.pack(expand=True, fill="both")

    def mostrar_clientes():
        texto.delete("1.0", tk.END)
        rows = Relatorio.clientes()

        if not rows:
            texto.insert(tk.END, "Nenhum cliente cadastrado.\n")
            return

        for (cid, nome, cpf, placa, tipo, valor) in rows:
            linha = (
                f"ID: {cid}\n"
                f"Nome: {nome}\n"
                f"CPF: {cpf}\n"
                f"Placa: {placa}\n"
                f"Tipo: {tipo}\n"
                f"Último Valor (se houver): R$ {valor:.2f}\n"
                "-----------------------------\n\n"
            )
            texto.insert(tk.END, linha)

    def mostrar_movimentacoes():
        texto.delete("1.0", tk.END)
        rows = Relatorio.movimentacoes()

        if not rows:
            texto.insert(tk.END, "Nenhuma movimentação encontrada.\n")
            return

        for (mid, placa, entrada, saida, valor) in rows:
            linha = (
                f"ID: {mid}\n"
                f"Placa: {placa}\n"
                f"Entrada: {entrada}\n"
                f"Saída: {saida if saida else '-'}\n"
                f"Valor: R$ {valor:.2f}" if valor is not None else "Valor: -"
            )
            linha += "\n-----------------------------\n\n"
            texto.insert(tk.END, linha)

    from datetime import date

    def mostrar_faturamento_dia():
        texto.delete("1.0", tk.END)
        hoje = date.today().isoformat()
        total = Relatorio.faturamento_do_dia(hoje)
        texto.insert(tk.END, f"Faturamento do dia {hoje}: R$ {total:.2f}\n")

    def mostrar_faturamento_mes():
        texto.delete("1.0", tk.END)
        hoje = date.today()
        ano_mes = hoje.strftime("%Y-%m")
        total = Relatorio.faturamento_do_mes(ano_mes)
        texto.insert(tk.END, f"Faturamento do mês {ano_mes}: R$ {total:.2f}\n")

    tk.Button(
        frame_botoes_rel,
        text="Clientes",
        command=mostrar_clientes
    ).pack(side="left", padx=5)

    tk.Button(
        frame_botoes_rel,
        text="Movimentações",
        command=mostrar_movimentacoes
    ).pack(side="left", padx=5)

    tk.Button(
        frame_botoes_rel,
        text="Faturamento do dia",
        command=mostrar_faturamento_dia
    ).pack(side="left", padx=5)

    tk.Button(
        frame_botoes_rel,
        text="Faturamento do mês",
        command=mostrar_faturamento_mes
    ).pack(side="left", padx=5)

    tk.Button(
        frame_botoes_rel,
        text="Atualizar",
        command=mostrar_clientes
    ).pack(side="left", padx=5)

        # ================= ABA DASHBOARD =================
    aba_dash = ttk.Frame(abas)
    abas.add(aba_dash, text="Dashboard")

    frame_topo_dash = tk.Frame(aba_dash)
    frame_topo_dash.pack(side="top", fill="x", pady=10, padx=10)

    tk.Label(frame_topo_dash, text="Meta mensal (R$):").grid(row=0, column=0, sticky="w")
    entry_meta = tk.Entry(frame_topo_dash, width=10)
    entry_meta.grid(row=0, column=1, padx=5)

    lbl_faturamento_mes = tk.Label(frame_topo_dash, font=("Arial", 12, "bold"))
    lbl_faturamento_mes.grid(row=1, column=0, columnspan=2, sticky="w", pady=5)

    lbl_meta_mes = tk.Label(frame_topo_dash, font=("Arial", 12, "bold"))
    lbl_meta_mes.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)

    lbl_status_meta = tk.Label(frame_topo_dash, font=("Arial", 12, "bold"), fg="blue")
    lbl_status_meta.grid(row=3, column=0, columnspan=2, sticky="w", pady=5)

    fig = Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)

    canvas = FigureCanvasTkAgg(fig, master=aba_dash)
    canvas.get_tk_widget().pack(pady=10)

    def atualizar_dashboard():
        hoje = date.today()
        ano_mes = hoje.strftime("%m-%Y")

        faturamento_mes = Relatorio.faturamento_do_mes(ano_mes)

        meta_texto = entry_meta.get().strip()
        try:
            meta_mes = float(meta_texto) if meta_texto else 0.0
        except ValueError:
            meta_mes = 0.0

        lbl_faturamento_mes.config(text=f"Faturamento do mês ({ano_mes}): R$ {faturamento_mes:.2f}")
        lbl_meta_mes.config(text=f"Meta do mês: R$ {meta_mes:.2f}")

        if meta_mes > 0:
            if faturamento_mes >= meta_mes:
                lbl_status_meta.config(text="Meta atingida ou superada.", fg="green")
            else:
                restante = meta_mes - faturamento_mes
                lbl_status_meta.config(
                    text=f"Falta R$ {restante:.2f} para atingir a meta.",
                    fg="red"
                )
        else:
            lbl_status_meta.config(text="Defina uma meta mensal para acompanhar.", fg="blue")

        dados = Relatorio.faturamento_por_dia()
        datas = [d[0] for d in dados]
        valores = [d[1] for d in dados]

        ax.clear()
        # aqui entram seus comandos de plot (bar, line, etc.)
        ax.bar(datas, valores, color="#0d6efd", edgecolor="black",
               alpha=0.7, label="Faturamento Diário", width=0.6)
        ax.set_title("Faturamento por Dia")
        ax.set_xlabel("Data")
        ax.set_ylabel("Valor (R$)")
        ax.tick_params(axis='x', rotation=45)
        for barra, valor in zip(ax.patches, valores):
            altura = barra.get_height()
            ax.text(
                barra.get_x() + barra.get_width() / 2,
                altura,
                f"{valor:.2f}",
                ha="center",
                va="bottom",
                fontsize=8,
                rotation=0
            )
        canvas.draw()

    tk.Button(
        frame_topo_dash,
        text="Atualizar Dashboard",
        command=atualizar_dashboard
    ).grid(row=0, column=2, padx=10)

    atualizar_dashboard()

    
    janela.mainloop()
if __name__ == "__main__":
    iniciar_sistema()

