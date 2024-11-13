import mesa
from kyon.random_walk import RandomWalker

class Kyon(RandomWalker):
    """
    草原を歩き回り、繁殖し（無性繁殖）、捕食されるキョン。
    初期化メソッドはRandomWalkerと同じです。
    """
    
    def __init__(self, unique_id, pos, model, moore, kyon_reproduce_count=False, after_birth=0):
        super().__init__(unique_id, pos, model, moore=moore)
        self.kyon_reproduce_count = kyon_reproduce_count  # 繁殖フラグの初期化
        self.after_birth = after_birth
        self.steps_in_day = 8  # 1日8ステップ
        self.steps_to_next_move = 1  # 初期移動ステップ数        
        self.avoiding_beast_path = False  # 獣道を避けるフラグ
        self.avoid_beast_path_steps = 0   # 獣道を避ける期間のカウント
        self.avoiding_food_area = False  # 食物資源エリアを避けるフラグ
        self.avoid_food_area_steps = 0   # 食物資源エリアを避けるカウント
        self.visit_history = []  # 過去に訪れたセルの履歴リスト


    def update_steps_to_next_move(self):
        """
        植生密度に応じて次の移動までのステップ数を更新
        """
#        current_cell = self.model.grid.get_cell_list_contents([self.pos])
#        vegetation_density = [obj for obj in current_cell if isinstance(obj, VegetationDensity)][0]
#        if vegetation_density.density == "dense":
#            self.steps_to_next_move = 3  # 濃い植生エリアでは3ステップで1マス移動
#        elif vegetation_density.density == "normal":
#            self.steps_to_next_move = 2  # 普通の植生エリアでは2ステップで1マス移動
#        else:
#            self.steps_to_next_move = 1  # 薄い植生エリアでは1ステップで1マス移動

        self.steps_to_next_move = 1

    def step(self):
        """
        キョンの1ステップ。移動、罠のチェック、獣道と食物資源エリアの確認、繁殖、死亡を行う。
        """

        
        self.kyon_reproduce_count = False  # ステップごとに繁殖フラグをリセット

        # 移動処理
        self.steps_to_next_move -= 1
        if self.steps_to_next_move <= 0:
            self.random_move()
            self.update_steps_to_next_move()  # 次の移動までのステップ数を更新

        # 1日（8ステップ）ごとに年齢、自然死、繁殖判定を行う
        if self.model.current_step % self.steps_in_day == 0:
            self.after_birth += 1  # 1日経過


        # 獣道を避けている期間かどうかを確認
        if self.avoiding_beast_path:
            self.random_move()
            self.avoid_beast_path_steps += 1
            if self.avoid_beast_path_steps >= self.steps_in_day * 2:  # 2日分（16ステップに相当）
                self.avoiding_beast_path = False
                self.avoid_beast_path_steps = 0
            return  # 他の処理は行わない

        # 近くに獣道がある場合、引き寄せられるかチェック
        nearest_beast_path = self.find_nearest_beast_path()
        if nearest_beast_path and self.model.get_distance(self.pos, nearest_beast_path.pos) <= 10:
            if not self.avoiding_beast_path and self.random.random() < 0.8:  # 80%の確率で獣道に向かう
                self.move_towards(nearest_beast_path.pos)
                return


        # 獣道エリア内にいるかを確認
        current_cell = self.model.grid.get_cell_list_contents([self.pos])
        in_beast_path = any(isinstance(obj, BeastPath) for obj in current_cell)
        if in_beast_path:
            self.avoiding_beast_path = True
            self.random_move()
            return


        # 食物資源エリアを避けている期間かどうかを確認
        if self.avoiding_food_area:
            self.random_move()  # 食物資源エリアから離れるためにランダムに移動
            self.avoid_food_area_steps += 1
            if self.avoid_food_area_steps >= self.steps_in_day * 2:  # 2日分（16ステップに相当）避けたらリセット
                self.avoiding_food_area = False
                self.avoid_food_area_steps = 0
            return  # 他の処理は行わない

        # キョンが食物資源エリア内にいるかを確認
        in_food_area = any(isinstance(obj, FoodResourceArea) for obj in current_cell)
        if in_food_area:
            self.avoiding_food_area = True
            self.random_move()
            return


        # 近くに食物エリアがある場合の動き
        nearest_food_area = self.find_nearest_food_area()
        if nearest_food_area and self.model.get_distance(self.pos, nearest_food_area.pos) <= 7:
            if not self.avoiding_food_area and self.random.random() < 0.6:  # 60%の確率で食物資源エリアに向かう
                self.move_towards(nearest_food_area.pos)
                return


        # 一度訪れたエリアを避けるための処理（過去8ステップ分のみ保持）
        self.visit_history.append(self.pos)
        if len(self.visit_history) > self.steps_in_day*2:  # 2日分（16ステップ）だけ保持
            self.visit_history.pop(0)  # 履歴は過去8ステップ分のみ保持


        # 過去に訪れたセルを除外してランダム移動
        next_moves = [move for move in self.model.grid.get_neighborhood(self.pos, self.moore, include_center=False)
                      if move not in self.visit_history]
        if next_moves:
            next_move = self.random.choice(next_moves)
            self.model.grid.move_agent(self, next_move)
        else:
            # 全ての隣接セルが履歴に含まれる場合は通常のランダム移動
            self.random_move()



        # 年齢に基づく死亡率の計算
        if self.after_birth < 1825:  # 5歳未満
            death_probability = 0.001
        elif self.after_birth < 2555:  # 5歳から7歳
            death_probability = ((self.after_birth ) / 1825) * 0.05
        else:  # 7歳以上
            death_probability = 1.0

        # ランダムに基づく死亡判定
        if self.random.random() < death_probability:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
            self.model.step_dead_kyons += 1
            return  # 死亡した場合は以降の処理を行わない


        # 出産処理
        if 180 <= self.after_birth :  # 出産可能な年齢範囲
            
            # ランダムに基づく出産判定
            #if self.random.random() < (1/2) * (1/210): 
            if self.random.random() < 0.015: 
                lamb = Kyon(
                    self.model.next_id(), self.pos, self.model, self.moore, kyon_reproduce_count=True, after_birth=0
                )
                self.model.grid.place_agent(lamb, self.pos)
                self.model.schedule.add(lamb)
                self.model.step_born_kyons += 1
                self.kyon_reproduce_count = True



    def find_nearest_food_area(self):
        """
        最も近い食物資源エリアを見つけ、その位置を返す。
        """
        min_distance = float("inf")
        nearest_food_area = None
        for food_area in [agent for agent in self.model.schedule.agents if isinstance(agent, FoodResourceArea)]:
            distance = self.model.get_distance(self.pos, food_area.pos)
            if distance < min_distance:
                min_distance = distance
                nearest_food_area = food_area
        return nearest_food_area
  
    def find_nearest_beast_path(self):
        """
        最も近い獣道を見つけ、その位置を返す。
        """
        min_distance = float("inf")
        nearest_path = None
        for path in [agent for agent in self.model.schedule.agents if isinstance(agent, BeastPath)]:
            distance = self.model.get_distance(self.pos, path.pos)
            if distance < min_distance:
                min_distance = distance
                nearest_path = path
        return nearest_path      

    

class BeastPath(mesa.Agent):
    """
    フィールド上の獣道を表すエージェント。キョンは獣道に引き寄せられる。
    """
    def __init__(self, unique_id, pos, model):
        super().__init__(unique_id, model)
        self.pos = pos

    def step(self):
        pass


class Trap(mesa.Agent):
    """
    トラップエージェント（罠）。植生の密度に応じて捕獲確率が異なる。
    """
#    def __init__(self, unique_id, pos, model, is_hunt=False, active_days_per_week=3):
#        super().__init__(unique_id, model)
#        self.is_hunt = False
#        self.steps_per_day = 8  # 1日8ステップ
#        self.steps_per_week = self.steps_per_day * 7  # 1週間で56ステップ
#        self.active_steps = self.set_active_steps(active_days_per_week)  # 稼働するステップを設定
#        self.current_step = 0

    def __init__(self, unique_id, pos, model, is_hunt=False, active_days_per_week=5, inactive_steps_after_capture=16):
        super().__init__(unique_id, model)
        self.is_hunt = False
        self.steps_per_day = 8  # 1日8ステップ
        self.steps_per_week = self.steps_per_day * 7  # 1週間で56ステップ
        self.inactive_steps_after_capture = inactive_steps_after_capture  # 捕獲後の非稼働ステップ数
        self.remaining_inactive_steps = 0  # 残りの非稼働ステップ数

        # 稼働日数を週5日に固定
        self.active_steps = self.set_active_steps(active_days_per_week)
        self.current_step = 0


    def set_active_steps(self, active_days_per_week):
        """
        1週間（56ステップ）のうち稼働するステップをランダムに選択。
        たとえば、週に5日稼働する場合、5×8 = 40ステップをランダムに選びます。
        """
        active_steps = active_days_per_week * self.steps_per_day
        return sorted(self.random.sample(range(self.steps_per_week), active_steps))




#    def step(self):
#        # 現在のステップが設定された稼働ステップか確認
#        if (self.current_step % self.steps_per_week) in self.active_steps:
#            current_cell = self.model.grid.get_cell_list_contents([self.pos])
#            kyon_in_cell = [obj for obj in current_cell if isinstance(obj, Kyon)]
#
#            if kyon_in_cell:
#                for kyon in kyon_in_cell:
#                    success_rate = self.calculate_trap_success_rate(self.pos)
#                    if self.random.random() < success_rate:
#                        # 捕獲成功
#                        self.model.grid.remove_agent(kyon)
#                        self.model.schedule.remove(kyon)
#                        self.model.step_captured_kyons += 1
#                        return



    def step(self):
        """
        稼働時間を導入、稼働を5日に変更
        """
        # 非稼働期間中の場合
        if self.remaining_inactive_steps > 0:
            self.remaining_inactive_steps -= 1
            self.current_step += 1  # ステップを進める
            return  # 非稼働状態で終了

        # 現在のステップが設定された稼働ステップか確認
        if (self.current_step % self.steps_per_week) in self.active_steps:
            current_cell = self.model.grid.get_cell_list_contents([self.pos])
            kyon_in_cell = [obj for obj in current_cell if isinstance(obj, Kyon)]

            if kyon_in_cell:
                for kyon in kyon_in_cell:
                    success_rate = self.calculate_trap_success_rate(self.pos)
                    if self.random.random() < success_rate:
                        # 捕獲成功
                        self.model.grid.remove_agent(kyon)
                        self.model.schedule.remove(kyon)
                        self.model.step_captured_kyons += 1
                        # 捕獲成功後の非稼働期間を設定
                        self.remaining_inactive_steps = self.inactive_steps_after_capture
                        return


        # ステップを1進める
        self.current_step += 1


    def calculate_trap_success_rate(self, position):
        """
        現在のマスに基づいて、罠の捕獲成功率を計算する。
        """
        current_cell = self.model.grid.get_cell_list_contents([position])
        success_rate = self.model.base_success_rate  # 基本成功率を設定

        # 食物資源エリアでの成功率を調整
        in_food_area = any(isinstance(obj, FoodResourceArea) for obj in current_cell)
        if in_food_area:
            success_rate *= 1.5    #1.5から変更
        return success_rate


#class VegetationDensity(mesa.Agent):
#    """
#    各セルに植生密度を設定するエージェント。密度は "dense"（濃い）、"normal"（普通）、"sparse"（薄い）のいずれか。
#    """
#    def __init__(self, unique_id, pos, model, density):
#        super().__init__(unique_id, model)
#        self.pos = pos
#        self.density = density
#
#    def step(self):
#        pass


class FoodResourceArea(mesa.Agent):
    """
    フィールド上の食物資源エリアを表すエージェント。エリア内ではキョンの動きに影響を与える。
    """
    def __init__(self, unique_id, pos, model):
        super().__init__(unique_id, model)
        self.pos = pos

    def step(self):
        pass

