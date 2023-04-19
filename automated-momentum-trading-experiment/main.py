import os
import time
import pprint
import asyncio
from datetime import datetime
from deriv_api import DerivAPI
from dotenv import load_dotenv

load_dotenv()

async def buy_proposal(api, proposal, price):
    proposal_id = proposal.get('proposal').get('id')
    buy = await api.buy({"buy": proposal_id, "price": price})
    return buy

async def sell_contract(api, contract, price):
    contract_id = contract.get('buy').get('contract_id')
    sell = await api.sell({"sell": contract_id, "price": price})
    return(sell)

async def main():
# Deriv API endpoint and app_id
    app_id = os.getenv('APP_ID')
    api_token = os.getenv('DERIV_API')

    # Initialize variables
    last_price = None
    prev_price = None
    last_time = None
    curr_time = None
    contract = None

    # Momentum strategy parameters
    momentum_period = 4
    threshold = 0.5

    # Connect to Deriv API
    api = DerivAPI(app_id=app_id)
    authorize = await api.authorize(api_token)
    pprint.pprint(f"Authorization: {authorize}\n")

    account = await api.balance()
    pprint.pprint(f"Account: {account}\n") 


    while True:
        # Receive data from Deriv API
        proposal = await api.proposal({"proposal": 1, "amount": 2, "barrier": "+0.1", "basis": "payout",
                                "contract_type": "CALL", "currency": "USD", "duration": 60, "duration_unit": "s",
                                "symbol": "R_100"
        })

        # Check if data is candle data
        if 'spot' in proposal['proposal']:
            # Get the latest candle data
            price = proposal['proposal']['spot']
            # Check if it's a new trading period
            curr_time = datetime.utcfromtimestamp(proposal['proposal']['spot_time'])
            # print(curr_time)
            if last_time is None or (curr_time - last_time).seconds >= 30:
                last_time = curr_time
                if last_price is not None and prev_price is not None:
                    # Calculate momentum
                    momentum = last_price - prev_price
                    print(f"Momentum: {momentum}")

                    # Check if momentum is positive
                    if momentum > 0:
                        print(f"Possible buy: {threshold * (last_price - price)}")
                        # Buy if momentum is greater than threshold
                        if momentum >= threshold * (last_price - price):
                            # Place buy order
                            print(f'Buy at {price}')
                            contract = await buy_proposal(api, proposal, price)
                    # Check if momentum is negative
                    elif momentum < 0:
                        print(f"Possible sell: {threshold * (last_price - price)}")
                        # Sell if momentum is less than threshold
                        if abs(momentum) >= threshold * (price - last_price):
                            # Place sell order
                            print(f'Sell at {price}')
                            await sell_contract(api, contract, price)

        # Update previous and last price
        prev_price = last_price
        last_price = price

        # Wait for 1 second before receiving data again
        time.sleep(1)

        print(last_time, curr_time)
        print(prev_price, last_price)




asyncio.run(main())
