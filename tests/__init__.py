from unicex.enums import OrderType, Exchange


print(OrderType.LIMIT.to_exchange_format(Exchange.BINANCE))
