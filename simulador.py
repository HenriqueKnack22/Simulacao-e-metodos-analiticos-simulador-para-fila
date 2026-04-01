#!/usr/bin/env python3
"""Simulador de Fila G/G/c/K - Simulação baseada em eventos discretos.

Módulo: Simulação e Métodos Analíticos

Uso:
    python simulador.py [arquivo_config.yaml]

Se nenhum arquivo de configuração for fornecido, executa as simulações
padrão: G/G/1/5 e G/G/2/5 com chegadas U(2,5) e serviços U(3,5).
"""

import heapq
import random
import sys

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False


class SimuladorFila:
    """Simulador de fila G/G/c/K com chegadas e serviços uniformes.

    Atributos:
        servidores  -- número de servidores (c)
        capacidade  -- capacidade total do sistema, incluindo em atendimento (K)
        chegada_min -- limite inferior da distribuição uniforme de chegadas
        chegada_max -- limite superior da distribuição uniforme de chegadas
        servico_min -- limite inferior da distribuição uniforme de serviços
        servico_max -- limite superior da distribuição uniforme de serviços
        semente     -- semente para o gerador de aleatórios (opcional)
    """

    # Tipos de evento (usados como desempatador no heap: SAIDA=0 tem prioridade
    # sobre CHEGADA=1 quando ocorrem no mesmo instante)
    SAIDA = 0
    CHEGADA = 1

    def __init__(self, servidores, capacidade,
                 chegada_min, chegada_max,
                 servico_min, servico_max,
                 semente=None):
        if servidores < 1:
            raise ValueError("O número de servidores deve ser >= 1.")
        if capacidade < servidores:
            raise ValueError(
                "A capacidade do sistema deve ser >= ao número de servidores.")
        if chegada_min > chegada_max:
            raise ValueError(
                "chegada_min não pode ser maior que chegada_max.")
        if servico_min > servico_max:
            raise ValueError(
                "servico_min não pode ser maior que servico_max.")

        self.servidores = servidores
        self.capacidade = capacidade
        self.chegada_min = chegada_min
        self.chegada_max = chegada_max
        self.servico_min = servico_min
        self.servico_max = servico_max
        self.semente = semente

    # ------------------------------------------------------------------
    # Método auxiliar
    # ------------------------------------------------------------------

    @staticmethod
    def _uniforme(a, b, r):
        """Transforma um aleatório r ∈ [0,1) em U(a, b)."""
        return a + (b - a) * r

    # ------------------------------------------------------------------
    # Execução da simulação
    # ------------------------------------------------------------------

    def executar(self, num_aleatorios=100_000, primeira_chegada=2.0):
        """Executa a simulação e devolve um dicionário com os resultados.

        A simulação termina quando o num_aleatorios-ésimo aleatório é
        consumido (conforme especificado no enunciado).

        Parâmetros:
            num_aleatorios   -- número de aleatórios a utilizar (padrão 100.000)
            primeira_chegada -- tempo da primeira chegada (padrão 2,0)

        Retorna um dicionário com as chaves:
            servidores, capacidade, tempo_total, perdidos,
            tempos_estado, aleatorios_usados
        """
        if self.semente is not None:
            random.seed(self.semente)

        # ---- Contador de aleatórios ----
        aleatorios_usados = 0

        def proximo_aleatorio():
            nonlocal aleatorios_usados
            if aleatorios_usados >= num_aleatorios:
                return None
            aleatorios_usados += 1
            return random.random()

        # ---- Estado ----
        tempo = 0.0
        na_fila = 0                              # clientes no sistema
        perdidos = 0                             # clientes rejeitados
        tempos_estado = [0.0] * (self.capacidade + 1)

        # ---- Fila de eventos (min-heap): (tempo, tipo, seq) ----
        # O campo 'seq' é um contador de inserção que desfaz empates
        # adicionais após o desempate por tipo.
        eventos = []
        _seq = [0]

        def agendar(t, tipo):
            _seq[0] += 1
            heapq.heappush(eventos, (t, tipo, _seq[0]))

        # Agenda a primeira chegada (tempo fixo, sem consumir aleatório)
        agendar(primeira_chegada, self.CHEGADA)

        em_execucao = True

        while eventos and em_execucao:
            tempo_evento, tipo_evento, _ = heapq.heappop(eventos)

            # Acumula o tempo que o sistema ficou no estado atual
            tempos_estado[na_fila] += tempo_evento - tempo
            tempo = tempo_evento

            # ---- Evento de CHEGADA ----
            if tipo_evento == self.CHEGADA:

                if na_fila < self.capacidade:
                    na_fila += 1

                    # Se há servidor livre, inicia atendimento imediatamente
                    if na_fila <= self.servidores:
                        r = proximo_aleatorio()
                        if r is None:
                            em_execucao = False
                            break
                        ts = self._uniforme(self.servico_min,
                                            self.servico_max, r)
                        agendar(tempo + ts, self.SAIDA)
                else:
                    # Sistema cheio: cliente perdido
                    perdidos += 1

                # Agenda a próxima chegada
                r = proximo_aleatorio()
                if r is None:
                    em_execucao = False
                else:
                    intervalo = self._uniforme(self.chegada_min,
                                               self.chegada_max, r)
                    agendar(tempo + intervalo, self.CHEGADA)

            # ---- Evento de SAÍDA ----
            elif tipo_evento == self.SAIDA:
                na_fila -= 1

                # Se ainda há clientes aguardando, inicia o próximo atendimento
                # (num_in_system >= servidores após decremento significa que
                # havia pelo menos 1 cliente na fila de espera antes da saída)
                if na_fila >= self.servidores:
                    r = proximo_aleatorio()
                    if r is None:
                        em_execucao = False
                    else:
                        ts = self._uniforme(self.servico_min,
                                            self.servico_max, r)
                        agendar(tempo + ts, self.SAIDA)

        return {
            "servidores": self.servidores,
            "capacidade": self.capacidade,
            "tempo_total": tempo,
            "perdidos": perdidos,
            "tempos_estado": tempos_estado,
            "aleatorios_usados": aleatorios_usados,
        }


# ----------------------------------------------------------------------
# Funções de entrada/saída
# ----------------------------------------------------------------------

def imprimir_resultados(resultados):
    """Exibe os resultados da simulação de forma formatada."""
    s = resultados["servidores"]
    k = resultados["capacidade"]
    tempo_total = resultados["tempo_total"]
    perdidos = resultados["perdidos"]
    tempos = resultados["tempos_estado"]
    usados = resultados["aleatorios_usados"]

    print(f"\n{'=' * 65}")
    print(f"  Simulação G/G/{s}/{k}")
    print(f"{'=' * 65}")
    print(f"  Tempo global da simulação : {tempo_total:.4f}")
    print(f"  Clientes perdidos         : {perdidos}")
    print(f"  Aleatórios utilizados     : {usados}")
    print(f"\n  {'Estado':<10} {'Tempo Acumulado':>20} {'Probabilidade':>16}")
    print(f"  {'-' * 48}")
    for estado, t in enumerate(tempos):
        prob = t / tempo_total if tempo_total > 0.0 else 0.0
        print(f"  {estado:<10} {t:>20.4f} {prob:>16.6f}")
    print(f"{'=' * 65}")


def carregar_config_yaml(caminho):
    """Lê um arquivo YAML de configuração e devolve lista de parâmetros.

    Formato esperado do YAML:
        simulacoes:
          - servidores: 1
            capacidade: 5
            chegada_min: 2
            chegada_max: 5
            servico_min: 3
            servico_max: 5
            semente: null          # opcional
          - ...
        num_aleatorios: 100000    # opcional, padrão 100000
        primeira_chegada: 2.0     # opcional, padrão 2.0
    """
    if not _YAML_AVAILABLE:
        print("Aviso: PyYAML não está instalado. "
              "Execute 'pip install pyyaml' para usar configuração YAML.")
        return None

    with open(caminho, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    return cfg


# ----------------------------------------------------------------------
# Ponto de entrada
# ----------------------------------------------------------------------

def main():
    num_aleatorios = 100_000
    primeira_chegada = 2.0

    # Se um arquivo YAML for passado como argumento, usa suas configurações
    if len(sys.argv) > 1:
        cfg = carregar_config_yaml(sys.argv[1])
        if cfg is not None:
            num_aleatorios = cfg.get("num_aleatorios", num_aleatorios)
            primeira_chegada = cfg.get("primeira_chegada", primeira_chegada)

            print("Simulador de Fila G/G/c/K")
            print(f"Número de aleatórios : {num_aleatorios}")
            print(f"Primeira chegada     : {primeira_chegada}")

            for params in cfg.get("simulacoes", []):
                sim = SimuladorFila(
                    servidores=params["servidores"],
                    capacidade=params["capacidade"],
                    chegada_min=params["chegada_min"],
                    chegada_max=params["chegada_max"],
                    servico_min=params["servico_min"],
                    servico_max=params["servico_max"],
                    semente=params.get("semente"),
                )
                res = sim.executar(
                    num_aleatorios=num_aleatorios,
                    primeira_chegada=primeira_chegada,
                )
                imprimir_resultados(res)
            return

    # Simulações padrão exigidas pelo enunciado
    print("Simulador de Fila G/G/c/K")
    print("Distribuição de chegadas : Uniforme(2, 5)")
    print("Distribuição de serviços : Uniforme(3, 5)")
    print(f"Número de aleatórios     : {num_aleatorios}")
    print("Fila vazia, primeiro cliente chega no tempo 2,0")

    # --- Simulação 1: G/G/1/5 ---
    sim1 = SimuladorFila(
        servidores=1,
        capacidade=5,
        chegada_min=2, chegada_max=5,
        servico_min=3, servico_max=5,
    )
    res1 = sim1.executar(num_aleatorios=num_aleatorios,
                         primeira_chegada=primeira_chegada)
    imprimir_resultados(res1)

    # --- Simulação 2: G/G/2/5 ---
    sim2 = SimuladorFila(
        servidores=2,
        capacidade=5,
        chegada_min=2, chegada_max=5,
        servico_min=3, servico_max=5,
    )
    res2 = sim2.executar(num_aleatorios=num_aleatorios,
                         primeira_chegada=primeira_chegada)
    imprimir_resultados(res2)


if __name__ == "__main__":
    main()
