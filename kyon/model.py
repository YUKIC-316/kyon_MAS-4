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
from scipy.stats import lognorm
from kyon.scheduler import RandomActivationByTypeFiltered
from kyon.agents import Kyon, Trap, VegetationDensity  # 修正: Kyon, Trap, VegetationDensity をインポート
import pandas as pd

class KyonModel(mesa.Model):
    """
    キョン繁殖シミュレーションモデル
    """

    height = 100
    width = 100

    initial_kyon = 60
    initial_traps = 50

    kyon_reproduce = 0.005
    #wolf_reproduce = 0

    #capture_success_rate = 0.1
    base_success_rate=0.0006
    dense_vegetation_modifier=0.75
    normal_vegetation_modifier=1.0
    sparse_vegetation_modifier=2.0
    
    #wolf_gain_from_food = 0

    #grass = True
    #grass_regrowth_time = 3
    #Kyon_gain_from_food = 4
    
    
    simulation_counter = 1

    verbose = False  # モニタリングのための出力

    description = (
        "Kyon繁殖シミュレーションモデル"
    )

    def __init__(
        self,
        width=100,
        height=100,
        initial_kyon=60,
        initial_traps=50,
        kyon_reproduce=0.005,
        #wolf_reproduce=0,
        #wolf_gain_from_food=0,
        #grass=True,
        #grass_regrowth_time=3,
        #kyon_gain_from_food=4,
        #capture_success_rate=0.1,
        base_success_rate=0.0006,
        dense_vegetation_modifier=0.75,
        normal_vegetation_modifier=1.0,
        sparse_vegetation_modifier=2.0,
        simulation_counter=1,
    ):
        """
        指定されたパラメーターで新しいKyonモデルを作成します。

        """
    
        super().__init__()
        # パラメーターを設定
        self.width = width
        self.height = height
        self.initial_kyon = initial_kyon
        self.initial_traps = initial_traps
        self.kyon_reproduce = kyon_reproduce
        #self.wolf_reproduce = wolf_reproduce
        #self.wolf_gain_from_food = wolf_gain_from_food
        #self.grass = grass
        #self.grass_regrowth_time = grass_regrowth_time
        #self.kyon_gain_from_food = kyon_gain_from_food
        self.base_success_rate = base_success_rate  # 罠の基本成功率
        self.dense_vegetation_modifier = dense_vegetation_modifier  # 濃い植生での成功率補正
        self.normal_vegetation_modifier = normal_vegetation_modifier  # 普通の植生での成功率補正
        self.sparse_vegetation_modifier = sparse_vegetation_modifier  # 薄い植生での成功率補正
        self.simulation_counter = simulation_counter

        self.schedule = RandomActivationByTypeFiltered(self)
        self.grid = mesa.space.MultiGrid(self.width, self.height, torus=True)
        self.increased_kyon = 0
        self.kyon_nums = []
        self.captured_kyons = []
        self.dead_kyons = []
        self.born_kyons = []
        #self.eaten_grasses = []
        self.kyon_increase = []
        self.datacollector = mesa.DataCollector(
            {
                "Traps": lambda m: m.schedule.get_type_count(Trap),
                "Kyon": lambda m: m.schedule.get_type_count(Kyon),
                #"Grass": lambda m: m.schedule.get_type_count(
                    #GrassPatch, lambda x: x.fully_grown
                #),
                #"EatenGrass": lambda m: m.schedule.get_type_count(
                    #Kyon, lambda x: x.is_eat
                #),
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

        # 植生密度を設定（GrassPatch を使用）
        self.set_vegetation_density()
        
        # Create kyon:
        for i in range(self.initial_kyon):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            #energy = self.random.randrange(2 * self.kyon_gain_from_food)
            # print(type(energy))
            kyon = Kyon(self.next_id(), (x, y), self, False, int(age_distribution[i])) 
            self.grid.place_agent(kyon, (x, y))
            self.schedule.add(kyon)

        # Create traps
        for i in range(self.initial_traps):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            # energy = self.random.randrange(2 * self.wolf_gain_from_food)
            energy = self.random.randrange(2)
            trap = Trap(self.next_id(), (x, y), self)
            self.grid.place_agent(trap, (x, y))
            self.schedule.add(trap)

        # Create grass patches
        #if self.grass:
            #for agent, x, y in self.grid.coord_iter():

                #fully_grown = self.random.choice([True, False])

                #if fully_grown:
                    #countdown = self.grass_regrowth_time
                #else:
                    #countdown = self.random.randrange(self.grass_regrowth_time)

                #patch = GrassPatch(self.next_id(), (x, y), self, fully_grown, countdown)
                #self.grid.place_agent(patch, (x, y))
                #self.schedule.add(patch)

        self.running = True
        self.counter = 0
        self.before_kyon_count = self.initial_kyon
        self.datacollector.collect(self)

    def set_vegetation_density(self):
        """
        フィールドを10x10のブロックに分割し、それぞれのブロックに対して
        植生密度（濃い30%、普通40%、薄い30%）をランダムに割り振る。
        """
        block_size = 10
        densities = ["dense"] * 30 + ["normal"] * 40 + ["sparse"] * 30
        self.random.shuffle(densities)

        for i in range(10):  # 10列
            for j in range(10):  # 10行
                density = densities.pop()

                for x in range(i * block_size, (i + 1) * block_size):
                    for y in range(j * block_size, (j + 1) * block_size):
                        patch = VegetationDensity(self.next_id(), (x, y), self, density)  
                        self.grid.place_agent(patch, (x, y))
                        
    def step(self):
        self.schedule.step()
 
        self.increased_kyon = self.schedule.get_type_count(Kyon) - self.before_kyon_count
        # collect data
        self.datacollector.collect(self)

        self.before_kyon_count = self.schedule.get_type_count(Kyon)

        '''
        # キョンの増減数 = 子を産んだキョン - 捉えられたキョン - 寿命で死んだキョン
        # 寿命で死んだキョン = 子を産んだキョン - 捉えられたキョン - キョンの増減数

        # キョンの数
        print(f"キョンの数：{self.schedule.get_type_count(Kyon)}")
        
        # 子を産んだキョンの数
        print(f"子を産んだキョン：{self.schedule.get_type_count(Kyon, lambda x: x.kyon_reproduce_count)}")

        # 捉えられたキョンの数
        print(f"捉えられたキョン：{self.schedule.get_type_count(Wolf, lambda x: x.is_hunt)}")

        # 寿命で死んだキョン
        print(f"寿命で死んだキョン：{self.schedule.get_type_count(Kyon, lambda x: x.kyon_reproduce_count) - self.schedule.get_type_count(Wolf, lambda x: x.is_hunt) - self.increased_kyon}")

        # キョンの増減数
        print(f"キョンの増減数：{self.increased_kyon}")

        # キョンが食べた草の数
        print(f"キョンが食べた草の数：{self.schedule.get_type_count(Kyon, lambda x: x.is_eat)}")

        '''

        self.kyon_nums.append(self.schedule.get_type_count(Kyon))
        self.captured_kyons.append(self.schedule.get_type_count(Trap, lambda x: x.is_hunt))
        self.dead_kyons.append(self.schedule.get_type_count(Kyon, lambda x: x.kyon_reproduce_count) - self.schedule.get_type_count(Trap, lambda x: x.is_hunt) - self.increased_kyon)
        self.born_kyons.append(self.schedule.get_type_count(Kyon, lambda x: x.kyon_reproduce_count))
        #self.eaten_grasses.append(self.schedule.get_type_count(Kyon, lambda x: x.is_eat))
        self.kyon_increase.append(self.increased_kyon)

        self.counter += 1

        if self.counter == 365*6:
            df_result = pd.DataFrame({
                "kyon_nums": self.kyon_nums,
                "captured_kyons": self.captured_kyons,
                "dead_kyons": self.dead_kyons,
                "born_kyons": self.born_kyons,
                #"eaten_grasses": self.eaten_grasses,
                "increase": self.kyon_increase
            })

            print(df_result)

            df_result.to_csv(f"{self.initial_kyon}_{self.initial_traps}_{self.base_success_rate}_result_{self.simulation_counter}.csv")

            self.running = False
