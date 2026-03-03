from database import conectar


class Relatorio:
    @classmethod
    def clientes(cls):
        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            SELECT
                c.id,
                c.nome,
                c.cpf,
                c.placa,
                c.tipo,
                IFNULL(m.valor, 0)
            FROM clientes c
            LEFT JOIN movimentacoes m
                ON m.placa = c.placa
            ORDER BY c.nome
        """)
        rows = cur.fetchall()
        conn.close()
        return rows

    @classmethod
    def movimentacoes(cls):
        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            SELECT
                id,
                nome,
                placa,
                entrada,
                saida,
                valor
            FROM movimentacoes
            ORDER BY id DESC
        """)
        rows = cur.fetchall()
        conn.close()
        return rows

    
    @classmethod
    def faturamento_total(cls):
        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            SELECT COALESCE(SUM(valor), 0)
            FROM movimentacoes
            WHERE valor IS NOT NULL
        """)
        total = cur.fetchone()[0]
        conn.close()
        return total

    @classmethod
    def faturamento_por_dia(cls):
        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            SELECT
                substr(entrada, 1, 10) AS dia,
                COALESCE(SUM(valor), 0) AS total
            FROM movimentacoes
            WHERE valor IS NOT NULL
            GROUP BY dia
            ORDER BY dia
        """)
        rows = cur.fetchall()
        conn.close()
        return rows

    @classmethod
    def faturamento_do_dia(cls, data_iso):
        """
        data_iso no formato 'DD-MM-YYYY'
        """
        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            SELECT COALESCE(SUM(valor), 0)
            FROM movimentacoes
            WHERE valor IS NOT NULL
              AND substr(entrada, 1, 10) = ?
        """, (data_iso,))
        total = cur.fetchone()[0]
        conn.close()
        return total

    @classmethod
    def faturamento_do_mes(cls, ano_mes_iso):
        """
        ano_mes_iso no formato 'dd-mm-yyyy' (ex: '03-03-2026')
        """
        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            SELECT COALESCE(SUM(valor), 0)
            FROM movimentacoes
            WHERE valor IS NOT NULL
              AND substr(entrada, 1, 7) = ?
        """, (ano_mes_iso,))
        total = cur.fetchone()[0]
        conn.close()
        return total

    
   
