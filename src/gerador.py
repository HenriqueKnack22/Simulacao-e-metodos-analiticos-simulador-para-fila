class GeradorCongruente:
    def __init__(self, seed=12345, a=48271, c=0, m=2**31 - 1):
        """
        Inicializa o gerador com os parâmetros:
        a: multiplicador
        c: incremento
        m: módulo (2^31 - 1 é o padrão do Lehmer RNG)
        seed: semente inicial
        """
        self.a = a
        self.c = c
        self.m = m
        self.anterior = seed

    def next_random(self):
        """
        Calcula o próximo número da sequência e retorna 
        ele normalizado entre 0 e 1.
        """
        self.anterior = (self.a * self.anterior + self.c) % self.m
        
        return self.anterior / self.m
_instancia_padrao = GeradorCongruente()

def next_random():
    """Função de conveniência para ser chamada no simulador."""
    return _instancia_padrao.next_random()

if __name__ == "__main__":
    print("Testando os primeiros 5 números aleatórios:")
    for i in range(5):
        print(f"{i+1}: {next_random()}")