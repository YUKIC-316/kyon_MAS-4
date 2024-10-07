import mesa
from kyon.random_walk import RandomWalker


class Kyon(RandomWalker):
    """
    キョンエージェントの動きと生死に関するロジックを含むクラス。
    植生の密度、食物資源エリア、罠などの要素に基づいた移動と行動を行う。
    """
    def __init__(self, unique_id, pos, model, moore=True, energy=None, birth_probability=0.1, death_probability=0.1):
        super().__init__(unique_id, pos, model, moore=moore)
        self.energy = energy
        self.is_trapped = False  # 罠にかかっているかどうかのフラグ
        self.birth_probability = birth_probability  # 出産後の死亡確率
        self.death_probability = death_probability  # 自然死の確率
        self.after_birth = 0  # 出産後の時間

    def step(self):
        # 現在の位置の植生パッチを取得
        this_cell = self.model.grid.get_cell_list_contents([self.pos])
        grass_patch = [obj for obj in this_cell if isinstance(obj, GrassPatch)][0]

        # 出産後の時間を増加
        self.after_birth += 1

        # 食物資源エリアとの距離を計算
        distance_to_food = self.model.get_distance_to_food(self.pos)

        # 移動ロジック（食物資源エリアに基づく）
        if distance_to_food <= 5:
            # 5マス以内の場合、80%の確率で食物資源エリアに向かう
            move_towards_food = self.random.random() < 0.8
        else:
            # 5マスより離れている場合、20%の確率で食物資源エリアに向かう
            move_towards_food = self.random.random() < 0.2

        if move_towards_food:
            self.move_towards(self.model.food_location)
        else:
            # 植生密度に基づく移動速度の調整
            if grass_patch.density == "dense":
                if self.random.random() < 0.5:  # 濃い植生では50%の確率で移動
                    self.random_move()
            elif grass_patch.density == "medium":
                if self.random.random() < 0.75:  # 中密度植生では75%の確率で移動
                    self.random_move()
            else:
                self.random_move()  # 薄い植生では通常通り移動

        # 罠にかかった場合の処理
        traps_in_cell = [obj for obj in this_cell if isinstance(obj, Trap)]
        if traps_in_cell:
            trap = traps_in_cell[0]
            # 食物資源エリアにいるかどうかを確認
            in_food_area = self.model.is_in_food_area(self.pos)
            capture_probability = trap.get_capture_probability(grass_patch.density, in_food_area=in_food_area)
            if self.random.random() < capture_probability:
                self.is_trapped = True
                self.model.grid.remove_agent(self)
                self.model.schedule.remove(self)
                return  # キョンが罠にかかって死んだ場合、ここで終了

        # 自然死の処理（一定の確率で死亡）
        if self.random.random() < self.death_probability:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
            return  # 自然死の場合、ここで終了

        # 出産後に一定の確率で死亡
        if self.random.random() < self.birth_probability:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
            return  # 出産後に死亡した場合、ここで終了


class GrassPatch(mesa.Agent):
    """
    植生パッチエージェント。各パッチは成長し、キョンが食べることができる。
    """
    def __init__(self, unique_id, model, fully_grown, countdown, density):
        super().__init__(unique_id, model)
        self.fully_grown = fully_grown  # 草が完全に成長しているかどうか
        self.countdown = countdown  # 草の成長にかかる時間
        self.density = density  # 植生の密度（濃い、普通、薄い）

    def step(self):
        # 草が完全に成長していない場合、カウントダウンを減少
        if not self.fully_grown:
            if self.countdown <= 0:
                self.fully_grown = True
                self.countdown = self.model.grass_regrowth_time  # 成長時間をリセット
            else:
                self.countdown -= 1


class Trap(mesa.Agent):
    """
    罠エージェント。キョンを捕まえるための罠。
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def get_capture_probability(self, vegetation_density, in_food_area=False):
        """
        罠にかかる確率を植生密度と食物資源エリアの情報を基に計算する。
        """
        base_probability = {
            "dense": 0.3,
            "medium": 0.5,
            "sparse": 0.7
        }

        if in_food_area:
            # 食物資源エリアにいる場合は捕獲確率が高くなる
            return base_probability[vegetation_density] + 0.1
        return base_probability[vegetation_density]
