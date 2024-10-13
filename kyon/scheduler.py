from typing import Type, Callable

import mesa


class RandomActivationByTypeFiltered(mesa.time.RandomActivationByType):
    """
    エージェントをカウントする前に、関数によってフィルタリングを行う機能を追加した
    get_type_countメソッドをオーバーライドするスケジューラ。

    例:
    >>> scheduler = RandomActivationByTypeFiltered(model)
    >>> scheduler.get_type_count(AgentA, lambda agent: agent.some_attribute > 10)
    """

    def get_type_count(
        self,
        type_class: Type[mesa.Agent],
        filter_func: Callable[[mesa.Agent], bool] = None,
    ) -> int:
        """
        キュー内の指定されたタイプのエージェントのうち、フィルタ関数を満たすエージェントの
        現在の数を返します。
        """
        count = 0
        for agent in self.agents_by_type[type_class].values():
            if filter_func is None or filter_func(agent):
                count += 1
        return count
