from abc import ABC, abstractmethod
from datetime import datetime
import textwrap
import requests

class Customer:
  def __init__(self, address):
    self.address = address
    self.accounts = []

  def make_transaction(self, accounts, transaction):
    transaction.register(accounts)
  
  def adicionar_conta(self, account):
    self.accounts.append(account)

class IndividualPerson(Customer):
  def __init__(self, name, birthdate, cpf, address):
    super().__init__(address)
    self.name = name
    self.birthdate = birthdate
    self.cpf = cpf

class Account:
  def __init__(self, number, customer):
    self._balance = 0
    self._number = number
    self._agency = "0001"
    self._customer = customer
    self._transfer_history = TransferHistory()

  @classmethod
  def new_account(cls, number, customer):
    return cls(number, customer)

  @property
  def balance(self):
    return self._balance
  
  @property
  def number(self):
    return self._number

  @property
  def agency(self):
    return self._agency
  
  @property
  def customer(self):
    return self._customer
  
  @property
  def transfer_history(self):
    return self._transfer_history
  
  def withdraw(self, value):
    balance = self.balance
    exceeded_balance = value > balance

    if exceeded_balance:
      print("\nOperação falhou: Saldo insuficiente")
    elif value > 0:
      self._balance -= value
      print("\nSaque realizado com sucesso!")
      return True
    else:
      print("\nOperação falhou: O valor informado não é válido")
    return False

  def deposit(self, value):
    if value > 0:
      self._balance += value
      print("\Depósito realizado com sucesso!")
      return True
    else:
      print("\nOperação falhou: O valor informado não é válido")
      return False

class CurrentAccount(Account):
  def __init__(self, number, customer, limit=500, withdrawal_limit=3):
    super().__init__(number, customer)
    self.limit = limit
    self.withdrawal_limit = withdrawal_limit

  def withdraw(self, value):
    withdrawals_number = len([transaction for transaction in self.transfer_history.transactions if transaction["type"] == Saque.__name__])

    exceeded_withdraw_limit = value > self.limit
    exceeded_withdraw_number = withdrawals_number >= self.withdrawal_limit

    if exceeded_withdraw_limit:
      print("\nOperação falhou: O valor excede o limite para um único saque")
    elif exceeded_withdraw_number:
      print("\nOperação falhou: Limite de saques atingido")
    else:
      return super().withdraw(value)

    return False
  
  def __str__(self):
    return f"""
      Agência:\t{self.agency}
      C/C:\t\t{self.number}
      Titular:\t{self.customer.name}
    """

class TransferHistory:
  def __init__(self) -> None:
    self._transactions = []
  
  @property
  def transactions(self):
    return self._transactions
  
  def add_transaction(self, transaction):
    self._transactions.append(
      {
        "type": transaction.__class__.__name__,
        "value": transaction.value,
        "date": datetime.now().strftime("%d-$m$Y %H:%M:%s")
      }
    )

class Transaction(ABC):
  @property
  @abstractmethod
  def value(self):
    pass

  @classmethod
  @abstractmethod
  def register(self, account):
    pass
  
class Saque(Transaction):
  def __init__(self, value):
    self._value = value
  
  @property
  def value(self):
    return self._value
  
  def register(self, account):
    transaction_success = account.withdraw(self.value)
    if transaction_success:
      account.transfer_history.add_transaction(self)

class Deposito(Transaction):
  def __init__(self, value):
    self._value = value

  @property
  def value(self):
    return self._value
  
  def register(self, account):
    transaction_success = account.deposit(self.value)
    if transaction_success:
      account.transfer_history.add_transaction(self)

def menu():
  menu = """
  ==================== MENU ====================
  [1]\tDepositar
  [2]\tSacar
  [3]\tExtrato
  [4]\tNova conta  
  [5]\tListar contas
  [6]\tNovo usuário
  [0]\tSair
"""
  return input(textwrap.dedent(menu))

def filter_customer(cpf, customers):
  filtered_customer = [customer for customer in customers if customer.cpf == cpf]
  return filtered_customer[0] if filtered_customer else None

def get_customer_account(customer):
  if not customer.accounts:
    print("Este cliente ainda não possui uma conta.")
    return
  return customer.accounts[0]

def find_customer(customers):
  cpf = input("Informe o CPF do cliente: ")
  if not cpf_validate(cpf):
    print("O CPF informado não é válido")
    return
  
  customer = filter_customer(cpf, customers)
  if not customer:
    print("\nCliente não encontrado")

  return customer

def deposit(customers):
  customer = find_customer(customers)
  if not customer:
    return
  
  value = float(input("Informe o valor a ser depositado: "))
  transaction = Deposito(value)
  account = get_customer_account(customer)
  if not account:
    return
  
  customer.make_transaction(account, transaction)

def withdraw(customers):
  customer = find_customer(customers)
  if not customer:
    return
  
  value = float(input("Informe o valor a ser sacado: "))
  transaction = Saque(value)
  account = get_customer_account(customer)
  if not account:
    return
  
  customer.make_transaction(account, transaction)

def show_statement(customers):
  customer = find_customer(customers)
  if not customer:
    return

  account = get_customer_account(customer)
  if not account:
    return
  
  print("================== EXTRATO ===================")
  transactions = account.transfer_history.transactions
  statement = ""
  if not transactions:
    statement = "Não foram realizadas movimentações."
  else:
    for transaction in transactions:
      statement += f"{transaction['type']}:\n\tR$ {transaction['value']:.2f}\n"
  print(statement)
  print(f"Saldo:\tRS {account.balance:.2f}")
  print("==============================================")

def get_cep_data(cep):
  CEP_API_BASE_URL = "https://viacep.com.br/ws"
  response = requests.get(f"{CEP_API_BASE_URL}/{cep}/json")
  if not response.ok:
    raise Exception(f"Erro ao obter dados. Código de status: {response.status_code}")
  return response.json()

def cpf_validate(cpf):
    cpf = ''.join(filter(str.isdigit, cpf))

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
    if resto != int(cpf[9]):
        return False

    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
    if resto != int(cpf[10]):
        return False

    return True

def create_customer(customers):
  cpf = input("Informe o CPF do customer: ")
  if not cpf_validate(cpf):
    print("O CPF informado não é válido")
    return
  
  customer = filter_customer(cpf, customers)
  if customer:
    print("Já existe um cliente com esse CPF.")
    return
  
  print("vamos realizar o seu cadastro")  
  name = input("Informe o nome completo: ")
  birthdate = input("Informe sua data de nascimento (dd-mm_aaaa): ")
  cep = input("informe seu CEP: ")
  cep_data = get_cep_data(cep)
  number = input("Informe o número da sua residência: ")
  address_number = number if number else "S/N"
  address = f"{cep_data['logradouro']}, {address_number} - {cep_data['bairro']} - {cep_data['localidade']}/{cep_data['uf']}"

  customer = IndividualPerson(name=name, birthdate=birthdate, cpf=cpf, address=address)

  customers.append(customer)
  print("Cliente criado com sucesso")

def create_account(account_number, customers, accounts):
  cpf = input("Informe o CPF do cliente: ")
  # aplicar a validação de cpf
  customer = filter_customer(cpf, customers)
  if not customer:
    print("\nCliente não encontrado")
    return
  
  account = CurrentAccount.new_account(customer=customer, number=account_number)
  accounts.append(account)
  customer.accounts.append(account)

  print("Conta criada com sucesso!")

def list_accounts(accounts):
  for account in accounts:
    print("=" * 100)
    print(textwrap.dedent(str(account)))

def main():
  customers = []
  contas = []

  while True:
    option = menu()
    if option == "1":
      deposit(customers)
    elif option == "2":
      withdraw(customers)
    elif option == "3":
      show_statement(customers)
    elif option == "4":
      numero_conta = len(contas) + 1
      create_account(numero_conta, customers, contas) 
    elif option == "5":
      list_accounts(contas)
    elif option == "6":
      create_customer(customers)
    elif option == "0":
      break

main()