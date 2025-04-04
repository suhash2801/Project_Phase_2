from backend.blockchain.block import Block
from backend.wallet.transaction import Transaction
from backend.wallet.wallet import Wallet
from backend.config import MINING_REWARD_INPUT


class Blockchain:
    
    def __init__(self):
        self.chain=[Block.genesis()]

    def add_block(self,data):
        self.chain.append(Block.mine_block(self.chain[-1],data))
        #self.chain[-1] references the last block in the chain
    

    def __repr__(self):
        return f'Blockchain: {self.chain}'
    
    def replace_chain(self,chain):
        """
        Replace the local chain with incoming chain if:
        1. Incoming chain is longer than local
        2. Incoming chain is formatted properly
        """
        if len(chain)<=len(self.chain):
            raise Exception('Cannot replace. Incoming chain must be longer')
        
        try:
            Blockchain.is_valid_chain(chain)

        except Exception as e:
            raise Exception (F'Cannot replace. Incoming chain is invalid: {e}')
        
        self.chain=chain
        
    def to_json(self):
        """Serialize blockchain to list of blocks
        """
        return list(map(lambda block: block.to_json(),self.chain))
    @staticmethod
    def from_json(chain_json):

        """
        Deserialize a list into a blockchain instance.
        Result contains chain list of Block instances
        """
        blockchain=Blockchain()
        blockchain.chain=list(map(lambda block_json: Block.from_json(block_json),chain_json))

        return blockchain

    

    @staticmethod
    def is_valid_chain(chain):
        """
        Validate the incoming chain
        Enforce following rules:
        1. Starts with genesis block
        2. Blocks format must be crct
        """
        if chain[0]!=Block.genesis():
            raise Exception('Genesis block must be valid')

        for i in range(1,len(chain)):
            block=chain[i]
            last_block=chain[i-1]
            Block.is_valid_block(last_block,block)

        Blockchain.is_valid_transaction_chain(chain)

    @staticmethod
    def is_valid_transaction_chain(chain):
        """
        Enforce rules of transaction:
        1.Each transaction must only appear once
        2.Only 1 mining reward per block
        3.Each transaction must be valid
        """
        transaction_ids=set()

        for i in range(len(chain)):
            block = chain[i]
            has_mining_reward=False

            for transaction_json in block.data:
                transaction=Transaction.from_json(transaction_json)

                if transaction.id in transaction_ids:
                    raise Exception(f'Transaction {transaction.id} is not unique')
                
                transaction_ids.add(transaction.id)

                if transaction.input==MINING_REWARD_INPUT:
                    if has_mining_reward:
                        raise Exception(f'There can only be one mining reward per block.Check block with hash: {block.hash}')
                    has_mining_reward=True

                else:
                    historic_blockchain=Blockchain()
                    historic_blockchain.chain=chain[0:i]

                    historic_balance=Wallet().calculate_balance(historic_blockchain,transaction.input['address'])


                    if historic_balance!=transaction.input['amount']:
                        raise Exception(f'Transaction {transaction.id} has invalid input amount')

                Transaction.is_valid_transaction(transaction)





    
def main():

    blockchain=Blockchain()

    blockchain.add_block('one')
    blockchain.add_block('two')

    print(blockchain)


    print(f'block.py __name__:{__name__}')
if __name__=='__main__':
    main()