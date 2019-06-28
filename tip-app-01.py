# First attempt at tip app.
#

# Tkinter, apparently a standard lib:
import json
import binascii
import struct
from tkinter import *
from bitshares import BitShares
from bitsharesbase import operations
from bitsharesbase.signedtransactions import Signed_Transaction
from bitshares.account import Account
from bitshares.amount import Amount
from bitshares.asset import Asset
from bitshares.memo import Memo
from asn1 import Encoder, Numbers
from ledgerblue.comm import getDongle

blockchain = BitShares("wss://bitshares.openledger.info/ws")
bip32_path = "48'/1'/1'/0'/0'"
op_xfr_from = "ledger-demo" #"hw-lns-test-02"

def append_transfer_tx(append_to, dest_account_name):
    #
    account = Account(op_xfr_from, blockchain_instance=blockchain)
    amount = Amount(2.0, "BTS", blockchain_instance=blockchain)
    to = Account(dest_account_name, blockchain_instance=blockchain)
    memoObj = Memo(from_account=account, to_account=to, blockchain_instance=blockchain)
    memo_text = "" #"Signed by BitShares App on Ledger Nano S!"

    op = operations.Transfer(
        **{
            "fee": {"amount": 0, "asset_id": "1.3.0"},
            "from": account["id"],
            "to": to["id"],
            "amount": {"amount": int(amount), "asset_id": amount.asset["id"]},
            "memo": memoObj.encrypt(memo_text),
        }
    )

    append_to.appendOps(op)
    return append_to

def sendTip(to_name):
    #
    print("\nButton Pressed")
    print("Attempting to send 2.0 BTS to %s" % (to_name))
    tx_head = blockchain.new_tx()  # Pull recent TaPoS
    tx = append_transfer_tx(tx_head, to_name)
    print("We have constructed the following transaction:")
    print(tx)
    tx_st = Signed_Transaction(
            ref_block_num=tx['ref_block_num'],
            ref_block_prefix=tx['ref_block_prefix'],
            expiration=tx['expiration'],
            operations=tx['operations'],
    )
    signData = encode(binascii.unhexlify(blockchain.rpc.chain_params['chain_id']), tx_st)
    print("Serialized:")
    print (binascii.hexlify(signData).decode())
    print("Sending transaction to Ledger Nano S for signature...")
    donglePath = parse_bip32_path(bip32_path)
    pathSize = int(len(donglePath) / 4)
    dongle = getDongle(True)
    offset = 0
    first = True
    signSize = len(signData)
    while offset != signSize:
        if signSize - offset > 200:
            chunk = signData[offset: offset + 200]
        else:
            chunk = signData[offset:]

        if first:
            totalSize = len(donglePath) + 1 + len(chunk)
            apdu = binascii.unhexlify("B5040000" + "{:02x}".format(totalSize) + "{:02x}".format(pathSize)) + donglePath + chunk
            first = False
        else:
            totalSize = len(chunk)
            apdu = binascii.unhexlify("B5048000" + "{:02x}".format(totalSize)) + chunk

        offset += len(chunk)
        result = dongle.exchange(apdu)
        print (binascii.hexlify(result).decode())
        print ("Broadcasting transaction...")
        tx_sig = blockchain.new_tx(json.loads(str(tx_st)))
        tx_sig["signatures"].extend([binascii.hexlify(result).decode()])
        print (blockchain.broadcast(tx=tx_sig))
        print ("Success!")


# from signTransaction.py
def encode(chain_id, tx):
    encoder = Encoder()

    encoder.start()

    encoder.write(struct.pack(str(len(chain_id)) + 's', chain_id), Numbers.OctetString)
    encoder.write(bytes(tx['ref_block_num']), Numbers.OctetString)
    encoder.write(bytes(tx['ref_block_prefix']), Numbers.OctetString)
    encoder.write(bytes(tx['expiration']), Numbers.OctetString)
    encoder.write(bytes(tx['operations'].length), Numbers.OctetString)
    for opIdx in range(0, len(tx.toJson()['operations'])):
        encoder.write(bytes([tx['operations'].data[opIdx].opId]), Numbers.OctetString)
        encoder.write(bytes(tx['operations'].data[opIdx].op), Numbers.OctetString)

    if 'extension' in tx:
        encoder.write(bytes(tx['extension']), Numbers.OctetString)
    else:
        encoder.write(bytes([0]), Numbers.OctetString)

    return encoder.output()

def parse_bip32_path(path):
    if len(path) == 0:
        return bytes([])
    result = bytes([])
    elements = path.split('/')
    for pathElement in elements:
        element = pathElement.split('\'')
        if len(element) == 1:
            result = result + struct.pack(">I", int(element[0]))
        else:
            result = result + struct.pack(">I", 0x80000000 | int(element[0]))
    return result


# Main()
if __name__ == "__main__":

    bkgnd = "light blue"

    # create a GUI window
    gui = Tk()
    gui.configure(background=bkgnd)
    gui.title("BitShares Ledger Nano Tip Bot")
    gui.geometry("600x320")

    # Labels and Such
    label01 = Label(gui, text="BitShares Tips via Ledger Nano S",
                    font=("Times", 24, "bold"),
                    background=bkgnd,
                    #relief="groove"
                   )
    label01.pack(pady=40)


    # Destination Frame
    frame01 = Frame(gui, background = bkgnd)
    frame01.pack(pady=10)

    label02 = Label(frame01, text="Send To: (BitShares User Account)",
                    font=("Helvetica", 16),
                    background=bkgnd,
                    #relief="groove"
                   )
    label02.pack(side="left")

    to_account_name = Entry(frame01)
    to_account_name.pack(side="left", padx=10)

    button_send = Button(gui, text="Send Tip!", command=lambda: sendTip(to_account_name.get()))
    button_send.pack(pady=40)

    label03 = Label(gui,
                    text="Click ''Send!'' to receive 2.0 BTS tip signed by Ledger Nano S hardware wallet...",
                    font=("Helvetica", 12, "italic"),
                    background=bkgnd,
                    #relief="groove"
                   )
    label03.pack()


    # start the GUI
    gui.mainloop()