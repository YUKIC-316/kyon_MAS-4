from kyon.model import KyonModel
import mesa

# 罠の回復ターン数や配置方法を設定する
trap_recovery_turns = 0  # 罠が捕獲後に再び機能するまでのターン数
placement_method = "sparse_vegetation"  # "random", "sparse_vegetation", "food_resource" などを選択


# 10回シミュレーションを実行する
for i in range(10):
    # モデルを作成し、シミュレーションを実行
    model = KyonModel(
        width=100,
        height=100,
        initial_kyon=60,
        initial_traps=100,    #60,100,200から選択
        #kyon_reproduce=0.005,    #削除
        base_success_rate=0.0006,
        dense_vegetation_modifier=0.75,
        normal_vegetation_modifier=1.0,
        sparse_vegetation_modifier=2.0,
        trap_recovery_turns=trap_recovery_turns,  # 罠の回復ターン数を設定
        simulation_counter=i + 1,  # シミュレーション番号を設定
        placement_method=placement_method  # 罠の配置方法を設定
    )

    # 365*6ステップを実行
    for step in range(365 * 6):
        model.step()
    
    # 結果がCSVに保存されるのを確認する
    print(f"Simulation {i+1} completed with trap recovery turns {trap_recovery_turns}.")


#一回だけシミュレーション動かすとき
#from kyon.server import server

#server.launch()