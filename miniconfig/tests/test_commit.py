# -*- coding:utf-8 -*-
def _getTarget():
    from miniconfig import ConfiguratorCore

    return ConfiguratorCore


def test_order__no_order_option():
    config = _getTarget()()
    L = []

    def one():
        L.append(1)

    def two():
        L.append(2)

    def three():
        L.append(3)

    config.action("o", one)
    config.action("tw", two)
    config.action("th", three)

    config.commit()

    assert L == [1, 2, 3]


def test_order__with_order_option():
    from miniconfig import (
        PHASE1_CONFIG,
        PHASE2_CONFIG,
    )

    config = _getTarget()()
    L = []

    def one():
        L.append(1)

    def two():
        L.append(2)

    def three():
        L.append(3)

    config.action("o", one)
    config.action("tw", two, order=PHASE2_CONFIG)
    config.action("th", three, order=PHASE1_CONFIG)

    config.commit()

    assert L == [3, 2, 1]
