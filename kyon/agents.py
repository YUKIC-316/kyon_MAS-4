import mesa
from kyon.random_walk import RandomWalker

class Kyon(RandomWalker):
    """
    草原を歩き回り、繁殖し（無性繁殖）、捕食されるキョン。
    初期化メソッドはRandomWalkerと同じです。
    """
    
    after_birth = 0
    steps_in_food_area = 0  # 食物資源エリア内にいるターン数をカウント

    def __init__(self, unique_id, pos, model, moore,  kyon_reproduce_count=False, after_birth=0):
        super().__init__(unique_id, pos, model, moore=moore)
        self.kyon_reproduce_count = kyon_reproduce_count
        self.after_birth = after_birth
        self.in_food_area = False  # 食物資源エリアにいるかどうかのフラグを初期化
        self.steps_in_food_area = 0  # 食物資源エリア内にいるターン数を初期化



    def step(self):
        """
        モデルのステップ。植生の密度に応じて移動し、食物資源エリアにも対応する
        """
        self.kyon_reproduce_count = False
        self.after_birth += 1        
        
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
        if self.after_birth < 2190:
            if self.random.random() < (1 / 2500) * (self.after_birth / 2190):  # 若いキョンのリスクを少し上げる
                self.model.grid.remove_agent(self)
                self.model.schedule.remove(self)
                return  # 死亡した場合は以降の処理を行わない
        else:
            if self.random.random() < (1 / 800) * ((self.after_birth / 2190) ** 2):  # 6歳以降のリスクを高める
                self.model.grid.remove_agent(self)
                self.model.schedule.remove(self)
                return  # 死亡した場合は以降の処理を行わない    


        # 繁殖
        if self.after_birth >= 150 and self.random.random() < (1/2) * (1/210):
            # 新しい羊(=lamb)を生成します            
            lamb = Kyon(
                self.model.next_id(), self.pos, self.model, self.moore, self.kyon_reproduce_count, 0
            )
            self.model.grid.place_agent(lamb, self.pos)
            self.model.schedule.add(lamb)
            self.kyon_reproduce_count = True


    def move_with_trap_check(self, move_steps):
        """
        指定されたマス数だけ移動し、その途中で罠に入ったかをチェックする
        """
        current_position = self.pos
        for step in range(move_steps):
            # 現在の位置からランダムに次のマスへ移動
            next_position = self.random_move_step()

            # 現在のマスと次のマスの罠を確認
            self.check_trap_in_position(current_position)

            # 次のマスに移動（間のマスも含む）
            current_position = next_position
            
            # 最後に移動したマスで罠を確認
            if step == move_steps - 1:
                self.check_trap_in_position(current_position)

        # 最後の移動先に移動
        self.model.grid.move_agent(self, current_position)

    def random_move_step(self):
        """
        キョンが1ステップだけランダムに移動するための関数
        """
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        return self.random.choice(possible_steps)

    def check_trap_in_position(self, position):
        """
        指定されたマスに罠があるかどうかをチェックし、罠があれば捕獲を処理する
        """
        current_cell = self.model.grid.get_cell_list_contents([position])
        trap_in_cell = [obj for obj in current_cell if isinstance(obj, Trap)]

        if trap_in_cell:
            for trap in trap_in_cell:
                if trap.recovery_timer == 0:  # 罠が稼働中であるかどうかを確認
                    success_rate = trap.calculate_trap_success_rate(position)
                    if self.random.random() < success_rate:
                        self.model.grid.remove_agent(self)
                        self.model.schedule.remove(self)
                        trap.is_hunt = True
                        trap.recovery_timer = trap.trap_recovery_turns  # 罠の再稼働までの時間をセット
                        return
        

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

    def calculate_trap_success_rate(self, position):
        """
        現在のセルに応じた罠の捕獲成功率を計算する。
        """
        current_cell = self.model.grid.get_cell_list_contents([position])
        vegetation_density = [obj for obj in current_cell if isinstance(obj, VegetationDensity)][0]

        if vegetation_density.density == "dense":
            trap_success_rate = self.model.base_success_rate * self.model.dense_vegetation_modifier
        elif vegetation_density.density == "normal":
            trap_success_rate = self.model.base_success_rate * self.model.normal_vegetation_modifier
        else:
            trap_success_rate = self.model.base_success_rate * self.model.sparse_vegetation_modifier

        # 食物資源エリアにいる場合、捕獲成功率をさらに強化
        in_food_area = any(isinstance(obj, FoodResourceArea) for obj in current_cell)
        if in_food_area:
            if vegetation_density.density == "dense":
                trap_success_rate *= 3  # 濃いエリアでは捕獲成功率が3倍
            else:
                trap_success_rate *= 4  # 普通・薄いエリアでは捕獲成功率が4倍

        return trap_success_rate


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