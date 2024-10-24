"""
ウルフ-シープ捕食モデル
=========================

NetLogoで見つけたモデルの複製:
  Wilensky, U. (1997). NetLogo ウルフ・シープ捕食モデル。
  http://ccl.northwestern.edu/netlogo/models/WolfSheepPredation.
  ノースウェスタン大学、Center for Connected Learning and Computer-Based Modeling,
  イリノイ州エバンストン。
"""


import mesa
import numpy as np
import math
from scipy.stats import lognorm
from kyon.scheduler import RandomActivationByTypeFiltered
from kyon.agents import Kyon, Trap, VegetationDensity, FoodResourceArea  # 修正: Kyon, Trap, VegetationDensity, FoodResourceArea をインポート
import pandas as pd

class KyonModel(mesa.Model):
    """
    キョン繁殖シミュレーションモデル
    """

    height = 200
    width = 200
    initial_kyon = 60  #15
    initial_traps = 60   #25   #60,100,200から選択       
    food_resource_area_percentage = 0.1  # 食物資源エリア
    base_success_rate=0.05  #捕獲成功率0.01
    dense_vegetation_modifier=1.2
    normal_vegetation_modifier=1.0
    sparse_vegetation_modifier=0.8 
    trap_recovery_turns=0    #罠の回復ステップ数
    placement_method="random"  # "random", "sparse_vegetation", "food_resource",   などを選択          
    simulation_counter = 1

    verbose = False  # モニタリングのための出力

    description = (
        "Kyon繁殖シミュレーションモデル"
    )

    def __init__(
        self,
        width=200,
        height=200,
        initial_kyon=60,  #15
        initial_traps=60,   #25   #60,100,200から選択
        food_resource_area_percentage=0.1,  # 食物資源エリア
        base_success_rate=0.05,   #捕獲成功率0.01
        dense_vegetation_modifier=1.2,
        normal_vegetation_modifier=1.0,
        sparse_vegetation_modifier=0.8,
        trap_recovery_turns=0,    #罠の回復ステップ数
        placement_method="random",  # "random", "sparse_vegetation", "food_resource"  などを選択
        simulation_counter=1,
    ):
        """
        指定されたパラメーターで新しいKyonモデルを作成します。

        """
    
        super().__init__()
        # パラメーターを設定
        self.height = height
        self.width = width
        self.initial_kyon = initial_kyon
        self.initial_traps = initial_traps
        self.food_resource_area_percentage = food_resource_area_percentage  # 食物資源エリアの割合                        
        self.base_success_rate = base_success_rate  # 罠の基本成功率
        self.dense_vegetation_modifier = dense_vegetation_modifier  # 濃い植生での成功率補正
        self.normal_vegetation_modifier = normal_vegetation_modifier  # 普通の植生での成功率補正
        self.sparse_vegetation_modifier = sparse_vegetation_modifier  # 薄い植生での成功率補正
        self.trap_recovery_turns = trap_recovery_turns    #罠の回復ステップ数
        self.placement_method = placement_method  # 罠の配置方法を保持
        self.simulation_counter = simulation_counter        
        self.schedule = RandomActivationByTypeFiltered(self)
        self.grid = mesa.space.MultiGrid(self.width, self.height, torus=True)
        self.increased_kyon = 0
        self.kyon_nums = []
        self.captured_kyons = []
        self.dead_kyons = []
        self.born_kyons = []
        self.kyon_increase = []
        self.datacollector = mesa.DataCollector(
            {
                "Traps": lambda m: m.schedule.get_type_count(Trap),
                "Kyon": lambda m: m.schedule.get_type_count(Kyon),
                "BornKyon":lambda m: m.schedule.get_type_count(
                    Kyon, lambda x: x.kyon_reproduce_count
                ),
                
                "DeadinLifeKyon": lambda m: m.schedule.get_type_count(Kyon, lambda x: x.kyon_reproduce_count) - m.schedule.get_type_count(Trap, lambda x: x.is_hunt) - m.increased_kyon,
                "CapturedKyon":lambda m: m.schedule.get_type_count(
                    Trap, lambda x: x.is_hunt
                ),
                "IncreasedKyon":lambda m:m.increased_kyon,
            }
        )

        data = lognorm(s=0.5, scale=540).rvs(size=self.initial_kyon)
        age_distribution = []
        for d in data:
            age_distribution.append(round(d))

        # 植生密度を設定
        self.set_vegetation_density()
        
        # 食物資源エリアを生成
        self.set_food_resource_areas()
        
        
        # Create kyon:
        for i in range(self.initial_kyon):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            kyon = Kyon(self.next_id(), (x, y), self, False, int(age_distribution[i])) 
            self.grid.place_agent(kyon, (x, y))
            self.schedule.add(kyon)

        # 罠を配置
        if self.placement_method == "sparse_vegetation":
            self.place_traps_in_sparse_areas()
        elif self.placement_method == "food_resource":
            self.place_traps_in_food_areas()
        else:
            self.place_traps_randomly()

        self.running = True
        self.counter = 0
        self.before_kyon_count = self.initial_kyon
        self.datacollector.collect(self)

    def set_vegetation_density(self):
        """
        フィールドを10x10のブロックに分割し、それぞれのブロックに対して
        植生密度（濃い30%、普通40%、薄い30%）をランダムに割り振る。
        """
        block_size = 20   #10から変更
        densities = ["dense"] * 30 + ["normal"] * 40 + ["sparse"] * 30  #30,40,30から変更
        self.random.shuffle(densities)

        for i in range(10):  # 10列から変更
            for j in range(10):  # 10行から変更
                density = densities.pop()

                for x in range(i * block_size, (i + 1) * block_size):
                    for y in range(j * block_size, (j + 1) * block_size):
                        patch = VegetationDensity(self.next_id(), (x, y), self, density)  
                        self.grid.place_agent(patch, (x, y))
    
    def set_food_resource_areas(self):
        """
        フィールドを40x40のブロックに分割し、その中の20％に当たる320ブロックを食物資源エリアとしてランダムに割り当てる。
        """
        block_size = 5  # 各ブロックは5x5マス,5から変更
        total_blocks = 40 * 40  # 全フィールドは400ブロック、20から変更
        food_area_blocks = int(total_blocks * 0.1)    #20% = 320ブロックが食物資源エリア

        food_area_positions = []
        for i in range(40):  # 20列
            for j in range(40):  # 20行
                food_area_positions.append((i, j))

        # ランダムに160ブロックを食物資源エリアに割り当てる
        self.random.shuffle(food_area_positions)
        food_area_positions = food_area_positions[:food_area_blocks]

        for i, j in food_area_positions:
            # 各ブロックの中に5x5の食物資源エリアを配置
            for x in range(i * block_size, (i + 1) * block_size):
                for y in range(j * block_size, (j + 1) * block_size):
                    food_area = FoodResourceArea(self.next_id(), (x, y), self)
                    self.grid.place_agent(food_area, (x, y))


    # 罠をランダムに配置する関数
    def place_traps_randomly(self):
        for i in range(self.initial_traps):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            trap = Trap(self.next_id(), (x, y), self)
            trap.trap_recovery_turns = self.trap_recovery_turns
            self.grid.place_agent(trap, (x, y))
            self.schedule.add(trap)

    # 食物資源エリアに罠を集中して配置する関数
    def place_traps_in_food_areas(self):
        """
        食物資源エリアに罠を集中して配置する。
        """
        food_cells = []

        # フィールド全体をスキャンして、食物資源エリアの座標を取得する
        for (content, pos) in self.grid.coord_iter():
            for obj in content:
                if isinstance(obj, FoodResourceArea):
                    food_cells.append(pos)

        # 食物資源エリアに罠を設置
        for _ in range(self.initial_traps):
            if food_cells:
                # 食物資源エリアからランダムに選んで罠を配置
                pos = self.random.choice(food_cells)
                trap = Trap(self.next_id(), pos, self)
                self.grid.place_agent(trap, pos)
                self.schedule.add(trap)
            else:
                # 食物資源エリアがなければランダムに配置
                x = self.random.randrange(self.width)
                y = self.random.randrange(self.height)
                trap = Trap(self.next_id(), (x, y), self)
                self.grid.place_agent(trap, (x, y))
                self.schedule.add(trap)



    #植生の薄いエリアに集中的に罠を配置する際のコード以下28行
    def place_traps_in_sparse_areas(self):
        """
        植生が薄いエリア ("sparse") に罠を集中して配置する。
        """
        sparse_cells = []

        # フィールド全体をスキャンして、植生が薄いエリア ("sparse") の座標を取得する
        for (content, pos) in self.grid.coord_iter():
            vegetation_density = [obj for obj in content if isinstance(obj, VegetationDensity)]
            if vegetation_density and vegetation_density[0].density == "sparse":
                sparse_cells.append(pos)
        
        # 植生が薄いエリアに罠を設置
        for _ in range(self.initial_traps):
            if sparse_cells:
                # 植生が薄いエリアからランダムに選んで罠を配置
                pos = self.random.choice(sparse_cells)
                trap = Trap(self.next_id(), pos, self)
                self.grid.place_agent(trap, pos)
                self.schedule.add(trap)
            else:
                # 植生が薄いエリアがなければランダムに配置
                x = self.random.randrange(self.width)
                y = self.random.randrange(self.height)
                trap = Trap(self.next_id(), (x, y), self)
                self.grid.place_agent(trap, (x, y))
                self.schedule.add(trap)

    def get_distance(self, pos1, pos2):
        """
        2つの座標間のユークリッド距離を計算する。
        pos1, pos2はタプル (x, y) の形式。
        """
        dx = abs(pos1[0] - pos2[0])
        dy = abs(pos1[1] - pos2[1])
        return math.sqrt(dx ** 2 + dy ** 2)    

    def step(self):
        self.schedule.step()
 
        self.increased_kyon = self.schedule.get_type_count(Kyon) - self.before_kyon_count
        
        self.datacollector.collect(self)
        
        self.before_kyon_count = self.schedule.get_type_count(Kyon)

        self.kyon_nums.append(self.schedule.get_type_count(Kyon))
        self.captured_kyons.append(self.schedule.get_type_count(Trap, lambda x: x.is_hunt))
        self.dead_kyons.append(self.schedule.get_type_count(Kyon, lambda x: x.kyon_reproduce_count) - self.schedule.get_type_count(Trap, lambda x: x.is_hunt) - self.increased_kyon)
        self.born_kyons.append(self.schedule.get_type_count(Kyon, lambda x: x.kyon_reproduce_count))
        self.kyon_increase.append(self.increased_kyon)        
 
       
        self.counter += 1

        if self.counter == 365*6:  # シュミレーションの期間
            df_result = pd.DataFrame({
                "kyon_nums": self.kyon_nums,
                "captured_kyons": self.captured_kyons,
                "dead_kyons": self.dead_kyons,
                "born_kyons": self.born_kyons,
                "increase": self.kyon_increase
            })
            
            print(df_result)

            
            # 結果をファイルに保存
            placement_method = self.placement_method  
            
            # 選択した罠の設置方法に応じてファイル名を変更
            file_path = f"results/{placement_method}_{self.initial_traps}_{self.initial_kyon}_recovery{self.trap_recovery_turns}__{self.base_success_rate}_result_1.csv"  #{self.trap_recovery_turns}_
            df_result.to_csv(file_path)

            self.running = False

