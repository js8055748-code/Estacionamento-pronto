from datetime import datetime
from database import conectar


class Movimentacao:
    @staticmethod
    def registrar_entrada(placa):
        if not placa:
            raise ValueError("Placa não informada.")

        agora = datetime.now().isoformat(timespec="seconds")

        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO movimentacoes (placa, entrada)
            VALUES (?, ?)
        """, (placa, agora))
        conn.commit()
        conn.close()

    @staticmethod
    def registrar_saida(placa):
        if not placa:
            raise ValueError("Placa não informada.")

        conn = conectar()
        cur = conn.cursor()

        # 1) Verifica se o cliente é mensalista e qual a mensalidade
        cur.execute("""
            SELECT mensalista, valor_mensalidade
            FROM clientes
            WHERE placa = ?
        """, (placa,))
        cli = cur.fetchone()

        mensalista = 0
        valor_mensalidade = None
        if cli:
            mensalista, valor_mensalidade = cli

        # 2) Busca a última movimentação em aberto dessa placa
        cur.execute("""
            SELECT id, entrada
            FROM movimentacoes
            WHERE placa = ? AND saida IS NULL
            ORDER BY id DESC LIMIT 1
        """, (placa,))
        mov = cur.fetchone()

        if not mov:
            conn.close()
            return None  # nenhuma entrada em aberto

        mov_id, entrada_iso = mov
        saida_iso = datetime.now().isoformat(timespec="seconds")

        # 3) Define o valor conforme tipo de cliente
        if mensalista:
            # Cliente mensalista: não cobra por saída
            valor = 0.0
        else:
            # Cliente rotativo: coloque aqui sua regra real de cálculo
            # Exemplo simples: valor fixo
            valor = 10.0

        # 4) Atualiza a movimentação com saída e valor
        cur.execute("""
            UPDATE movimentacoes
            SET saida = ?, valor = ?
            WHERE id = ?
        """, (saida_iso, valor, mov_id))

        conn.commit()
        conn.close()

        # retorna info para o ticket
        return valor, bool(mensalista), valor_mensalidade
