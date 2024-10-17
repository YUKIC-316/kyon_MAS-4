from kyon.model import KyonModel
import mesa

# 10回シミュレーションを実行する
for i in range(10):
    # モデルを作成し、シミュレーションを実行
    model = KyonModel(
        width=100,
        height=100,
        initial_kyon=60,
        initial_traps=50,
        kyon_reproduce=0.005,
        base_success_rate=0.0006,
        dense_vegetation_modifier=0.75,
        normal_vegetation_modifier=1.0,
        sparse_vegetation_modifier=2.0,
        simulation_counter=i + 1  # シミュレーション番号を設定
    )

    # 365*6ステップを実行
    for step in range(365 * 6):
        model.step()
    
    # 結果がCSVに保存されるのを確認する
    print(f"Simulation {i+1} completed.")
