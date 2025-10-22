from decimal import Decimal


def test_decimal_exponent_behavior() -> None:
    """Тестирует, как работает извлечение количества знаков после запятой через Decimal()."""
    steps = [
        1,
        10,
        0.1,
        0.01,
        0.001,
        0.0001,
        0.00001,
        5,
        0.5,
        0.05,
        0.005,
        2.5,
        0.25,
        0.125,
        0.00025,
        1000,
        0.0000001,
        0.00000001,
        0.000000001,
        0.0000000001,
        # 1e-1,
        # 1e-2,
        # 1e-3,
        # 1e-4,
        # 1e-5,
        # 1e-6,
        # 1e-7,
        # 1e-8,
        # 1e-9,
        # 1e-10,
    ]

    for step in steps:
        d = Decimal(str(step))
        digits = abs(d.as_tuple().exponent)  # type: ignore
        print(f"step={step:<15} exponent={d.as_tuple().exponent:<4} digits={digits}")


if __name__ == "__main__":
    test_decimal_exponent_behavior()
