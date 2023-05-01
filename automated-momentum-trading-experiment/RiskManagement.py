import logging
import pprint
import asyncio
from typing import List, Dict, Any
from deriv_api import DerivAPI
import deriv_api.errors

class RiskManagement():
    def __init__(self, api: DerivAPI, contracts: List[Dict[str, Any]]) -> None:
        self.api = api
        self.contracts = contracts


    async def risk_management_logic(self) -> None:
        while True:
            print("\n" + "*" * 30)
            print("Risk logic.")
            print("*" * 30)

            pprint.pprint(self.contracts)
            # Check PNL on all active contracts
            for contract_info in self.contracts:
                if contract_info['status'] == "active":
                    try:
                        contract_info = await self.api.proposal_open_contract()
                        pnl = contract_info['proposal_open_contract']['profit']
                        contract_id = contract_info['proposal_open_contract']['contract_id']
                        req_id = contract_info['req_id']
                        sell_contract = {
                            'price': 0,
                            'req_id': req_id,
                            'sell': contract_id,
                        }
                        # Exit trade if momentum of contract price has approached the calculated_loss
                        if pnl <= -0.40:
                            logging.info(
                                "Risk management:- Sell the contract, when pnl is -0.40.")
                            await self.api.sell(sell_contract)
                        if pnl >= 0.50:
                            logging.info(
                                "Risk management:- Sell the contract, when pnl is 0.50.")
                            await self.api.sell(sell_contract)
                    except deriv_api.errors.ResponseError as e:
                        print("Error occurred:", str(e))
                    except Exception as e:
                        print("Error occurred:", str(e))
            print("\n")
            await asyncio.sleep(5)

