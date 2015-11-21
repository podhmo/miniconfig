def _getTarget():
    from miniconfig import ConfiguratorCore
    return ConfiguratorCore


def test_with_queue():
    config = _getTarget()()

    def includeme(config):
        config.queue.append(object())

    assert len(config.queue) == 0
    config.include(includeme)
    assert len(config.queue) == 1

