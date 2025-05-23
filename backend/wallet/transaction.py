import uuid
import time

from backend.wallet.wallet import Wallet
from backend.config import MINING_REWARD, MINING_REWARD_INPUT


class Transaction:
    """
    Documents transactions from sender to one or more recipients
    """
    def __init__(self,
                 sender_wallet=None,
                 recipient=None,
                 amount=None,
                 id=None,
                 output=None,
                 input=None,
                 chip_info=None):
        self.id = id or str(uuid.uuid4())[0:8]
        self.output = output or self.create_output(sender_wallet, recipient, amount)
        self.input = input or self.create_input(sender_wallet, self.output)
        self.chip_info = chip_info or {'chip_id': None, 'chip_make': None, 'current_status': None}

    def create_output(self, sender_wallet, recipient, amount):
        """
        Structures output data for transaction
        """
        if amount > sender_wallet.balance:
            raise Exception('Amount exceeds balance')
        output = {}
        output[recipient] = amount
        output[sender_wallet.address] = sender_wallet.balance - amount

        return output
    
    def create_input(self, sender_wallet, output):
        """
        Structure input data for transaction
        Sign transaction and include sender's public key and address
        """
        return {
            'timestamp': time.time_ns(),
            'amount': sender_wallet.balance,
            'address': sender_wallet.address,
            'public_key': sender_wallet.public_key,
            'signature': sender_wallet.sign(output)
        }
    
    def update(self, sender_wallet, recipient, amount):
        """
        Update transaction with existing or new recipient
        """
        if amount > self.output[sender_wallet.address]:
            raise Exception('Amount exceeds balance')
        
        if recipient in self.output:
            self.output[recipient] += amount
        else:
            self.output[recipient] = amount

        self.output[sender_wallet.address] -= amount
        self.input = self.create_input(sender_wallet, self.output)

    def update_chip_info(self, chip_id, chip_make, current_status):
        """
        Update chip information in the transaction
        """
        self.chip_info = {
            'chip_id': chip_id,
            'chip_make': chip_make,
            'current_status': current_status
        }

    def to_json(self):
        """
        Serialize the transaction
        """
        return self.__dict__
    
    @staticmethod
    def from_json(transaction_json):
        """
        Deserialize transaction's JSON representation back into Transaction instance
        """
        return Transaction(**transaction_json)

    @staticmethod
    def is_valid_transaction(transaction):
        """
        Validates transactions and raises exception if not
        """
        if transaction.input == MINING_REWARD_INPUT:
            if list(transaction.output.values()) != [MINING_REWARD]:
                raise Exception('Invalid mining reward')
            return

        output_total = sum(transaction.output.values())
        if transaction.input['amount'] != output_total:
            raise Exception('Invalid transaction output values')
        
        if not Wallet.verify(transaction.input['public_key'], transaction.output, transaction.input['signature']):
            raise Exception('Invalid signature')
        
    @staticmethod
    def reward_transaction(miner_wallet):
        """
        Generate reward transaction for miner
        """
        output = {}
        output[miner_wallet.address] = MINING_REWARD

        return Transaction(input=MINING_REWARD_INPUT, output=output)
        

def main():
    transaction = Transaction(Wallet(), 'recipient', 15)
    transaction.update_chip_info('12345', 'ChipCorp', 'active')
    print(f'transaction.__dict__: {transaction.__dict__}')
    transaction_json = transaction.to_json()
    restored_transaction = Transaction.from_json(transaction_json)

    print(f'restored_transaction.__dict__: {restored_transaction.__dict__}')

if __name__ == '__main__':
    main()