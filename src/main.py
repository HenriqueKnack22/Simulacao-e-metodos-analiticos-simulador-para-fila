import os
from gerador import next_random
from simulador import Simulador

def gerar_csv_teste(quantidade=1000):
    """Gera o CSV de validação do gerador conforme solicitado."""
    os.makedirs('data', exist_ok=True)
    with open('data/testes_rng.csv', 'w') as f:
        f.write("Indice,Valor\n")
        for i in range(quantidade):
            f.write(f"{i},{next_random()}\n")

def rodar_validacao(nome, servidores, k, chegadas, atendimentos):
    """Executa a simulação para um cenário específico."""
    sim = Simulador(capacidade_k=k, servidores=servidores, 
                    chegada_range=chegadas, atendimento_range=atendimentos)
    
    eventos_totais = 100000
    count = eventos_totais
    
    while count > 0:
        tipo, idx_servidor = sim.next_event()
        if tipo == "CHEGADA":
            sim.executar_chegada()
        else:
            sim.executar_saida(idx_servidor)
        count -= 1

    print(f"\n" + "="*45)
    print(f" RESULTADO DA VALIDAÇÃO: {nome}")
    print("="*45)
    print(f"{'ESTADO':<10} | {'TEMPO ACUMULADO':<15} | {'PROBABILIDADE'}")
    print("-" * 45)
    
    for i in range(k + 1):
        tempo = sim.times[i]
        prob = (tempo / sim.tempo_global) * 100
        print(f"Fila {i:<5} | {tempo:>15.2f} | {prob:>11.2f}%")
    
    print("-" * 45)
    print(f"Tempo Global Total: {sim.tempo_global:.2f}")

if __name__ == "__main__":
    gerar_csv_teste(1000)
    print("Gerador testado e CSV criado em data/testes_rng.csv")
    rodar_validacao("G/G/1/5", servidores=1, k=5, chegadas=(2, 5), atendimentos=(3, 5))
    rodar_validacao("G/G/2/5", servidores=2, k=5, chegadas=(2, 5), atendimentos=(3, 5))