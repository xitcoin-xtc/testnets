# Xitchain Testnets

Canonical genesis and public configuration files for the Xitchain test networks. Xitchain is the proof-of-stake chain of XTC, built with the Cosmos SDK and compatible with the EVM. Mainnet is not launched; its identifiers `xitcoin` and `101088` are reserved.

## Active public testnet

| Parameter | Value |
| --- | --- |
| Network | Xitchain Testnet |
| Cosmos chain ID | `xitcoin-testnet-v2-1` |
| EVM chain ID | `101089` (`0x18ae1`) |
| Native symbol | `XTC` |
| Base denomination | `axtc` |
| Decimals | `18` |
| Genesis supply | `477,000,000 XTC` |
| Genesis SHA-256 | `5db34acf6496b2c76a6f516e0eb605caef6762552584ddbed7c8703239f33d72` |
| Initial validators | `4` |
| Validator capacity | `258` |
| Minimum self-delegation | `5,000,000 XTC` |
| Public faucet | `10 XTC` per successful request |
| Bridge route | Initialised on 3 Sep 2026 at height `74270` (tx [`721E39…`](https://explorer-testnet.xitchain.com/xitcoin-testnet/tx/721E397ABC01D3D195B98AFE927B9ED666ED6DBC28FD1EEEA0909BC8D8AF4A5E)); disabled and paused |

The active network files are stored in [`xitcoin-testnet-v2-1`](./xitcoin-testnet-v2-1).

## Public endpoints

| Service | URL |
| --- | --- |
| CometBFT RPC | https://rpc-testnet.xitchain.com |
| REST API | https://api-testnet.xitchain.com |
| EVM JSON-RPC | https://evm-rpc-testnet.xitchain.com |
| Cosmos explorer | https://explorer-testnet.xitchain.com/xitcoin-testnet |
| EVM explorer | https://evm-explorer-testnet.xitchain.com |
| Faucet | https://faucet-testnet.xitchain.com |

Documentation: https://xitcoin.com/chain/ and https://xitcoin.com/docs/. Source code: https://github.com/xitcoin-xtc.

## Standard EVM contracts

Installed on 2026-11-28 at their usual addresses, so wallets, Safe multisig accounts and common tools work on Xitchain Testnet. The full list with deployment transactions and code hashes is in [`xitcoin-testnet-v2-1/standard-contracts.json`](./xitcoin-testnet-v2-1/standard-contracts.json).

| Contract | Address |
| --- | --- |
| Deterministic deployment proxy (CREATE2) | `0x4e59b44847b379578588920cA78FbF26c0B4956C` |
| Multicall3 | `0xcA11bde05977b3631167028862bE2a173976CA11` |
| Safe 1.3.0 GnosisSafeL2 | `0x3E5c63644E683549055b9Be8653de26E0B4CD36E` |
| Safe 1.3.0 GnosisSafe | `0xd9Db270c1B5E3Bd161E8c8503c55cEABeE709552` |
| Safe 1.3.0 GnosisSafeProxyFactory | `0xa6B71E26C5e0845f74c812102Ca7114b6a896AB2` |
| Safe 1.3.0 CompatibilityFallbackHandler | `0xf48f2B2d2a534e402487b3ee7C18c33Aec0Fe5e4` |
| Safe 1.3.0 MultiSend / MultiSendCallOnly | `0xA238CBeb142c10Ef7Ad8442C6D1f9E89e07e7761` / `0x40A2aCCbd92BCA938b02010E17A5b8929b49130D` |
| Safe 1.3.0 CreateCall / SignMessageLib / SimulateTxAccessor | `0x7cbB62EaA69F79e6873cD1ecB2392971036cFAa4` / `0xA65387F16B013cf2Af4605Ad8aA5ec25a2cbA3a2` / `0x59AD6735bCd8152B84860Cb256dD9e96b85F69Da` |
| Permit2 | `0x000000000022D473030F116dDEE9F6B43aC78BA3` |
| ERC-4337 EntryPoint v0.7 | `0x0000000071727De22E5E9d8BAf0edAc6f37da032` |

The runtime code of each contract is byte-identical to Ethereum mainnet, except Permit2, which stores the chain ID and its EIP-712 domain separator at construction. A test Safe (1 owner, threshold 1) was created through the factory and executed a signed transaction successfully.

## Bridge route

The testnet bridge route `0x21121c16…4b5cd9` (Cronos testnet 338 to Xitchain Testnet) was initialised after genesis by `MsgInitializeRouteConfig` at height `74270`, with three bridge signers, a guardian and limits of 100 XTC per transfer, 500 XTC per day and 1,000,000 XTC outstanding. It was created disabled and paused, and no resume, configuration update, attestation or outbound transfer has been recorded since. Resuming the route, changing its limits or rotating its signers needs 2 of the 3 bridge signers; the guardian can only pause. Nobody can bridge XTC today.

Verify the byte-identical genesis file with:

```bash
cd xitcoin-testnet-v2-1
sha256sum -c genesis.sha256
```

## Retired networks

[`xitcoin-testnet-1`](./xitcoin-testnet-1) is retained only for historical verification. It is not active and must not be used for new deployments or transactions.

## Planned Member State seats

[`xitcoin-testnet-1`](./xitcoin-testnet-1) also holds the reference allocation for the planned Member State validator seats. Seats and vesting are planned for mainnet and are not implemented on chain: the running software only caps the validator set at 258.

| Parameter | Value |
| --- | --- |
| Seat pool | `386,000,000 XTC` (the sovereign reserve of the testnet genesis) |
| Equal share | `1,500,000 XTC` for each of the 193 UN Member States (`289,500,000 XTC`) |
| Population pool | `96,500,000 XTC`, in proportion to the square root of each Member State's population |
| Population | UN World Population Prospects 2024, medium variant, 1 July 2026, the figure published for each Member State, used as it is |
| Rounding | Whole XTC, largest remainder, ties by ISO3 code; the total is exactly `386,000,000 XTC` |
| Smallest | Tuvalu: population 9,362, `1,511,216 XTC` |
| Median | Hungary: population 9,585,818, `1,858,884 XTC` |
| Largest | India: population 1,476,625,576, `5,954,251 XTC` |

The pool is funded from the Xitchain reserve of Kcalb Ltd (Cronos wallet `0x4993F2012D72C3cFb67eBde946481b9dbFB3F254`). At mainnet it crosses the bridge one for one, locked on Cronos, so the total supply stays 5,250,000,000 XTC.

Recompute or check the files with:

```bash
cd xitcoin-testnet-1
python3 compute-sovereign-allocation-2026.py --check
```

Add `--wpp WPP2024_TotalPopulationBySex.csv.gz` (from https://population.un.org/wpp/) to check every population against the UN file.

Private keys, mnemonics, keyrings, passwords, runtime state and validator backups must never be committed to this repository.
