# Superkernel

Integração com a Polygon Mainnet e oráculo TACE para registrar evoluções do organismo digital diretamente on-chain.

## Uso rápido
1. Crie um `.env` baseado em `.env.example` com `POLYGON_PRIVATE_KEY`, `POSE_CONTRACT_ADDRESS` e o ABI do contrato PoSE.
2. Para recursos on-chain, instale os extras opcionais: `pip install ".[polygon]"`.
3. Execute o CLI para ativar o oráculo:
   ```bash
   python -m ui.cli.superkernel_cli
   ```

## Modo Zero Dependency (sem pip)
Para ambientes que bloqueiam downloads de dependências, use a edição ZDL (zero dependency):
```bash
python -m ui.cli.cli_zdl
```
Ela utiliza o `SuperkernelZDL` e o `TACEOracleZDL`, ambos escritos apenas com a biblioteca padrão.

## Contrato PoSE
O contrato `contracts/PoSE.sol` registra métricas e eventos de evolução TACE na Polygon. Compile e faça o deploy para obter o endereço usado pelo oráculo.
