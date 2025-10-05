    async def metadata(self, dex: str | None = None) -> dict:
        """Получение метаинформации о бирже.

        https://docs.chainstack.com/reference/hyperliquid-info-meta
        """
        payload = {
            "type": "meta",
            "dex": dex,
        }

        return await self._post_request("/info", data=payload)

    async def spot_metadata(self) -> dict:
        """Получение спотовой метаинформации о бирже.

        https://docs.chainstack.com/reference/hyperliquid-info-spotmeta
        """
        payload = {"type": "spotMeta"}

        return await self._post_request("/info", data=payload)

    async def clearinghouse_state(self, user: str, dex: str | None = None) -> dict:
        """Получение сводки по фьючерсному аккаунту пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-clearinghousestate
        """
        payload = {
            "type": "clearinghouseState",
            "user": user,
            "dex": dex,
        }

        return await self._post_request("/info", data=payload)

    async def spot_clearinghouse_state(self, user: str) -> dict:
        """Получение информации о балансе спотового аккаунта пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-spotclearinghousestate
        """
        payload = {
            "type": "spotClearinghouseState",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def open_orders(self, user: str, dex: str | None = None) -> list[dict]:
        """Получение списка открытых ордеров пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-openorders
        """
        payload = {
            "type": "openOrders",
            "user": user,
            "dex": dex,
        }

        return await self._post_request("/info", data=payload)

    async def exchange_status(self) -> dict:
        """Получение текущего статуса биржи Hyperliquid.

        https://docs.chainstack.com/reference/hyperliquid-info-exchangestatus
        """
        payload = {"type": "exchangeStatus"}

        return await self._post_request("/info", data=payload)

    async def frontend_open_orders(self, user: str, dex: str | None = None) -> list[dict]:
        """Получение открытых ордеров в формате фронтенда.

        https://docs.chainstack.com/reference/hyperliquid-info-frontendopenorders
        """
        payload = {
            "type": "frontendOpenOrders",
            "user": user,
            "dex": dex,
        }

        return await self._post_request("/info", data=payload)

    async def liquidatable(self, user: str) -> dict:
        """Проверка, подлежит ли аккаунт пользователя ликвидации.

        https://docs.chainstack.com/reference/hyperliquid-info-liquidatable
        """
        payload = {
            "type": "liquidatable",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def active_asset_data(self, user: str, coin: str) -> dict:
        """Получение сведений об активном фьючерсном активе пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-activeassetdata
        """
        payload = {
            "type": "activeAssetData",
            "user": user,
            "coin": coin,
        }

        return await self._post_request("/info", data=payload)

    async def max_market_order_ntls(self) -> list[dict]:
        """Получение максимальных объёмов рыночных ордеров по активам.

        https://docs.chainstack.com/reference/hyperliquid-info-maxmarketorderntls
        """
        payload = {"type": "maxMarketOrderNtls"}

        return await self._post_request("/info", data=payload)

    async def vault_summaries(self) -> list[dict]:
        """Получение сводки по всем доступным вултам (vaults).

        https://docs.chainstack.com/reference/hyperliquid-info-vaultsummaries
        """
        payload = {"type": "vaultSummaries"}

        return await self._post_request("/info", data=payload)

    async def user_vault_equities(self, user: str) -> list[dict]:
        """Получение данных об инвестициях пользователя в вулты (vaults).

        https://docs.chainstack.com/reference/hyperliquid-info-uservaultequities
        """
        payload = {
            "type": "userVaultEquities",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def leading_vaults(self, user: str) -> list[dict]:
        """Получение списка вултов (vaults), которыми управляет пользователь.

        https://docs.chainstack.com/reference/hyperliquid-info-leadingvaults
        """
        payload = {
            "type": "leadingVaults",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def extra_agents(self, user: str) -> list[dict]:
        """Получение списка дополнительных агентов пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-extraagents
        """
        payload = {
            "type": "extraAgents",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def sub_accounts(self, user: str) -> list[dict]:
        """Получение списка саб-аккаунтов пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-subaccounts
        """
        payload = {
            "type": "subAccounts",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def user_fees(self, user: str) -> dict:
        """Получение информации о торговых комиссиях пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-userfees
        """
        payload = {
            "type": "userFees",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def user_rate_limit(self, user: str) -> dict:
        """Получение сведений о лимитах запросов пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-userratelimit
        """
        payload = {
            "type": "userRateLimit",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def spot_deploy_state(self, user: str) -> dict:
        """Получение состояния системы деплоя спотовых токенов.

        https://docs.chainstack.com/reference/hyperliquid-info-spotdeploystate
        """
        payload = {
            "type": "spotDeployState",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def perp_deploy_auction_status(self) -> dict:
        """Получение статуса аукционов деплоя перпетуалов.

        https://docs.chainstack.com/reference/hyperliquid-info-perpdeployauctionstatus
        """
        payload = {"type": "perpDeployAuctionStatus"}

        return await self._post_request("/info", data=payload)

    async def delegations(self, user: str) -> list[dict]:
        """Получение списка делегаций пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-delegations
        """
        payload = {
            "type": "delegations",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def delegator_summary(self, user: str) -> dict:
        """Получение сводки по делегациям пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-delegator-summary
        """
        payload = {
            "type": "delegatorSummary",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def max_builder_fee(self, user: str, builder: str) -> int:
        """Получение максимальной комиссии билдера, одобренной пользователем.

        https://docs.chainstack.com/reference/hyperliquid-info-max-builder-fee
        """
        payload = {
            "type": "maxBuilderFee",
            "user": user,
            "builder": builder,
        }

        return await self._post_request("/info", data=payload)

    async def user_to_multi_sig_signers(self, user: str) -> list[str]:
        """Получение списка подписантов мультисиг-кошелька пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-user-to-multi-sig-signers
        """
        payload = {
            "type": "userToMultiSigSigners",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def user_role(self, user: str) -> dict:
        """Получение информации о роли пользователя в системе.

        https://docs.chainstack.com/reference/hyperliquid-info-user-role
        """
        payload = {
            "type": "userRole",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def perps_at_open_interest_cap(self) -> list[str]:
        """Получение списка перпетуалов на предельном открытом интересе.

        https://docs.chainstack.com/reference/hyperliquid-info-perps-at-open-interest-cap
        """
        payload = {"type": "perpsAtOpenInterestCap"}

        return await self._post_request("/info", data=payload)

    async def validator_l1_votes(self) -> list[dict]:
        """Получение сведений о голосах валидаторов на L1.

        https://docs.chainstack.com/reference/hyperliquid-info-validator-l1-votes
        """
        payload = {"type": "validatorL1Votes"}

        return await self._post_request("/info", data=payload)

    async def web_data2(self) -> dict:
        """Получение агрегированных данных для веб-интерфейса.

        https://docs.chainstack.com/reference/hyperliquid-info-web-data2
        """
        payload = {"type": "webData2"}

        return await self._post_request("/info", data=payload)

    async def all_mids(self, dex: str | None = None) -> dict:
        """Получение текущих средних цен по всем активам.

        https://docs.chainstack.com/reference/hyperliquid-info-allmids
        """
        payload = {
            "type": "allMids",
            "dex": dex,
        }

        return await self._post_request("/info", data=payload)

    async def user_fills(self, user: str, aggregate_by_time: bool | None = None) -> list[dict]:
        """Получение последних исполнений ордеров пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-user-fills
        """
        payload = {
            "type": "userFills",
            "user": user,
            "aggregateByTime": aggregate_by_time,
        }

        return await self._post_request("/info", data=payload)

    async def user_fills_by_time(
        self,
        user: str,
        start_time: int,
        end_time: int | None = None,
        aggregate_by_time: bool | None = None,
    ) -> list[dict]:
        """Получение исполнений ордеров пользователя за период.

        https://docs.chainstack.com/reference/hyperliquid-info-user-fills-by-time
        """
        payload = {
            "type": "userFillsByTime",
            "user": user,
            "startTime": start_time,
            "endTime": end_time,
            "aggregateByTime": aggregate_by_time,
        }

        return await self._post_request("/info", data=payload)

    async def order_status(self, user: str, oid: int | str) -> dict:
        """Получение статуса ордера по идентификатору.

        https://docs.chainstack.com/reference/hyperliquid-info-order-status
        """
        payload = {
            "type": "orderStatus",
            "user": user,
            "oid": oid,
        }

        return await self._post_request("/info", data=payload)

    async def l2_book(
        self,
        coin: str,
        n_sig_figs: Literal[2, 3, 4, 5] | None = None,
        mantissa: Literal[1, 2, 5] | None = None,
    ) -> list[list[dict]]:
        """Получение снапшота стакана уровня L2 для актива.

        https://docs.chainstack.com/reference/hyperliquid-info-l2-book
        """
        payload = {
            "type": "l2Book",
            "coin": coin,
            "nSigFigs": n_sig_figs,
            "mantissa": mantissa,
        }

        return await self._post_request("/info", data=payload)

    async def batch_clearinghouse_states(
        self, users: list[str], dex: str | None = None
    ) -> list[dict | None]:
        """Получение сводок фьючерсных аккаунтов группы пользователей.

        https://docs.chainstack.com/reference/hyperliquid-info-batch-clearinghouse-states
        """
        payload = {
            "type": "batchClearinghouseStates",
            "users": users,
            "dex": dex,
        }

        return await self._post_request("/info", data=payload)

    async def candle_snapshot(
        self,
        coin: str,
        interval: Literal[
            "1m",
            "3m",
            "5m",
            "15m",
            "30m",
            "1h",
            "2h",
            "4h",
            "8h",
            "12h",
            "1d",
            "3d",
            "1w",
            "1M",
        ],
        start_time: int,
        end_time: int,
    ) -> list[dict]:
        """Получение датасета свечей за указанный период.

        https://docs.chainstack.com/reference/hyperliquid-info-candle-snapshot
        """
        payload = {
            "type": "candleSnapshot",
            "req": {
                "coin": coin,
                "interval": interval,
                "startTime": start_time,
                "endTime": end_time,
            },
        }

        return await self._post_request("/info", data=payload)

    async def historical_orders(self, user: str) -> list[dict]:
        """Получение истории ордеров пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-historical-orders
        """
        payload = {
            "type": "historicalOrders",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def user_twap_slice_fills(self, user: str) -> list[dict]:
        """Получение последних TWAP-исполнений пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-user-twap-slice-fills
        """
        payload = {
            "type": "userTwapSliceFills",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def recent_trades(self, coin: str) -> list[dict]:
        """Получение последних публичных сделок по активу.

        https://docs.chainstack.com/reference/hyperliquid-info-recent-trades
        """
        payload = {
            "type": "recentTrades",
            "coin": coin,
        }

        return await self._post_request("/info", data=payload)

    async def vault_details(self, vault_address: str, user: str | None = None) -> dict:
        """Получение подробной информации о выбранном вулте.

        https://docs.chainstack.com/reference/hyperliquid-info-vault-details
        """
        payload = {
            "type": "vaultDetails",
            "vaultAddress": vault_address,
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def portfolio(self, user: str) -> list[list[Any]]:
        """Получение данных о производительности портфеля пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-portfolio
        """
        payload = {
            "type": "portfolio",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def referral(self, user: str) -> dict:
        """Получение реферальной информации пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-referral
        """
        payload = {
            "type": "referral",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def delegator_rewards(self, user: str) -> list[dict]:
        """Получение истории стейкинг-наград пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-delegator-rewards
        """
        payload = {
            "type": "delegatorRewards",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def meta_and_asset_contexts(self) -> list[Any]:
        """Получение метаданных и рыночных метрик по перпетуалам.

        https://docs.chainstack.com/reference/hyperliquid-info-meta-and-asset-ctxs
        """
        payload = {"type": "metaAndAssetCtxs"}

        return await self._post_request("/info", data=payload)

    async def user_funding(
        self, user: str, start_time: int, end_time: int | None = None
    ) -> list[Any]:
        """Получение истории фандинга пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-user-funding
        """
        payload = {
            "type": "userFunding",
            "user": user,
            "startTime": start_time,
            "endTime": end_time,
        }

        return await self._post_request("/info", data=payload)

    async def funding_history(
        self, coin: str, start_time: int, end_time: int | None = None
    ) -> list[dict]:
        """Получение истории ставок фандинга по активу.

        https://docs.chainstack.com/reference/hyperliquid-info-funding-history
        """
        payload = {
            "type": "fundingHistory",
            "coin": coin,
            "startTime": start_time,
            "endTime": end_time,
        }

        return await self._post_request("/info", data=payload)

    async def predicted_fundings(self) -> list[Any]:
        """Получение прогнозных ставок фандинга по всем перпетуалам.

        https://docs.chainstack.com/reference/hyperliquid-info-predicted-fundings
        """
        payload = {"type": "predictedFundings"}

        return await self._post_request("/info", data=payload)

    async def spot_meta_and_asset_contexts(self) -> list[Any]:
        """Получение метаданных и метрик для спотовых активов.

        https://docs.chainstack.com/reference/hyperliquid-info-spot-meta-and-asset-ctxs
        """
        payload = {"type": "spotMetaAndAssetCtxs"}

        return await self._post_request("/info", data=payload)

    async def gossip_root_ips(self) -> list[str]:
        """Получение списка узлов для P2P-госсипа.

        https://docs.chainstack.com/reference/hyperliquid-info-gossip-root-ips
        """
        payload = {"type": "gossipRootIps"}

        return await self._post_request("/info", data=payload)

    async def token_details(self, token_id: str) -> dict:
        """Получение подробной информации о токене.

        https://docs.chainstack.com/reference/hyperliquid-info-token-details
        """
        payload = {
            "type": "tokenDetails",
            "tokenId": token_id,
        }

        return await self._post_request("/info", data=payload)

    async def place_order(
        self,
        asset: str,
        is_buy: bool,
        size: str,
        reduce_only: bool,
        order_type: Literal["limit", "trigger"],
        order_body: dict,
        price: str | None = None,
        client_order_id: str | None = None,
        grouping: Literal["na", "normalTpsl", "positionTpsl"] = "na",
        builder_address: str | None = None,
        builder_fee: int | None = None,
        nonce: int | None = None,
        expires_after: int | None = None,
        vault_address: str | None = None,
    ) -> dict:
        """Выставление ордера на бирже.

        https://docs.chainstack.com/reference/hyperliquid-exchange-place-order
        """
        order_payload: dict[str, Any] = {
            "a": asset,
            "b": is_buy,
            "p": price,
            "s": size,
            "r": reduce_only,
            "t": {order_type: order_body},
        }
        if client_order_id is not None:
            order_payload["c"] = client_order_id

        return await self.batch_place_orders(
            [order_payload],
            grouping=grouping,
            builder_address=builder_address,
            builder_fee=builder_fee,
            nonce=nonce,
            expires_after=expires_after,
            vault_address=vault_address,
        )

    async def batch_place_orders(
        self,
        orders: list[dict[str, Any]],
        grouping: Literal["na", "normalTpsl", "positionTpsl"] = "na",
        builder_address: str | None = None,
        builder_fee: int | None = None,
        nonce: int | None = None,
        expires_after: int | None = None,
        vault_address: str | None = None,
    ) -> dict:
        """Пакетное выставление ордеров на бирже.

        https://docs.chainstack.com/reference/hyperliquid-exchange-place-order
        """
        if not orders:
            raise ValueError("orders must not be empty")
        if self._wallet is None:
            raise NotAuthorized("Private key is required for private endpoints.")
        if builder_address is not None and builder_fee is None:
            raise TypeError("builder_fee is required when builder_address is provided")
        if builder_address is None and builder_fee is not None:
            raise TypeError("builder_address is required when builder_fee is provided")

        required_keys = {"a", "b", "p", "s", "r", "t"}
        normalized_orders: list[dict[str, Any]] = []
        for order in orders:
            missing_keys = required_keys - order.keys()
            if missing_keys:
                missing = ", ".join(sorted(missing_keys))
                raise ValueError(f"order is missing required fields: {missing}")
            normalized = dict(order)
            normalized["p"] = str(normalized["p"])
            normalized["s"] = str(normalized["s"])
            if normalized.get("c") is None:
                normalized.pop("c", None)
            normalized_orders.append(normalized)

        action: dict[str, Any] = {
            "type": "order",
            "orders": normalized_orders,
            "grouping": grouping,
        }
        if builder_address is not None:
            action["builder"] = {"b": builder_address, "f": builder_fee}

        effective_vault = vault_address or self._vault_address
        action_nonce = nonce if nonce is not None else int(time.time() * 1000)
        signature = sign_l1_action(
            self._wallet,
            action,
            effective_vault,
            action_nonce,
            expires_after,
        )

        payload: dict[str, Any] = {
            "action": action,
            "nonce": action_nonce,
            "signature": signature,
        }
        if effective_vault is not None:
            payload["vaultAddress"] = effective_vault
        if expires_after is not None:
            payload["expiresAfter"] = expires_after

        return await self._post_request("/exchange", data=payload)
