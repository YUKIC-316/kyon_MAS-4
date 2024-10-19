import pandas as pd
import matplotlib.pyplot as plt

# 解析するためのリストを作成
all_data = []

# 10回分のシミュレーションデータを読み込んでリストに追加
for i in range(1, 11):    
    file_name = f"results/sparse_vegetation_100_60_recovery_0_result_{i}.csv"   # "random", "sparse_vegetation", "food_resource" などを選択 # 罠の回復ステップ数を変更忘れずに
    df = pd.read_csv(file_name)
    all_data.append(df)

# データフレームを結合（インデックスで）
combined_df = pd.concat(all_data, axis=0)

# 平均を計算する
average_data = combined_df.groupby(combined_df.index).mean()

# 平均データをCSVとして保存
average_data.to_csv('results/average_sparse_vegetation_100_60_recovery_0.csv')  # "random", "sparse_vegetation", "food_resource" などを選択 # 罠の回復ステップ数を変更忘れずに

# グラフ化
plt.figure(figsize=(10, 6))

# 10回分のシミュレーションデータのプロット
for df in all_data:
    plt.plot(df.index, df['kyon_nums'], alpha=0.3, color='blue', linestyle='-', label='_nolegend_')

# 10回分の平均データのプロット
plt.plot(average_data.index, average_data['kyon_nums'], label='Average Kyon Population', color='green', linewidth=2)

# ラベルとタイトルを設定
plt.xlabel('Step')
plt.ylabel('Kyon Population')
plt.title('Kyon Population Over Time: Simulations and Average')
plt.legend()

# 画像として保存する
plt.savefig('results/simulation_results_sparse_vegetation_100_60_recovery_0_.png')  # "random", "sparse_vegetation", "food_resource" などを選択 # 保存先のパスを指定、罠の回復ステップ数を変更忘れずに 



# グラフを表示
plt.show()

#ターミナルまたはコマンドラインで以下を実行して、解析コードを動かします
#python analyze_results.py
