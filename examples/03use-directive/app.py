from miniconfig import Configurator as _Configurator


q = []


class Configurator(_Configurator):
    pass


def includeme(c: Configurator) -> None:
    def add_task(c: Configurator, task: str) -> None:
        def register():
            q.append(task)

        discriminator = (add_task.__name__, object())
        c.action(discriminator, register)

    c.add_directive("add_task", add_task)


def include_xxx(c: Configurator):
    for i in range(3):
        c.add_task(f"x{i}")


def include_yyy(c: Configurator):
    for i in range(3):
        c.add_task(f"y{i}")


def include_zzz(c: Configurator):
    for i in range(3):
        c.add_task(f"z{i}")


c = Configurator()

c.include(includeme)
c.include(include_xxx)
c.include(include_zzz)

print(f"before commit q={q}")
c.commit()
print(f"after commit q={q}")
