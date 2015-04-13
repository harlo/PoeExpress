## Dockerizing Proof of Existence

```
cd ProofOfExistence
git submodule update --init --recursive
dutils/setup.sh poe_express /path/to/your/config.json --pgpkey=/path/to/a/secret/key.asc

```

### What does a config file look like?

```
{
	"DEFAULT_SENDER_EMAIL": "hello@localhost", 
	"ADMIN_EMAIL": "your@email.com", 
	"PAYMENT_ADDRESS": "as per your blockchain.info account", 
	"SECRET_ADMIN_PATH": "secret/admin/path/on/deployment",
	"BLOCKCHAIN_WALLET_GUID" : "from blockchain.info",
	"BLOCKCHAIN_PASSWORD_1" : "for encryption",
	"BLOCKCHAIN_PASSWORD_2" : "for double-encryption, so they say"
}
```