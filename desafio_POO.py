import textwrap
from abc import ABC, abstractmethod

class Transacao(ABC):
    @abstractmethod
    def registra(self, conta):
        pass

class Deposito(Transacao):
    def __init__(self, valor):
        self.valor = valor

    def registra(self, conta):
        if self.valor > 0:
            conta.saldo += self.valor
            conta.historico.adicionar_transacao(self)
            return True
        return False

class Saque(Transacao):
    def __init__(self, valor):
        self.valor = valor

    def registra(self, conta):
        if self.valor > 0 and conta.saldo >= self.valor:
            conta.saldo -= self.valor
            conta.historico.adicionar_transacao(self)
            return True
        return False

class Historico:
    def __init__(self):
        self.transacoes = []

    def adicionar_transacao(self, transacao):
        self.transacoes.append(transacao)

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        if transacao.registra(conta):
            print(f"Transação de R$ {transacao.valor:.2f} realizada com sucesso!")
        else:
            print("Transação falhou!")

    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, endereco, cpf, nome, data_nascimento):
        super().__init__(endereco)
        self.cpf = cpf
        self.nome = nome
        self.data_nascimento = data_nascimento

class Conta:
    def __init__(self, cliente, numero, agencia):
        self._saldo = 0.0
        self._numero = numero
        self._agencia = agencia
        self._cliente = cliente
        self._historico = Historico()
        cliente.adicionar_conta(self)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    @staticmethod
    def nova_conta(cliente, numero):
        return Conta(cliente, numero, "0001")

    def sacar(self, valor):
        if valor > 0 and self._saldo >= valor:
            self._saldo -= valor
            self._historico.adicionar_transacao(Saque(valor))
            return True
        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            self._historico.adicionar_transacao(Deposito(valor))
            return True
        return False

class ContaCorrente(Conta):
    def __init__(self, cliente, numero, agencia, limite, limite_saques):
        super().__init__(cliente, numero, agencia)
        self._limite = limite
        self._limite_saques = limite_saques
        self._numero_saques = 0

    @property
    def limite(self):
        return self._limite

    @property
    def limite_saques(self):
        return self._limite_saques

    @property
    def numero_saques(self):
        return self._numero_saques

    def sacar(self, valor):
        if self._numero_saques >= self._limite_saques:
            print("Número máximo de saques excedido.")
            return False
        if valor > self._limite:
            print("Valor do saque excede o limite.")
            return False
        if super().sacar(valor):
            self._numero_saques += 1
            return True
        return False

def menu():
    menu = """\n
    ================ MENU ================
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [q]\tSair
    => """
    return input(textwrap.dedent(menu))

def main():
    LIMITE_SAQUES = 3
    AGENCIA = "0001"
    LIMITE_CONTA = 500.0

    usuarios = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            cpf = input("Informe o CPF do usuário: ")
            usuario = next((u for u in usuarios if u.cpf == cpf), None)
            if usuario:
                conta = usuario.contas[0]
                valor = float(input("Informe o valor do depósito: "))
                deposito = Deposito(valor)
                usuario.realizar_transacao(conta, deposito)
            else:
                print("Usuário não encontrado.")

        elif opcao == "s":
            cpf = input("Informe o CPF do usuário: ")
            usuario = next((u for u in usuarios if u.cpf == cpf), None)
            if usuario:
                conta = usuario.contas[0]
                valor = float(input("Informe o valor do saque: "))
                saque = Saque(valor)
                usuario.realizar_transacao(conta, saque)
            else:
                print("Usuário não encontrado.")

        elif opcao == "e":
            cpf = input("Informe o CPF do usuário: ")
            usuario = next((u for u in usuarios if u.cpf == cpf), None)
            if usuario:
                conta = usuario.contas[0]
                print("\n================ EXTRATO ================")
                for transacao in conta.historico.transacoes:
                    print(f"Transação: R$ {transacao.valor:.2f}")
                print(f"Saldo: R$ {conta.saldo:.2f}")
                print("==========================================")
            else:
                print("Usuário não encontrado.")

        elif opcao == "nu":
            cpf = input("Informe o CPF (somente número): ")
            usuario = next((u for u in usuarios if u.cpf == cpf), None)
            if usuario:
                print("\n@@@ Já existe usuário com esse CPF! @@@")
            else:
                nome = input("Informe o nome completo: ")
                data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
                endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")
                usuario = PessoaFisica(endereco, cpf, nome, data_nascimento)
                usuarios.append(usuario)
                print("=== Usuário criado com sucesso! ===")

        elif opcao == "nc":
            cpf = input("Informe o CPF do usuário: ")
            usuario = next((u for u in usuarios if u.cpf == cpf), None)
            if usuario:
                numero_conta = len(contas) + 1
                conta = ContaCorrente(usuario, numero_conta, AGENCIA, LIMITE_CONTA, LIMITE_SAQUES)
                contas.append(conta)
                print("\n=== Conta criada com sucesso! ===")
            else:
                print("Usuário não encontrado.")

        elif opcao == "lc":
            for conta in contas:
                linha = f"""\
                    Agência:\t{conta.agencia}
                    C/C:\t\t{conta.numero}
                    Titular:\t{conta.cliente.nome}
                """
                print("=" * 100)
                print(textwrap.dedent(linha))

        elif opcao == "q":
            break

        else:
            print("Operação inválida, por favor selecione novamente a operação desejada.")

if __name__ == "__main__":
    main()
