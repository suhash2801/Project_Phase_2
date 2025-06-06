import uuid
import time

from backend.wallet.wallet import Wallet


class Transaction:
    """
    Documents transactions from sender to one or more recipients
    """
    def __init__(self,sender_wallet,recipient,amount):
        self.id=str(uuid.uuid4)[:8]
        self.output=self.create_output(sender_wallet,recipient,amount)
        self.input=self.create_input(sender_wallet,self.output)


    def create_output(self,sender_wallet,recipient,amount):
        """
        structures output data for transaction
        """
        if amount>sender_wallet.balance:
            raise Exception('Amount exceeds balance')
        output={}
        output[recipient]=amount
        output[sender_wallet.address]=sender_wallet.balance-amount

        return output
    
    def create_input(self,sender_wallet,output):
        """
        Structure input data for transaction
        Sign transaction and include sender's public key and address
        """

        return{
            'timestamp': time.time_ns(),
            'amount':sender_wallet.balance,
            'address':sender_wallet.address,
            'public_key':sender_wallet.public_key,
            'signature':sender_wallet.sign(output)
        }
        
def main():
    transaction=Transaction(Wallet(),'recipient',15)
    print(f'transaction.__dict__: {transaction.__dict__}')

if __name__=='__main__':
    main()