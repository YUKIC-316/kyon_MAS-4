import pandas as pd
import matplotlib.pyplot as plt

# 罠の張り方の異なる3種類の平均データファイルを読み込む
methods = ['random', 'sparse_vegetation', 'food_resource']  # 罠の張り方の種類
colors = ['blue', 'green', 'red']  # 各張り方に対するグラフの色

# 各張り方の平均データを読み込む (ファイル名が変わったらそれに対応すること忘れずに：罠の張り方、罠数、キョン数、回復数)
average_data_files = {
    'random': 'results/average_random_100_60_recovery_0.csv',
    'sparse_vegetation': 'results/average_sparse_vegetation_100_60_recovery_0.csv',
    'food_resource': 'results/average_food_resource_100_60_recovery_0.csv'
}

# グラフ化
plt.figure(figsize=(10, 6))

# 各張り方の平均データをプロット
for i, method in enumerate(methods):
    # 保存された平均データを読み込む
    average_data = pd.read_csv(average_data_files[method])
    
    # 平均データをグラフにプロット
    plt.plot(average_data.index, average_data['kyon_nums'], label=f'{method} - Average', color=colors[i], linewidth=2)

# ラベルとタイトルを設定
plt.xlabel('Step')
plt.ylabel('Kyon Population')
plt.title('Kyon Population Over Time: Different Trap Placement Methods')
plt.legend()

# 画像として保存
plt.savefig('results/comparison_of_trap_methods.png')  # 保存先のパスを指定

# グラフを表示
plt.show()


#ターミナルまたはコマンドラインで以下を実行して、解析コードを動かします
#python analyze_comparison.py