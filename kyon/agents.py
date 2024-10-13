import mesa
from kyon.random_walk import RandomWalker

class Kyon(RandomWalker):
    """
    草原を歩き回り、繁殖し（無性繁殖）、捕食されるキョン。
    初期化メソッドはRandomWalkerと同じです。
    """
    
    #energy = None
    after_birth = 0

    def __init__(self, unique_id, pos, model, moore,  kyon_reproduce_count=False, after_birth=0):
        super().__init__(unique_id, pos, model, moore=moore)
        #self.energy = energy
        self.kyon_reproduce_count = kyon_reproduce_count
        self.after_birth = after_birth
        #self.is_eat = False

    def step(self):
        """
        モデルのステップ。植生の密度に応じて移動し、草を食べ、繁殖します。
        """
        self.kyon_reproduce_count = False
        self.after_birth += 1
        #self.is_eat = False
        
        # 植生の密度に基づいて移動マス数を決定する
        current_cell = self.model.grid.get_cell_list_contents([self.pos])
        vegetation_density = [obj for obj in current_cell if isinstance(obj, VegetationDensity)][0]
        
        if vegetation_density.density == "dense":  # 濃い植生
            move_steps = 1
        elif vegetation_density.density == "normal":  # 普通の植生
            move_steps = 2
        else:  # 薄い植生
            move_steps = 3

        # ランダムに指定されたマス数だけ移動
        self.random_move(move_steps=move_steps)

        living = True

        #if self.model.grass:
            # エネルギーを減少させる
            #self.energy -= 1
            
            # もし草があれば、食べる
            #this_cell = self.model.grid.get_cell_list_contents([self.pos])
            #grass_patch = [obj for obj in this_cell if isinstance(obj, GrassPatch)][0]
            #if grass_patch.fully_grown:
                #self.energy += self.model.kyon_gain_from_food
                #grass_patch.fully_grown = False
                #self.is_eat = True
                
        # 死亡
        # if self.energy <= 0:
        #     self.model.grid.remove_agent(self)
        #     self.model.schedule.remove(self)
        #     living = False

        # 死亡（年齢が高くなるほど死亡率があがる）
        if self.random.random() < (self.model.kyon_reproduce / 5) * (self.after_birth / 540):
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
            living = False

        # 繁殖
        if living and self.after_birth >= 150 and self.random.random() < self.model.kyon_reproduce / 2:
            # 新しい羊を生成します
            #if self.model.grass:
                #self.energy /= 2
            lamb = Kyon(
                self.model.next_id(), self.pos, self.model, self.moore, self.energy, self.kyon_reproduce_count, 0
            )
            self.model.grid.place_agent(lamb, self.pos)
            self.model.schedule.add(lamb)
            self.kyon_reproduce_count = True


class Trap(mesa.Agent):
    """
    トラップエージェント（罠）。植生の密度に応じて捕獲確率が異なる。
    """

    #energy = None

    def __init__(self, unique_id, pos, model, is_hunt=False):
        super().__init__(unique_id, model)
        #self.energy = energy
        self.is_hunt = is_hunt  # 捕獲の成功を示すフラグ

    def step(self):
        """
        罠は固定されている。キョンが同じセルに入った場合に捕獲を判定する。
        """
        self.is_hunt = False  # 毎ステップ、捕獲フラグを初期化

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

            # 捕獲確率に基づいて捕獲判定
            if self.random.random() < trap_success_rate:
                self.is_hunt = True  # 捕獲に成功
                for kyon in kyon_in_cell:
                    self.model.grid.remove_agent(kyon)  # キョンを捕獲して取り除く
                    self.model.schedule.remove(kyon)
                    
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
