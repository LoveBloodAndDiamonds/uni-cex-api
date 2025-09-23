def compare_2_classes(sync_cls: type, async_cls: type) -> dict:
    """
    compare the signature of 2 class definition ignoring private methods
    check that async_cls has a method with the same name of sync_cls but returning a coroutine
    returns the difference between the 2 classes as a dict
    """
    import inspect

    sync_methods = {
        m
        for m in dir(sync_cls)
        if not m.startswith("_") and inspect.isfunction(getattr(sync_cls, m))
    }
    async_methods = {
        m
        for m in dir(async_cls)
        # if not m.startswith("_") and inspect.iscoroutinefunction(getattr(async_cls, m))
        if not m.startswith("_") and inspect.isfunction(getattr(sync_cls, m))
    }
    common = sync_methods.intersection(async_methods)
    missing_from_sync = async_methods - sync_methods
    missing_from_async = sync_methods - async_methods
    issues = {}
    if len(missing_from_sync):
        issues["missing_from_sync"] = missing_from_sync
    if len(missing_from_async):
        issues["missing_from_async"] = missing_from_async

    # Compare each function signature types
    # for method in common:
    #     sync_sig = inspect.signature(getattr(sync_cls, method))
    #     async_sig = inspect.signature(getattr(async_cls, method))
    #     if sync_sig != async_sig:
    #         issues[method] = {}
    #         issues[method]["issues"] = []
    #         for param_sync, param_async in zip(
    #             sync_sig.parameters.items(), async_sig.parameters.items(), strict=True
    #         ):
    #             if param_sync != param_async:
    #                 key_sync, params_sync = param_sync
    #                 key_async, params_async = param_async

    #                 issues[method]["issues"].append(
    #                     f"param {key_sync} | {key_async} {params_sync} != {params_async}"
    #                 )

    #         issues[method]["sync_sig"] = str(sync_sig)
    #         issues[method]["async_sig"] = str(async_sig)

    return issues


def main() -> None:
    """Main entry point for the application."""

    from unicex.binance.asyncio import WebsocketManager as AsyncWebsocketManager
    from unicex.binance import WebsocketManager

    result = compare_2_classes(WebsocketManager, AsyncWebsocketManager)

    from pprint import pp

    pp(result)


if __name__ == "__main__":
    main()
