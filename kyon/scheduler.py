from typing import Type, Callable
import mesa


class RandomActivationByTypeFiltered(mesa.time.RandomActivationByType):
    """
    エージェントのタイプに基づいてスケジュールするクラス。
    get_type_countメソッドをオーバーライドして、エージェントのフィルタリングを行い、
    特定の条件を満たすエージェントのみをカウントすることができるようにしています。
    """

    def get_type_count(self, type_class: Type[mesa.Agent], filter_func: Callable[[mesa.Agent], bool] = None) -> int:
        """
        指定されたタイプのエージェント数を返します。
        フィルタリング関数を指定することで、その関数がTrueを返すエージェントのみをカウントします。

        Args:
            type_class: カウントするエージェントのタイプ（例: SheepやWolfなど）
            filter_func: フィルタリングの条件（Trueを返す条件に合うエージェントのみカウント）
        Returns:
            フィルタされたエージェントの数
        """
        count = 0
        for agent in self.agents_by_type[type_class].values():
            # フィルタ関数が指定されていない場合、または条件を満たす場合にカウント
            if filter_func is None or filter_func(agent):
                count += 1
        return count
