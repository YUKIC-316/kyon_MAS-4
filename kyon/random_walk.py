import mesa

class RandomWalker(mesa.Agent):
    """
    ランダムな移動を行うエージェントの基底クラス。
    このクラス自体は直接使用されず、他のエージェント（キョンなど）が継承することを想定している。
    """
    
    grid = None
    x = None
    y = None
    moore = True

    def __init__(self, unique_id, pos, model, moore=True):
        """
        Args:
            unique_id: エージェントの一意のID。
            pos: エージェントの位置（x, y）。
            model: メサモデルのインスタンス。
            moore: エージェントが8方向に移動できるかどうか。Trueなら8方向、Falseなら上下左右の4方向に限定。
        """
        super().__init__(unique_id, model)
        self.pos = pos
        self.moore = moore

    def random_move(self):
        """
        エージェントがランダムに隣接セルへ移動する。
        """
        # 隣接セルから次に移動するセルを選択
        next_moves = self.model.grid.get_neighborhood(self.pos, self.moore, True)
        next_move = self.random.choice(next_moves)
        
        # 移動を実行
        self.model.grid.move_agent(self, next_move)

    def move_towards(self, target_pos):
        """
        エージェントが指定された位置に向かって移動する。
        """
        # 現在位置とターゲットの位置から次に移動するべき位置を計算
        x, y = self.pos
        target_x, target_y = target_pos
        new_x = x + (1 if target_x > x else -1 if target_x < x else 0)
        new_y = y + (1 if target_y > y else -1 if target_y < y else 0)
        
        # ターゲットの方向へ移動
        self.model.grid.move_agent(self, (new_x, new_y))
