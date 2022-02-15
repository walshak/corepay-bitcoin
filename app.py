from flask import Flask, request, jsonify, Response
from bitcoinlib.mnemonic import Mnemonic
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import os

from markupsafe import re

#global vars
db_uri = 'mysql://root:18781875Core@localhost:3306/corepay_btc'

base_url = 'http://corepago:18781875Core@localhost:18332'
bdc = AuthServiceProxy(base_url)
wallet_name_default = 'hkmnnjjmmkmkk'
passphrase_default = "just anchor glance brown person liquid pair joy word clip effort broccoli"
#txid = 'e0cee8955f516d5ed333d081a4e2f55b999debfff91a49e8123d20f7ed647ac5'
#rt = bdc.getrawtransaction(txid)
#print("Raw: %s" % rt)

# init app
app = Flask(__name__)
# app.config["MYSQL_HOST"]="localhost"
# app.config["MYSQL_USER"]="corepay"


@app.route('/wallet/create', methods=['POST'])
def create_wallet():
    global bdc
    
    #get posted wallet name
    wallet_name = request.json['wallet_name']
    
    # create a Mnemonic phrase/masterkey
    passphrase = Mnemonic().generate()
    
    try:
        #create wallet
        bdc.createwallet(wallet_name,False, False, passphrase)
        
        try:
            #reload wallet
            bdc.unloadwallet(wallet_name)
            bdc.loadwallet(wallet_name)
            
            try:
                #add wallet precision to bdc base_url so that getwalletinfo() will work
                bdc = AuthServiceProxy(base_url+'/wallet/'+wallet_name)
                try:
                    #get wallet info
                    info = bdc.getwalletinfo()
                    
                    #format and snd response
                    return jsonify({'passphrase':passphrase,'info':info})
                except JSONRPCException as e:
                    return Response('Error: {}'.format(str(e)), status=500, mimetype='application/json')
            except JSONRPCException as e:
                return Response('Error: {}'.format(str(e)), status=500, mimetype='application/json')
        except JSONRPCException as e:
            return Response('Error: {}'.format(str(e)), status=500, mimetype='application/json')
     
    except JSONRPCException as e:
        return Response('Error: {}'.format(str(e)), status=500, mimetype='application/json')
    
       
@app.route('/wallet/balance',methods=['GET'])
def get_balance():
    wallet_name = request.json['wallet_name']

    #set wallet_name
    if wallet_name == "":
        wallet_name = wallet_name_default

    try:
        #add wallet precision to bdc base_url so that getnewaddress() will work
        bdc = AuthServiceProxy(base_url+'/wallet/'+wallet_name)

        try:
            # get new wallet address
            bal = bdc.getbalance()
            bal_details = bdc.getbalances()
            #use the key to create a payment address
            return jsonify(balance = bal, bal_details = bal_details)
        except JSONRPCException as e:
            return Response('Error: {}'.format(str(e)), status=500, mimetype='application/json')
    except JSONRPCException as e:
        return Response('Error: {}'.format(str(e)), status=500, mimetype='application/json')

@app.route('/wallet/get-wallet-info', methods=['GET'])
def get_wallet_info():
    global bdc
    global wallet_name_default

    wallet_name = request.json['wallet_name']

    #set the name of the wallet
    if wallet_name == "":
        wallet_name = wallet_name_default
    
    try:
        #add wallet precision to bdc base_url so that getnewaddress() will work
        bdc = AuthServiceProxy(base_url+'/wallet/'+wallet_name)

        try:
            # get the wallet address info
            info = bdc.getwalletinfo()

            #return info about the given wallet
            return jsonify(info)
        except JSONRPCException as e:
            return Response('Error: {}'.format(str(e)), status=500, mimetype='application/json')
    except JSONRPCException as e:
        return Response('Error: {}'.format(str(e)), status=500, mimetype='application/json')



@app.route('/wallet/get-address', methods=['GET'])
def get_address():
    global bdc
    global wallet_name_default

    wallet_name = request.json['wallet_name']
    label = request.json['label']

    #set the name of the wallet
    if wallet_name == "":
        wallet_name = wallet_name_default
    
    try:
        #add wallet precision to bdc base_url so that getnewaddress() will work
        bdc = AuthServiceProxy(base_url+'/wallet/'+wallet_name)

        try:
            # get new wallet address
            address = bdc.getnewaddress(label)
            address = bdc.getaddressinfo(address)
            #use the key to create a payment address
            return jsonify(address)
        except JSONRPCException as e:
            return Response('Error: {}'.format(str(e)), status=500, mimetype='application/json')
    except JSONRPCException as e:
        return Response('Error: {}'.format(str(e)), status=500, mimetype='application/json')

@app.route('/wallet/get-address-info', methods=['GET'])
def get_address_info():
    global bdc
    global wallet_name_default

    wallet_name = request.json['wallet_name']
    address = request.json['address']

    #set the name of the wallet
    if wallet_name == "":
        wallet_name = wallet_name_default
    
    try:
        #add wallet precision to bdc base_url so that getnewaddress() will work
        bdc = AuthServiceProxy(base_url+'/wallet/'+wallet_name)

        try:
            # get the wallet address info
            info = bdc.getaddressinfo(address)

            #return info about the given address
            return jsonify(info)
        except JSONRPCException as e:
            return Response('Error: {}'.format(str(e)), status=500, mimetype='application/json')
    except JSONRPCException as e:
        return Response('Error: {}'.format(str(e)), status=500, mimetype='application/json')

@app.route('/wallet/dump-wallet-info', methods=['GET'])
def dump_wallet_info():
    global bdc
    global wallet_name_default

    wallet_name = request.json['wallet_name']
    filename = request.json['filename']
    passphrase = request.json['passphrase']

    #set the name of the wallet
    if wallet_name == "":
        wallet_name = wallet_name_default
    
    #set default passphrase 
    if passphrase == "":
        passphrase = passphrase_default
    
    try:
        #add wallet precision to bdc base_url so that getnewaddress() will work
        bdc = AuthServiceProxy(base_url+'/wallet/'+wallet_name)

        try:
            #use the passphrase to unlock the wallet
            bdc.walletpassphrase(passphrase,120)
            try:
                # get the wallet address info and dump in a file
                info = bdc.dumpwallet('/home/walshak/'+filename)

                #return info about the given wallet
                return jsonify(info)
            except JSONRPCException as e:
                return Response('Error: {}'.format(str(e)), status=500, mimetype='application/json')
            
        except JSONRPCException as e:
            return Response('Error: {}'.format(str(e)), status=500, mimetype='application/json')
    except JSONRPCException as e:
        return Response('Error: {}'.format(str(e)), status=500, mimetype='application/json')

    
    
    

@app.route('/wallet/send', methods=['POST'])
def send_to():
    wallet_name = request.json['wallet_name']
    reciever_address = request.json['reciever_address']
    amount = request.json['amount']
    rx_name = request.json['reciever_name']
    tx_desc = request.json['description']
    subtract_fee = request.json['subtract_fee']
    passphrase = request.json['passphrase']

    #open wallet
    #set the name of the wallet
    if wallet_name == "":
        wallet_name = wallet_name_default

    if passphrase == "":
        passphrase = passphrase_default
    
    try:
        #add wallet precision to bdc base_url so that getnewaddress() will work
        bdc = AuthServiceProxy(base_url+'/wallet/'+wallet_name)

        try:
            bdc.walletpassphrase(passphrase,120)

            try:
                # send
                tx_id = bdc.sendtoaddress(reciever_address,amount,tx_desc,rx_name,subtract_fee)
                # get the wallet tx info
                tx = bdc.gettransaction(tx_id,True,True)
                #return info about the tx 
                return jsonify({'tx':tx})
            except JSONRPCException as e:
                return Response('Error: {}'.format(str(e)), status=500, mimetype='application/json')
        except JSONRPCException as e:
            return Response('Error: {}'.format(str(e)), status=500, mimetype='application/json')
    except JSONRPCException as e:
        return Response('Error: {}'.format(str(e)), status=500, mimetype='application/json')

    

@app.route('/wallet/tx/status',methods=['GET'])
def tx_status():
    wallet_name = request.json['wallet_name']
    tx_id = request.json['tx_id']
    
    #open wallet
    #set the name of the wallet
    if wallet_name == "":
        wallet_name = wallet_name_default
    
    try:
        #add wallet precision to bdc base_url so that getnewaddress() will work
        bdc = AuthServiceProxy(base_url+'/wallet/'+wallet_name)
        try:
            # get the wallet tx info
            tx = bdc.gettransaction(tx_id,True,True)

            #return info about the given tx
            return jsonify(tx)
        except JSONRPCException as e:
            return Response('Error: {}'.format(str(e)), status=500, mimetype='application/json')
    except JSONRPCException as e:
        return Response('Error: {}'.format(str(e)), status=500, mimetype='application/json')

@app.route('/wallet/tx/list',methods=['GET'])
def tx_list():
    wallet_name = request.json['wallet_name']
    label = request.json['label']
    count = request.json['count']
    skip = request.json['skip']
    
    #open wallet
    #set the name of the wallet
    if wallet_name == "":
        wallet_name = wallet_name_default
    #return wallet_name
    
    try:
        #add wallet precision to bdc base_url so that getnewaddress() will work
        bdc = AuthServiceProxy(base_url+'/wallet/'+wallet_name)
        try:
            # get the wallet address info
            tx = bdc.listtransactions(label,count,skip)

            #return info about the given tx
            return jsonify(tx)
        except JSONRPCException as e:
            return Response('Error: {}'.format(str(e)), status=500, mimetype='application/json')
    except JSONRPCException as e:
        return Response('Error: {}'.format(str(e)), status=500, mimetype='application/json')


# start server
if __name__ == '__main__':
    app.run(debug=True)
