import pprint
import asyncio
import argparse
import numpy as np
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
from deriv_api import DerivAPI


class MomentumTrader():
    """Class that implements momentum based strategy."""
    def __init__(self, api: DerivAPI, arguments: argparse.Namespace, contracts: List[Dict[str, Any]]) -> None:
        self.position = 0
        self.momentum = 3
        self.bar_length = '1min'
        self.raw_data = pd.DataFrame()
        self.min_length = self.momentum + 1
        self.api = api
        self.arguments = arguments
        self.contracts = contracts
        self.data = pd.DataFrame()
        self.resample_rate = '30S'


    async def buy_proposal(self, proposal: Dict[str, Any], price: int) -> Dict[str, Any]:
        proposal_id = proposal.get("proposal").get("id")
        buy = await self.api.buy({"buy": proposal_id, "price": int(price)})
        return buy


    async def create_options_contract(self, contract_type: str, spot_price: float) -> None:
        """Creates options contracts, on deriv.com"""
        proposal = await self.api.proposal(
            {
                "proposal": self.arguments.proposal_amount,
                "amount": self.arguments.amount,
                "barrier": "+0.10",
                "basis": "payout",
                "contract_type": contract_type,
                "currency": "USD",
                "duration": self.arguments.duration,
                "duration_unit": "s",
                "symbol": self.arguments.symbol
            }
        )
        if (
            "error" not in proposal
            and "proposal" in proposal
        ):
            # Place buy order
            print(f"Trading:- Buying {contract_type} contract @ {spot_price}")
            new_contract = await self.buy_proposal(proposal, spot_price)
            self.contracts.append({
                'contract_id': new_contract["buy"]["contract_id"],
                'pnl': 0,
                'buy_price': new_contract["buy"]["buy_price"],
                'possible_payout': new_contract["buy"]["payout"],
                'start_time': new_contract["buy"]["start_time"],
                'side': contract_type,
                'status': "active"
            })


    def convert_timestamp(self, timestamp: float) -> str:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime('%Y-%m-%d %H:%M:%S.%f')


    async def trading_logic(self) -> None:
        # Initialize variables
        last_price = None
        prev_price = None
        curr_balance = 0
        account = await self.api.balance()
        intial_balance = account["balance"]["balance"]
        line_str = "*" * 30

        # Momentum strategy parameters
        while True:
            print("\n" + line_str)
            print("Trading logic.")
            print(line_str)

            print("Raw data.")
            pprint.pprint(self.raw_data)

            account = await self.api.balance()
            curr_balance = account["balance"]["balance"]
            print(f"\nCurrent account balance: {curr_balance}")
            print(f"Initial account balance: {intial_balance}")

            proposal = await self.api.proposal(
                {
                    "proposal": self.arguments.proposal_amount,
                    "amount": self.arguments.amount,
                    "barrier": "+0.1",
                    "basis": "payout",
                    "contract_type": "PUT",
                    "currency": "USD",
                    "duration": self.arguments.duration,
                    "duration_unit": "s",
                    "symbol": self.arguments.symbol,
                }
            )
            spot_price = proposal["proposal"]["spot"]
            spot_time = proposal["proposal"]["spot_time"]

            if curr_balance > intial_balance / 2 and last_price is not None:
                row = pd.DataFrame(
                    {'bid': spot_price}, index=[pd.Timestamp(self.convert_timestamp(spot_time))])
                self.raw_data = self.raw_data._append(row)
                self.data = self.raw_data.resample(
                    self.resample_rate).last().ffill().iloc[:-1]
                self.data['mid'] = self.data.mean(axis=1)
                self.data['returns'] = np.log(
                    self.data['mid'] / self.data['mid'].shift(1))
                self.data['position'] = np.sign(
                    self.data['returns'].rolling(self.momentum).mean())

                print("\nData")
                pprint.pprint(self.data)

                if len(self.data) > self.min_length:
                    self.min_length += 1
                    if self.data['position'].iloc[-1] == 1:
                        if self.position == 0 or self.position == -1:
                            await self.create_options_contract("CALL", spot_price)
                        self.position = 1
                    elif self.data['position'].iloc[-1] == -1:
                        if self.position == 0 or self.position == 1:
                            await self.create_options_contract("PUT", spot_price)
                        self.position = -1

            prev_price = last_price
            last_price = spot_price
            print(f"\nPrevious price: {prev_price}, Last price: {last_price}")
            print(line_str + "\n")

            if curr_balance > intial_balance + self.arguments.target:
                print(f"Reached targeted amount.\nExiting script.")
                exit()
            await asyncio.sleep(5)
