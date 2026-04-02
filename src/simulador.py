from gerador import next_random


def tempo_uniforme(minimo, maximo):
    """Gera um tempo aleatório entre o intervalo min e max."""
    return minimo + (maximo - minimo) * next_random()


class Simulador:
    def __init__(
        self, capacidade_k, servidores=1, chegada_range=(2, 5), atendimento_range=(3, 5)
    ):
        self.K = capacidade_k
        self.S = servidores
        self.c_min, self.c_max = chegada_range
        self.a_min, self.a_max = atendimento_range
        self.tempo_global = 0.0
        self.fila_atual = 0
        self.tempo_ultimo_evento = 0.0
        self.times = [0.0] * (self.K + 1)

        self.proxima_chegada = 2.0

        self.proximas_saidas = [float("inf")] * self.S

        self.clientes_perdidos = 0

    def contabilizar_tempo(self):
        """Acumula o tempo que o sistema passou no estado atual da fila."""
        duracao = self.tempo_global - self.tempo_ultimo_evento
        if 0 <= self.fila_atual <= self.K:
            self.times[self.fila_atual] += duracao
        self.tempo_ultimo_evento = self.tempo_global

    def executar_chegada(self):
        self.contabilizar_tempo()

        if self.fila_atual < self.K:
            self.fila_atual += 1
            for i in range(self.S):
                if self.proximas_saidas[i] == float("inf"):
                    self.proximas_saidas[i] = self.tempo_global + tempo_uniforme(
                        self.a_min, self.a_max
                    )
                    break
        else:
            self.clientes_perdidos += 1

        self.proxima_chegada = self.tempo_global + tempo_uniforme(
            self.c_min, self.c_max
        )

    def executar_saida(self, servidor_idx):
        self.contabilizar_tempo()

        if self.fila_atual > 0:
            self.fila_atual -= 1
        if self.fila_atual >= self.S:
            self.proximas_saidas[servidor_idx] = self.tempo_global + tempo_uniforme(
                self.a_min, self.a_max
            )
        else:
            self.proximas_saidas[servidor_idx] = float("inf")

    def next_event(self):
        """Descobre qual evento ocorre primeiro e avança o tempo global."""
        menor_saida = min(self.proximas_saidas)
        servidor_idx = self.proximas_saidas.index(menor_saida)

        if self.proxima_chegada <= menor_saida:
            self.tempo_global = self.proxima_chegada
            return "CHEGADA", None
        else:
            self.tempo_global = menor_saida
            return "SAIDA", servidor_idx
