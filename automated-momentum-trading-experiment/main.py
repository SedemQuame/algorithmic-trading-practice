import os
import logging
import asyncio
import argparse
import collections
from typing import List, Dict, Any
from deriv_api import DerivAPI
from dotenv import load_dotenv
from MomentumTrader import MomentumTrader
from RiskManagement import RiskManagement

load_dotenv()


async def run_trading_logic(api: DerivAPI, contracts: List[Dict[str, Any]], arguments: argparse.Namespace) -> None:
    """Trading logic, that uses the momentum trading strategy."""
    trader = MomentumTrader(api, arguments, contracts)
    await trader.trading_logic()


async def run_risk_management_logic(api: DerivAPI, contracts: List[Dict[str, Any]]) -> None:
    risk = RiskManagement(api, contracts)
    await risk.risk_management_logic()


async def run_tasks(api: DerivAPI, arguments: argparse.Namespace) -> None:
    contracts = collections.deque([])
    risk_task = asyncio.create_task(run_risk_management_logic(api, contracts))
    trading_task = asyncio.create_task(
        run_trading_logic(api, contracts, arguments))
    await asyncio.gather(trading_task, risk_task)


async def main(arguments: argparse.Namespace) -> None:
    # Deriv API endpoint and app_id
    app_id = os.getenv("APP_ID")
    api_token = os.getenv("DERIV_API")

    # Connect to Deriv API
    api = DerivAPI(app_id=app_id)
    await api.authorize(api_token)
    await run_tasks(api, args)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--symbol", default="R_100", choices=['1HZ10V', 'R_10', '1HZ25V', 'R_25', '1HZ50V', 'R_50', '1HZ75V', 'R_75', '1HZ100V', 'R_100', '1HZ150V', '1HZ250V', 'OTC_DJI'])
    parser.add_argument("-p", "--proposal_amount", default=1, type=int)
    # the default amount to by a proposal at.
    parser.add_argument("-a", "--amount", default=10, type=int)
    # the default run time for a contract should be 1 full day (intraday trading)
    parser.add_argument("-d", "--duration", default=86400, type=int)
    # target to take profits at.
    parser.add_argument("-t", "--target", default=4, type=int)
    # run the script in demo mode.
    parser.add_argument("-e", "--demo", action='store_true')
    args = parser.parse_args()
    asyncio.run(main(args))