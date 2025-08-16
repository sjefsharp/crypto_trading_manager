"""
Type stubs for python_bitvavo_api library
"""

from typing import Any, Callable, Dict, List, Optional, Union

class Bitvavo:
    def __init__(self, options: Dict[str, Any] = ...) -> None: ...

    # Rate limiting
    def getRemainingLimit(self) -> int: ...
    def updateRateLimit(self, response: Union[Dict[str, Any], Any]) -> None: ...

    # Public endpoints
    def time(self) -> Dict[str, Any]: ...
    def markets(
        self, options: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]: ...
    def assets(
        self, options: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]: ...
    def book(
        self, symbol: str, options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]: ...
    def publicTrades(
        self, symbol: str, options: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]: ...
    def candles(
        self,
        symbol: str,
        interval: str,
        options: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        start: Optional[Any] = None,
        end: Optional[Any] = None,
    ) -> List[List[Union[int, str]]]: ...
    def tickerPrice(
        self, options: Optional[Dict[str, Any]] = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]: ...
    def tickerBook(
        self, options: Optional[Dict[str, Any]] = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]: ...
    def ticker24h(
        self, options: Optional[Dict[str, Any]] = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]: ...

    # Private endpoints
    def placeOrder(
        self, market: str, side: str, orderType: str, body: Dict[str, Any]
    ) -> Dict[str, Any]: ...
    def getOrder(self, market: str, orderId: str) -> Dict[str, Any]: ...
    def updateOrder(
        self, market: str, orderId: str, body: Dict[str, Any]
    ) -> Dict[str, Any]: ...
    def cancelOrder(
        self, market: str, orderId: str, operatorId: Optional[str] = None
    ) -> Dict[str, Any]: ...
    def getOrders(
        self, market: str, options: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]: ...
    def cancelOrders(
        self, options: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]: ...
    def ordersOpen(
        self, options: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]: ...
    def trades(
        self, market: str, options: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]: ...
    def account(self) -> Dict[str, Any]: ...
    def fees(self, market: Optional[str] = None) -> Dict[str, Any]: ...
    def balance(
        self, options: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]: ...
    def depositAssets(self, symbol: str) -> Dict[str, Any]: ...
    def withdrawAssets(
        self, symbol: str, amount: str, address: str, body: Dict[str, Any]
    ) -> Dict[str, Any]: ...
    def depositHistory(
        self, options: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]: ...
    def withdrawalHistory(
        self, options: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]: ...

    # WebSocket
    def newWebsocket(self) -> "BitvavoWebSocket": ...

class BitvavoWebSocket:
    def __init__(
        self,
        APIKEY: str,
        APISECRET: str,
        ACCESSWINDOW: int,
        WSURL: str,
        bitvavo: Bitvavo,
    ) -> None: ...
    def closeSocket(self) -> None: ...
    def setErrorCallback(self, callback: Callable[[Dict[str, Any]], None]) -> None: ...

    # Public WebSocket methods
    def time(self, callback: Callable[[Dict[str, Any]], None]) -> None: ...
    def markets(
        self, options: Dict[str, Any], callback: Callable[[List[Dict[str, Any]]], None]
    ) -> None: ...
    def assets(
        self, options: Dict[str, Any], callback: Callable[[List[Dict[str, Any]]], None]
    ) -> None: ...
    def book(
        self,
        market: str,
        options: Dict[str, Any],
        callback: Callable[[Dict[str, Any]], None],
    ) -> None: ...
    def publicTrades(
        self,
        market: str,
        options: Dict[str, Any],
        callback: Callable[[List[Dict[str, Any]]], None],
    ) -> None: ...
    def candles(
        self,
        market: str,
        interval: str,
        options: Dict[str, Any],
        callback: Callable[[List[List[Union[int, str]]]], None],
    ) -> None: ...
    def ticker24h(
        self,
        options: Dict[str, Any],
        callback: Callable[[Union[Dict[str, Any], List[Dict[str, Any]]]], None],
    ) -> None: ...
    def tickerPrice(
        self,
        options: Dict[str, Any],
        callback: Callable[[Union[Dict[str, Any], List[Dict[str, Any]]]], None],
    ) -> None: ...
    def tickerBook(
        self,
        options: Dict[str, Any],
        callback: Callable[[Union[Dict[str, Any], List[Dict[str, Any]]]], None],
    ) -> None: ...

    # Private WebSocket methods
    def placeOrder(
        self,
        market: str,
        side: str,
        orderType: str,
        body: Dict[str, Any],
        callback: Callable[[Dict[str, Any]], None],
    ) -> None: ...
    def getOrder(
        self, market: str, orderId: str, callback: Callable[[Dict[str, Any]], None]
    ) -> None: ...
    def updateOrder(
        self,
        market: str,
        orderId: str,
        body: Dict[str, Any],
        callback: Callable[[Dict[str, Any]], None],
    ) -> None: ...
    def cancelOrder(
        self,
        market: str,
        orderId: str,
        callback: Callable[[Dict[str, Any]], None],
        operatorId: Optional[str] = None,
    ) -> None: ...
    def getOrders(
        self,
        market: str,
        options: Dict[str, Any],
        callback: Callable[[List[Dict[str, Any]]], None],
    ) -> None: ...
    def cancelOrders(
        self, options: Dict[str, Any], callback: Callable[[List[Dict[str, Any]]], None]
    ) -> None: ...
    def ordersOpen(
        self, options: Dict[str, Any], callback: Callable[[List[Dict[str, Any]]], None]
    ) -> None: ...
    def trades(
        self,
        market: str,
        options: Dict[str, Any],
        callback: Callable[[List[Dict[str, Any]]], None],
    ) -> None: ...
    def account(self, callback: Callable[[Dict[str, Any]], None]) -> None: ...
    def fees(
        self, market: str, callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> None: ...
    def balance(
        self, options: Dict[str, Any], callback: Callable[[List[Dict[str, Any]]], None]
    ) -> None: ...
    def depositAssets(
        self, symbol: str, callback: Callable[[Dict[str, Any]], None]
    ) -> None: ...
    def withdrawAssets(
        self,
        symbol: str,
        amount: str,
        address: str,
        body: Dict[str, Any],
        callback: Callable[[Dict[str, Any]], None],
    ) -> None: ...
    def depositHistory(
        self, options: Dict[str, Any], callback: Callable[[List[Dict[str, Any]]], None]
    ) -> None: ...
    def withdrawalHistory(
        self, options: Dict[str, Any], callback: Callable[[List[Dict[str, Any]]], None]
    ) -> None: ...

    # Subscription methods
    def subscriptionTicker(
        self, market: str, callback: Callable[[Dict[str, Any]], None]
    ) -> None: ...
    def subscriptionTicker24h(
        self, market: str, callback: Callable[[Dict[str, Any]], None]
    ) -> None: ...
    def subscriptionAccount(
        self, market: str, callback: Callable[[Dict[str, Any]], None]
    ) -> None: ...
    def subscriptionCandles(
        self,
        market: str,
        interval: str,
        callback: Callable[[List[List[Union[int, str]]]], None],
    ) -> None: ...
    def subscriptionTrades(
        self, market: str, callback: Callable[[List[Dict[str, Any]]], None]
    ) -> None: ...
    def subscriptionBookUpdate(
        self, market: str, callback: Callable[[Dict[str, Any]], None]
    ) -> None: ...
    def subscriptionBook(
        self, market: str, callback: Callable[[Dict[str, Any]], None]
    ) -> None: ...
