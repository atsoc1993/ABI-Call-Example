from algokit_utils import ApplicationClient
from algosdk.atomic_transaction_composer import AtomicTransactionComposer, AccountTransactionSigner, TransactionWithSigner
from algosdk.transaction import PaymentTxn
from algosdk.v2client.algod import AlgodClient
from dotenv import load_dotenv
from algosdk.account import address_from_private_key
from pathlib import Path
from algosdk.abi import StringType
from base64 import b64decode
from algosdk.encoding import decode_address
import os

load_dotenv()

algod_token = os.getenv('NODE_TOKEN')
algod_port = os.getenv('NODE_PORT')
algod_client = AlgodClient(algod_token, algod_port)


private_key = os.getenv('TEST_USER_1_KEY')
sender = address_from_private_key(private_key)
decoded_address = decode_address(sender)

atc = AtomicTransactionComposer()
signer = AccountTransactionSigner(private_key)

params = algod_client.suggested_params()

app_id = int(os.getenv('APP_ID'))
app_address = os.getenv('APP_ADDRESS')

client = ApplicationClient(
    algod_client=algod_client,
    app_spec= Path(__file__).parent / './StakeTest.arc32.json',
    app_id=app_id,
    signer=signer,
    sender=sender,
    suggested_params=params,
)

box_ref = b'Staker' + decoded_address

payment_txn = PaymentTxn(sender, params, app_address, 24100)
payment_txn_with_signer = TransactionWithSigner(payment_txn, signer)

client.compose_call(atc, call_abi_method='createStakeAccount', transaction_parameters={"boxes": [[app_id, box_ref]]}, payment=payment_txn_with_signer)
result = atc.execute(algod_client, 2)


tx_id = result.tx_ids[0]
tx_info = result.abi_results[0].tx_info
tx_error = result.abi_results[0].decode_error
print(tx_id)
print(tx_info)
print(tx_error)
logs = result.abi_results[0].tx_info['logs']

string_schema = StringType()

for log in logs:
    print(string_schema.decode(b64decode(log)))

