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
from kyon.agents import Kyon, Trap,  FoodResourceArea, BeastPath  # 修正: Kyon, Trap, VegetationDensity, FoodResourceArea をインポート    VegetationDensity,を削除
import pandas as pd


class KyonModel(mesa.Model):
    """
    キョン繁殖シミュレーションモデル
    """

    height = 400
    width = 400
    initial_kyon = 250  #15
    initial_traps = 150   #25   #60,100,200から選択       
    food_resource_area_percentage = 0.4  # 食物資源エリア
    base_success_rate=0.6  #捕獲成功率0.01
    trap_recovery_turns=0    #罠の回復ステップ数
    #placement_method="random"  # "random", "dense_vegetation_modifier", "food_resource",   などを選択          
    simulation_counter = 1
    steps_per_day = 8  # 1日8ステップ

    verbose = False  # モニタリングのための出力

    description = (
        "Kyon繁殖シミュレーションモデル"
    )

    def __init__(
        self,
        height=400,
        width=400,
        initial_kyon=250,  #15
        initial_traps=150,   #25   #60,100,200から選択
        food_resource_area_percentage=0.4,  # 食物資源エリア
        base_success_rate=0.6,   #捕獲成功率0.01
        trap_recovery_turns=0,    #罠の回復ステップ数
        #placement_method="random",  # "random", "dense_vegetation", "food_resource"  などを選択
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
        self.trap_recovery_turns = trap_recovery_turns    #罠の回復ステップ数
        #self.placement_method = placement_method  # 罠の配置方法を保持
        self.simulation_counter = simulation_counter        
        self.schedule = RandomActivationByTypeFiltered(self)
        self.grid = mesa.space.MultiGrid(self.width, self.height, torus=True)
        self.increased_kyon = 0
        self.step_captured_kyons = 0 
        self.kyon_nums = []
        self.captured_kyons = []
        self.dead_kyons = []
        self.born_kyons = []
        self.kyon_increase = []
        self.current_step = 0  # 現在のステップを追加
        self.steps_per_day = 8  # 1日を8ステップで表現        
        
        # データ収集
        self.datacollector = mesa.DataCollector(
            {
                "Traps": lambda m: m.schedule.get_type_count(Trap),
                "Kyon": lambda m: m.schedule.get_type_count(Kyon),
                "BornKyon": lambda m: m.schedule.get_type_count(Kyon, lambda x: x.kyon_reproduce_count),
                "DeadinLifeKyon": lambda m: m.schedule.get_type_count(Kyon, lambda x: x.kyon_reproduce_count) - m.schedule.get_type_count(Trap, lambda x: x.is_hunt) - m.increased_kyon,
                "CapturedKyon": lambda m: m.step_captured_kyons,
                "IncreasedKyon": lambda m: m.increased_kyon,
            }
        )


        # キョンの初期年齢分布
        data = lognorm(s=0.5, scale=540).rvs(size=self.initial_kyon)
        age_distribution = []
        for d in data:
            age_distribution.append(round(d))


        # 獣道を配置
        self.set_beast_paths()  
        
        # 植生密度を設定
        #self.set_vegetation_density()
        
        # 食物資源エリアを生成
        self.set_food_resource_areas()
        

        # キョンを配置
        for i in range(self.initial_kyon):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            age = age_distribution[i]  # 初期年齢をリストから取得
            kyon = Kyon(self.next_id(), (x, y), self, False, after_birth=age)
            self.grid.place_agent(kyon, (x, y))
            self.schedule.add(kyon)


#        # 罠を配置
#        if self.placement_method == "dense_vegetation":
#            self.place_traps_in_dense_vegetation_beast_paths()
#        elif self.placement_method == "food_resource":
#            self.place_traps_in_food_resource_beast_paths()            
#        else:
#            self.place_traps_in_random_beast_paths()

        # 罠を配置（獣道にのみ配置）
        self.place_traps_in_random_beast_paths()

        self.running = True
        self.counter = 0
        self.before_kyon_count = self.initial_kyon
        self.datacollector.collect(self)



#    def set_vegetation_density(self):
#        """
#        フィールドを10x10のブロックに分割し、それぞれのブロックに対して
#        植生密度（濃い30%、普通40%、薄い30%）をランダムに割り振る。
#        """
#        block_size = 20   
#        densities = ["dense"] * 120 + ["normal"] * 160 + ["sparse"] * 120  
#        #densities = ["dense"] * 30 + ["normal"] * 40 + ["sparse"] * 30
#        self.random.shuffle(densities)
#
#        for i in range(20):  # 20列,10から変更
#            for j in range(20):  # 20行から変更
#                density = densities.pop()
#
#                for x in range(i * block_size, (i + 1) * block_size):
#                    for y in range(j * block_size, (j + 1) * block_size):
#                        patch = VegetationDensity(self.next_id(), (x, y), self, density)  
#                        self.grid.place_agent(patch, (x, y))
    
    def set_food_resource_areas(self):
        """
        フィールドを20x20のブロックに分割し、その中の40％に当たる40ブロックを食物資源エリアとしてランダムに割り当てる。
        """
        block_size = 10  # 各ブロックは5x5マス,5から変更
        total_blocks = 40 * 40  # 全フィールドは400ブロック、20から変更
        #total_blocks = 20 * 20
        food_area_blocks = int(total_blocks * 0.4)    #40% = 640ブロックが食物資源エリア

        food_area_positions = []
        for i in range(40):  # 40列,20
            for j in range(40):  # 40行
                food_area_positions.append((i, j))

        # ランダムに120ブロックを食物資源エリアに割り当てる
        self.random.shuffle(food_area_positions)
        food_area_positions = food_area_positions[:food_area_blocks]

        for i, j in food_area_positions:
            # 各ブロックの中に5x5の食物資源エリアを配置
            for x in range(i * block_size, (i + 1) * block_size):
                for y in range(j * block_size, (j + 1) * block_size):
                    food_area = FoodResourceArea(self.next_id(), (x, y), self)
                    self.grid.place_agent(food_area, (x, y))


    def set_beast_paths(self):
        """
        獣道の各区間ごとに異なる開始地点と方向を設定して、曲がりくねった獣道を生成します。
        """
        # 手動で設定する獣道の区間リスト
        # (start_x, start_y, direction_x, direction_y, length) の形式で区間を定義
        beast_path_sections = [
            # 獣道1の各区間
            [(0, 100, 1, 0, 30),  
             (30, 100, 1, -1, 20),  
             (50, 80, -1, -1, 10), 
             (40, 70, -1, -1, 20),
             (20, 50, 1, -1, 50)],           
            # 獣道1の各区間
            [(330, 90, 1, 0, 10),  
             (340, 90, 0, 1, 30),  
             (340, 120, 1, 1, 20), 
             (360, 140, 1, 0, 20),
             (380, 140, 1, 1, 20)],              
            # 獣道11の各区間
            [(40, 0, 1, 1, 40)], 
            # 獣道11の各区間
            [(340, 120, -1, 0, 40)], 
            # 獣道11の各区間
            [(0, 110, 1, -1, 10)],             
            # 獣道11の各区間
            [(290, 250, -1, 1, 30)],  
            # 獣道2の各区間
            [(350, 30, 1, 1, 10),  
             (360, 40, -1, 1, 15),  
             (345, 55, 1, 1, 20), 
             (365, 75, -1, 0, 40),
             (325, 75, -1, 1, 5),
             (320, 80, 1, 1, 10)],
            # 獣道3の各区間
            [(400, 400, -1, -1, 80), 
             (320, 320, 1, -1, 30), 
             (350, 290, -1, -1, 40), 
             (310, 250, -1, 0, 20)],
            # 獣道3の各区間
            [(70, 250, 1, 1, 30), 
             (100, 280, 1, 0, 10),  
             (110, 280, 0, 1, 20)],
            # 獣道3の各区間
            [(160, 80, -1, 0, 20), 
             (140, 80, 0, -1, 40),  
             (140, 40, -1, -1, 40)],            
            # 獣道3の各区間
            [(230, 350, 0, -1, 20), 
             (230, 330, -1, 1, 30), 
             (200, 360, -1, -1, 30), 
             (170, 330, 0, 1, 30)],            
            # 獣道4の各区間
            [(300, 200, 0, -1, 80),  
             (300, 120, -1, -1, 30)],
            # 獣道4の各区間
            [(100, 180, 1, 1, 10),  
             (110, 190, 1, 0, 30)],            
            # 獣道7の各区間  
            [(320, 150, -1, 1, 70)],       
            # 獣道7の各区間  
            [(150, 160, -1, 1, 30)],      
            # 獣道7の各区間  
            [(150, 200, -1, -1, 10)],                               
            # 獣道5の各区間
            [(150, 200, 1, 0, 50), 
             (200, 200, 1, 1, 40), 
             (240, 240, -1, 1, 30), 
             (210, 270, -1, -1, 20)], 
            # 6
            [(70, 250, -1, 1, 50), 
             (20, 300, 1, 1, 40), 
             (60, 340, 0, 1, 50), 
             (60, 390, 1, 1, 10)],
            # 獣道7の各区間  
            [(40, 370, 1, 0, 40)], 
            # 獣道7の各区間  
            [(20, 300, 0, -1, 70)],  
            # 獣道7の各区間
            [(80, 80, 1, 1, 40), 
             (120, 120, -1, 1, 40)],  
            # 獣道7の各区間  
            [(100, 180, 0, -1, 90)],         
            # 獣道8の各区間
            [(120, 400, 1, -1, 50), 
             (170, 350, 1, 1, 50)],
            # 獣道9の各区間
            [(220, 0, 0, 1, 20),  
             (220, 20, 1, 1, 40),  
             (260, 60, 1, -1, 40), 
             (300, 20, 0, -1, 20)], 
            # 獣道10の各区間
            [(110, 300, 1, -1, 30)],   
            # 獣道11の各区間
            [(170, 170, 0, -1, 100)],    
            # 獣道11の各区間
            [(180, 160, -1, 0, 30)],             
             # 獣道11の各区間
            [(160, 80, 1, 1, 20)], 
            # 獣道11の各区間
            [(330, 270, 0, -1, 30),
             (330, 240, 1, -1, 40)],           
             # 獣道11の各区間
            [(260, 370, 0, -1, 90)],  
            # 獣道7の各区間  
            [(380, 350, -1, 1, 50)], 
            # 獣道12の各区間    
            [(230, 350, 1, 0, 50)]                      
        ]

        for sections in beast_path_sections:
            for section in sections:
                start_x, start_y, dir_x, dir_y, length = section
                for i in range(length):
                    x = (start_x + i * dir_x) % self.width
                    y = (start_y + i * dir_y) % self.height
                    beast_path = BeastPath(self.next_id(), (x, y), self)
                    self.grid.place_agent(beast_path, (x, y))
                    self.schedule.add(beast_path)
                   


#    def place_traps_in_food_resource_beast_paths(self):
#        """
#        食物資源エリア内の獣道に罠を集中して配置します。
#        食物資源エリア内の獣道がない場合、他のエリアの獣道にランダムに配置します。
#        """
#        # 食物資源エリア内の獣道セルの位置リストを取得
#        food_beast_path_cells = []
#        all_beast_path_cells = []
#
#        # フィールド全体をスキャンして、食物資源エリアかつ獣道のセルを取得
#        for (content, pos) in self.grid.coord_iter():
#            has_food_resource_area = any(isinstance(obj, FoodResourceArea) for obj in content)
#            has_beast_path = any(isinstance(obj, BeastPath) for obj in content)
#            if has_beast_path:
#                all_beast_path_cells.append(pos)  # 全ての獣道セルを追加
#                    food_beast_path_cells.append(pos)  # 食物資源エリア内の獣道セルを追加
#
#        # 罠の配置セルリストを決定
#        if food_beast_path_cells:
#            target_cells = food_beast_path_cells  # 食物資源エリア内の獣道セルがある場合
#        else:
#            print("食物資源エリア内の獣道セルが存在しないため、他のエリアの獣道に配置します。")
#            target_cells = all_beast_path_cells  # 食物資源エリア内の獣道セルがない場合、他のエリアの獣道セルを使用
#
#        # 罠を配置
#        for _ in range(self.initial_traps):
#            pos = self.random.choice(target_cells)
#            trap = Trap(self.next_id(), pos, self)
#            self.grid.place_agent(trap, pos)
#            self.schedule.add(trap)

#    def place_traps_in_dense_vegetation_beast_paths(self):
#        """
#        濃い植生エリア内の獣道に罠を集中して配置します。
#        濃い植生エリア内の獣道がない場合、他のエリアの獣道にランダムに配置します。
#        """
#        # 濃い植生エリア内の獣道セルの位置リストと全ての獣道セルの位置リストを取得
#        dense_beast_path_cells = []
#        all_beast_path_cells = []
#
#        # フィールド全体をスキャンして、濃い植生エリアかつ獣道のセルを取得
#        for (content, pos) in self.grid.coord_iter():
#            has_dense_vegetation = any(isinstance(obj, VegetationDensity) and obj.density == "dense" for obj in content)
#            has_beast_path = any(isinstance(obj, BeastPath) for obj in content)
#            if has_beast_path:
#                all_beast_path_cells.append(pos)  # 全ての獣道セルを追加
#                if has_dense_vegetation:
#                    dense_beast_path_cells.append(pos)  # 濃い植生エリア内の獣道セルを追加
#
#        # 罠の配置セルリストを決定
#        if dense_beast_path_cells:
#            target_cells = dense_beast_path_cells  # 濃い植生エリア内の獣道セルがある場合
#        else:
#            print("濃い植生エリア内の獣道セルが存在しないため、他のエリアの獣道に配置します。")
#            target_cells = all_beast_path_cells  # 濃い植生エリア内の獣道セルがない場合、他のエリアの獣道セルを使用
#
#        # 罠を配置
#        for _ in range(self.initial_traps):
#            pos = self.random.choice(target_cells)
#            trap = Trap(self.next_id(), pos, self)
#            self.grid.place_agent(trap, pos)
#            self.schedule.add(trap)

    def place_traps_in_random_beast_paths(self):
        """
        獣道にランダムに罠を配置します。
        """
        # 獣道セルのみを取得
        beast_path_cells = []
        # フィールド全体をスキャンして、獣道のセルを取得
        for (content, pos) in self.grid.coord_iter():
            for obj in content:
                if isinstance(obj, BeastPath):
                    beast_path_cells.append(pos)


        # 初期罠数分だけランダムに配置
        for _ in range(self.initial_traps):
            pos = self.random.choice(beast_path_cells)
            trap = Trap(self.next_id(), pos, self)
            self.grid.place_agent(trap, pos)
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
        self.step_captured_kyons = 0  # ステップ開始時に捕獲数をリセット
        self.step_dead_kyons = 0
        self.step_born_kyons = 0
        # エージェントのアクションを実行
        self.schedule.step()
        
        # 1日（8ステップ）ごとにデータ収集を行う
        if self.current_step % self.steps_per_day == 0:
            # 前日からの増加分（新生 - 自然死 - 捕獲数）を計算
            current_kyon_count = self.schedule.get_type_count(Kyon)
            self.increased_kyon = current_kyon_count - self.before_kyon_count
            
            # データ収集
            self.datacollector.collect(self)
            self.before_kyon_count = current_kyon_count  # 現在のキョン数を次の比較用に保存

            # データをリストに追加
            self.kyon_nums.append(current_kyon_count)
            self.captured_kyons.append(self.step_captured_kyons)
            self.dead_kyons.append(self.step_dead_kyons)  # 自然死亡数を直接使用
            self.born_kyons.append(self.step_born_kyons)  # 生まれたキョンの数
            self.kyon_increase.append(self.increased_kyon)  # 増加分

        # ステップカウンターを1増加
        self.current_step += 1

        if self.current_step == 365 * 5 * self.steps_per_day:  # シュミレーションの期間
            df_result = pd.DataFrame({
                "kyon_nums": self.kyon_nums,
                "captured_kyons": self.captured_kyons,
                "dead_kyons": self.dead_kyons,
                "born_kyons": self.born_kyons,
                "increase": self.kyon_increase
            })
            
            print(df_result)

            
            
            # 選択した罠の設置方法に応じてファイル名を変更
            file_path = f"results/{self.initial_traps}_{self.initial_kyon}_active5_{self.base_success_rate}_result1_.csv"  
            df_result.to_csv(file_path)

            self.running = False