__all__ = ["Client"]


from unicex._base import BaseClient
from unicex.utils import filter_params


class Client(BaseClient):
    """Клиент для работы с Hyperliquid API."""

    _BASE_URL = "https://api.hyperliquid.xyz"
    """Базовый URL для REST API Hyperliquid."""

    # topic: Info endpoint: Spot

    async def spot_metadata(self) -> dict:
        """Получение метаданных спотового рынка.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/spot#retrieve-spot-metadata
        """
        url = self._BASE_URL + "/info"
        data = filter_params({"type": "spotMeta"})

        return await self._make_request("POST", url, data=data)

    async def spot_asset_contexts(self) -> list:
        """Получение контекстов спотовых активов.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/spot#retrieve-spot-asset-contexts
        """
        url = self._BASE_URL + "/info"
        data = filter_params({"type": "spotMetaAndAssetCtxs"})

        return await self._make_request("POST", url, data=data)

    async def spot_token_balances(self, user: str) -> dict:
        """Получение балансов пользователя на спотовом рынке.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/spot#retrieve-a-users-token-balances
        """
        url = self._BASE_URL + "/info"
        data = filter_params({"type": "spotClearinghouseState", "user": user})

        return await self._make_request("POST", url, data=data)

    async def spot_deploy_state(self, user: str) -> dict:
        """Получение сведений об аукционе развертывания спотовых токенов.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/spot#retrieve-information-about-the-spot-deploy-auction
        """
        url = self._BASE_URL + "/info"
        data = filter_params({"type": "spotDeployState", "user": user})

        return await self._make_request("POST", url, data=data)

    async def spot_pair_deploy_auction_status(self) -> dict:
        """Получение статуса аукциона развертывания спотовых пар.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/spot#retrieve-information-about-the-spot-pair-deploy-auction
        """
        url = self._BASE_URL + "/info"
        data = filter_params({"type": "spotPairDeployAuctionStatus"})

        return await self._make_request("POST", url, data=data)

    async def token_details(self, token_id: str) -> dict:
        """Получение сведений о спотовом токене.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/spot#retrieve-information-about-a-token
        """
        url = self._BASE_URL + "/info"
        data = filter_params({"type": "tokenDetails", "tokenId": token_id})

        return await self._make_request("POST", url, data=data)

    # topic: Info endpoint: Perpetuals

    async def perp_dexs(self) -> list:
        """Получение списка всех perpetual DEX.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals#retrieve-all-perpetual-dexs
        """
        url = self._BASE_URL + "/info"
        data = filter_params({"type": "perpDexs"})

        return await self._make_request("POST", url, data=data)

    async def perp_metadata(self, dex: str | None = None) -> dict:
        """Получение метаданных perpetual-рынка.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals#retrieve-perpetuals-metadata-universe-and-margin-tables
        """
        url = self._BASE_URL + "/info"
        data = filter_params({"type": "meta", "dex": dex})

        return await self._make_request("POST", url, data=data)

    async def perp_asset_contexts(self) -> list:
        """Получение контекстов perpetual-активов.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals#retrieve-perpetuals-asset-contexts-includes-mark-price-current-funding-open-interest-etc
        """
        url = self._BASE_URL + "/info"
        data = filter_params({"type": "metaAndAssetCtxs"})

        return await self._make_request("POST", url, data=data)

    async def perp_account_summary(self, user: str, dex: str | None = None) -> dict:
        """Получение сводки по perpetual-счету пользователя.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals#retrieve-users-perpetuals-account-summary
        """
        url = self._BASE_URL + "/info"
        data = filter_params({"type": "clearinghouseState", "user": user, "dex": dex})

        return await self._make_request("POST", url, data=data)

    async def user_funding_history(
        self,
        user: str,
        start_time: int,
        end_time: int | None = None,
    ) -> list:
        """Получение истории фондирования пользователя.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals#retrieve-a-users-funding-history-or-non-funding-ledger-updates
        """
        url = self._BASE_URL + "/info"
        data = filter_params(
            {
                "type": "userFunding",
                "user": user,
                "startTime": start_time,
                "endTime": end_time,
            }
        )

        return await self._make_request("POST", url, data=data)

    async def user_non_funding_ledger_updates(
        self,
        user: str,
        start_time: int,
        end_time: int | None = None,
    ) -> list:
        """Получение нефондовых операций пользователя.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals#retrieve-a-users-funding-history-or-non-funding-ledger-updates
        """
        url = self._BASE_URL + "/info"
        data = filter_params(
            {
                "type": "userNonFundingLedgerUpdates",
                "user": user,
                "startTime": start_time,
                "endTime": end_time,
            }
        )

        return await self._make_request("POST", url, data=data)

    async def funding_history(
        self,
        coin: str,
        start_time: int,
        end_time: int | None = None,
    ) -> list:
        """Получение исторических ставок фондирования.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals#retrieve-historical-funding-rates
        """
        url = self._BASE_URL + "/info"
        data = filter_params(
            {
                "type": "fundingHistory",
                "coin": coin,
                "startTime": start_time,
                "endTime": end_time,
            }
        )

        return await self._make_request("POST", url, data=data)

    async def predicted_fundings(self) -> list:
        """Получение прогнозируемых ставок фондирования по площадкам.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals#retrieve-predicted-funding-rates-for-different-venues
        """
        url = self._BASE_URL + "/info"
        data = filter_params({"type": "predictedFundings"})

        return await self._make_request("POST", url, data=data)

    async def perps_at_open_interest_cap(self) -> list:
        """Получение списка инструментов на пределе открытого интереса.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals#query-perps-at-open-interest-caps
        """
        url = self._BASE_URL + "/info"
        data = filter_params({"type": "perpsAtOpenInterestCap"})

        return await self._make_request("POST", url, data=data)

    async def perp_deploy_auction_status(self) -> dict:
        """Получение статуса аукциона развертывания perpetual-рынка.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals#retrieve-information-about-the-perp-deploy-auction
        """
        url = self._BASE_URL + "/info"
        data = filter_params({"type": "perpDeployAuctionStatus"})

        return await self._make_request("POST", url, data=data)

    async def active_asset_data(self, user: str, coin: str) -> dict:
        """Получение актуальных данных по активу пользователя.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals#retrieve-users-active-asset-data
        """
        url = self._BASE_URL + "/info"
        data = filter_params({"type": "activeAssetData", "user": user, "coin": coin})

        return await self._make_request("POST", url, data=data)

    async def perp_dex_limits(self, dex: str) -> dict:
        """Получение лимитов для perpetual DEX, созданного билдерами.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals#retrieve-builder-deployed-perp-market-limits
        """
        url = self._BASE_URL + "/info"
        data = filter_params({"type": "perpDexLimits", "dex": dex})

        return await self._make_request("POST", url, data=data)
