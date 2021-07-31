from typing import Dict, Type, Callable
from mocobot.framework.module import Module
from mocobot.framework.runtime import Runtime
import unittest
import asyncio


class Root(Module):

    def __init__(self):
        super().__init__({}, Root, "root")

    def pre_run(self) -> None:
        pass

    async def on_run(self) -> None:
        pass

    @property
    def events(self) -> Dict[Type, Callable]:
        return {}

    async def on_stop(self) -> None:
        pass

    def post_run(self) -> None:
        pass


class Leaf(Module):

    def __init__(self, name: str, number: int):
        super().__init__({}, Leaf, name)
        self.number = number

    def pre_run(self) -> None:
        pass

    async def on_run(self) -> None:
        while self.is_running:
            await asyncio.sleep(2)
            self.log("running")

    @property
    def events(self) -> Dict[Type, Callable]:
        return {}

    async def on_stop(self) -> None:
        pass

    def post_run(self) -> None:
        pass


class Corrupt(Module):

    def pre_run(self) -> None:
        pass

    async def on_run(self) -> None:
        await asyncio.sleep(3)
        raise Exception()

    @property
    def events(self) -> Dict[Type, Callable]:
        return {}

    async def on_stop(self) -> None:
        pass

    def post_run(self) -> None:
        pass


class TestModule(unittest.TestCase):

    def test_get(self):

        root = Root()
        leaf1 = Leaf("first", 10)
        leaf2 = Leaf("second", 20)

        root.add_submodule(leaf1)
        root.add_submodule(leaf2)

        all_leaves = root.get_submodule(Leaf)
        self.assertEqual(len(all_leaves), 2)

        first_leaf = root.get_submodule(Leaf, name="first", number=10)
        first_leaf_by_str = root.get_submodule(Leaf, name="first")
        first_leaf_by_num = root.get_submodule(Leaf, number=10)

        self.assertEqual(len(first_leaf), 1)
        self.assertEqual(len(first_leaf_by_str), 1)
        self.assertEqual(len(first_leaf_by_num), 1)

        self.assertIs(first_leaf[0], first_leaf_by_num[0])
        self.assertIs(first_leaf_by_str[0], first_leaf_by_num[0])

        self.assertEqual(first_leaf[0].name, "first")
        self.assertEqual(first_leaf[0].number, 10)

        leaf3 = Leaf("third", 10)
        root.add_submodule(leaf3)

        two_leaves = root.get_submodule(Leaf, number=10)
        self.assertEqual(len(two_leaves), 2)
        self.assertEqual(two_leaves[0].name, "first")
        self.assertEqual(two_leaves[1].name, "third")

    def test_errors(self):

        async def run():

            root = Root().init()
            leaf1 = Leaf("first", 10).init()
            corrupt = Corrupt({}, Corrupt, "corrupt").init()

            root.add_submodule(leaf1)
            root.add_submodule(corrupt)

            await Runtime().run(root)

        asyncio.run(run())


