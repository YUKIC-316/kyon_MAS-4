import mesa
from kyon.random_walk import RandomWalker

class Kyon(RandomWalker):
    """
    草原を歩き回り、繁殖し（無性繁殖）、捕食されるキョン。
    初期化メソッドはRandomWalkerと同じです。
    """
    
    #energy = None
    after_birth = 0
    steps_in_food_area = 0  # 食物資源エリア内にいるターン数をカウント

    def __init__(self, unique_id, pos, model, moore,  kyon_reproduce_count=False, after_birth=0):
        super().__init__(unique_id, pos, model, moore=moore)
        self.kyon_reproduce_count = kyon_reproduce_count
        self.after_birth = after_birth
        self.in_food_area = False  # 食物資源エリアにいるかどうかのフラグを初期化
        self.steps_in_food_area = 0  # 食物資源エリア内にいるターン数を初期化
        #self.is_eat = False


    def step(self):
        """
        モデルのステップ。植生の密度に応じて移動し、食物資源エリアにも対応する
        """
        self.kyon_reproduce_count = False
        self.after_birth += 1
        #self.is_eat = False
        
        # 現在のセル情報を取得
        current_cell = self.model.grid.get_cell_list_contents([self.pos])
        
        # 植生の密度に基づいて移動マス数を決定する
        vegetation_density = [obj for obj in current_cell if isinstance(obj, VegetationDensity)][0]
        
        if vegetation_density.density == "dense":  # 濃い植生
            move_steps = 1
        elif vegetation_density.density == "normal":  # 普通の植生
            move_steps = 2
        else:  # 薄い植生
            move_steps = 3

        # キョンが食物資源エリア内にいるかを確認
        in_food_area = any(isinstance(obj, FoodResourceArea) for obj in current_cell)

        # 食物資源エリア内にいる場合の動き
        if in_food_area:
            self.steps_in_food_area += 1
            # 5ターン滞在したらランダムに外に出る
            if self.steps_in_food_area < 5:
                self.random_move(move_steps=1)
            else:
                self.steps_in_food_area = 0
                self.random_move(move_steps=move_steps)

        else:
            # 食物資源エリア外にいる場合
            self.steps_in_food_area = 0

            # 食物資源エリアに向かうかランダムに移動するかを決定
            nearest_food_area = self.find_nearest_food_area()
            if nearest_food_area:
                distance_to_food_area = self.model.grid.get_distance(self.pos, nearest_food_area.pos)
                
                if distance_to_food_area <= 5:
                    # 5マス以内にいる場合、80%の確率で食物資源エリアに向かう
                    if self.random.random() < 0.8:
                        self.move_towards(nearest_food_area.pos)
                    else:
                        self.random_move(move_steps=move_steps)
                else:
                    # 5マスより離れている場合、20%の確率で食物資源エリアに向かう
                    if self.random.random() < 0.2:
                        self.move_towards(nearest_food_area.pos)
                    else:
                        self.random_move(move_steps=move_steps)
            else:
                # 食物資源エリアが見つからない場合はランダムに移動
                self.random_move(move_steps=move_steps)


        # ランダムに指定されたマス数だけ移動
        #self.random_move(move_steps=move_steps)

        
#        # 死亡（年齢が高くなるほど死亡率があがる）
#        living = True
#        if self.random.random() < (1 / 2190) * (self.after_birth / 2190):
#            self.model.grid.remove_agent(self)
#            self.model.schedule.remove(self)
#            living = False

        # 死亡（年齢が高くなるほど死亡率が急激に上がる）
        living = True
        if self.after_birth < 2190:
            if self.random.random() < (1 / 2500) * (self.after_birth / 2190):  # 若いキョンのリスクを少し上げる
                self.model.grid.remove_agent(self)
                self.model.schedule.remove(self)
                living = False
        else:
            if self.random.random() < (1 / 800) * ((self.after_birth / 2190) ** 2):  # 6歳以降のリスクを高める
                self.model.grid.remove_agent(self)
                self.model.schedule.remove(self)
                living = False


        # 繁殖
        if living and self.after_birth >= 150 and self.random.random() < (1/2) * (1/210):
            # 新しい羊(=lamb)を生成します
            #if self.model.grass:
                #self.energy /= 2
            lamb = Kyon(
                self.model.next_id(), self.pos, self.model, self.moore, self.kyon_reproduce_count, 0
            )
            self.model.grid.place_agent(lamb, self.pos)
            self.model.schedule.add(lamb)
            self.kyon_reproduce_count = True
        

    def find_nearest_food_area(self):
        """
        最も近い食物資源エリアを見つけ、その位置を返す
        """
        min_distance = float("inf")
        nearest_food_area = None

        # 全ての食物資源エリアを検索
        for food_area in [agent for agent in self.model.schedule.agents if isinstance(agent, FoodResourceArea)]:
            distance = self.model.grid.get_distance(self.pos, food_area.pos)
            if distance < min_distance:
                min_distance = distance
                nearest_food_area = food_area

        return nearest_food_area

    

class Trap(mesa.Agent):
    """
    トラップエージェント（罠）。植生の密度に応じて捕獲確率が異なる。
    """


    def __init__(self, unique_id, pos, model, is_hunt=False, trap_recovery_turns=0):
        super().__init__(unique_id, model)  
        self.is_hunt = is_hunt  # 捕獲の成功を示すフラグ
        self.trap_recovery_turns = trap_recovery_turns  # 罠の回復までのターン数
        self.recovery_timer = 0  # 再稼働までの残りターン数

    def step(self):
        """
        罠は固定されている。キョンが同じセルに入った場合に捕獲を判定する。
        """
        # 捕獲後の回復タイマーが進行中なら、カウントダウンする
        if self.recovery_timer > 0:
            self.recovery_timer -= 1

        # 回復タイマーが0ならば罠が稼働状態に戻る
        if self.recovery_timer == 0:
            
            self.is_hunt = False  # 捕獲フラグを初期化

            # 現在のセルにいるキョンを探す
            this_cell = self.model.grid.get_cell_list_contents([self.pos])
            kyon_in_cell = [obj for obj in this_cell if isinstance(obj, Kyon)]

            if kyon_in_cell:
                # 現在のセルの植生密度を取得
                vegetation_density = [obj for obj in this_cell if isinstance(obj, VegetationDensity)][0]

                # 植生密度に応じて捕獲確率を設定
                if vegetation_density.density == "dense":
                    trap_success_rate = self.model.base_success_rate * self.model.dense_vegetation_modifier
                elif vegetation_density.density == "normal":
                    trap_success_rate = self.model.base_success_rate * self.model.normal_vegetation_modifier
                else:
                    trap_success_rate = self.model.base_success_rate * self.model.sparse_vegetation_modifier

                # セルが食物資源エリアに含まれているかを確認
                in_food_area = any(isinstance(obj, FoodResourceArea) for obj in this_cell)

                # 食物資源エリアにいる場合、捕獲成功率をさらに強化
                if in_food_area:
                    if vegetation_density.density == "dense":
                        trap_success_rate *= 3  # 濃いエリアでは捕獲成功率が3倍
                    else:
                        trap_success_rate *= 4  # 普通・薄いエリアでは捕獲成功率が4倍

                # 捕獲確率に基づいて捕獲判定
                if self.random.random() < trap_success_rate:
                    self.is_hunt = True  # 捕獲に成功
                    for kyon in kyon_in_cell:
                        self.model.grid.remove_agent(kyon)  # キョンを捕獲して取り除く
                        self.model.schedule.remove(kyon)
                    
                    # 捕獲後に罠を回復状態にセット
                    self.recovery_timer = self.trap_recovery_turns
                    
        # 死亡または繁殖
        # if self.energy <= 0:
        #     self.model.grid.remove_agent(self)
        #     self.model.schedule.remove(self)
        # else:
        #     if self.random.random() < self.model.wolf_reproduce:
            # 新しい狼を生成
            #self.energy /= 2
            #cub = Wolf(
            #    self.model.next_id(), self.pos, self.model, self.moore, self.energy
          #  )
          #  self.model.grid.place_agent(cub, cub.pos)
           # self.model.schedule.add(cub)


class VegetationDensity(mesa.Agent):
    """
    各セルに植生密度を設定するためのエージェント。密度は "dense"（濃い）、"normal"（普通）、"sparse"（薄い）のいずれか。
    """

    def __init__(self, unique_id, pos, model, density):
        """
        VegetationDensity の初期化。密度を設定します。
        """
        super().__init__(unique_id, model)
        self.pos = pos
        self.density = density  # "dense"、"normal"、"sparse" のいずれか

    def step(self):
        """
        VegetationDensity 自体は固定されているため、特に何もしません。
        """
        pass

class FoodResourceArea(mesa.Agent):
    """
    フィールド上の食物資源エリアを表します。
    エリア内ではキョンの動きに影響を与え、罠の成功率も上昇します。
    """
    
    def __init__(self, unique_id, pos, model):
        """
        食物資源エリアの初期化。
        """
        super().__init__(unique_id, model)
        self.pos = pos

    def step(self):
        """
        食物資源エリア自体は固定されているため、特に何もしません。
        ただし、キョンや罠の動作に影響を与える役割を持ちます。
        """
        pass