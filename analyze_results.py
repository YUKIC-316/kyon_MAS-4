import pandas as pd

# 統合するための空のリストを作成
all_data = []

# 10回分のシミュレーションデータを読み込んでリストに追加
for i in range(1, 11):
    file_name = f"results/random_50_60_result_{i}.csv"
    df = pd.read_csv(file_name)
    all_data.append(df)

# データフレームを結合（インデックスで）
combined_df = pd.concat(all_data, axis=0)

# 平均を計算する
average_data = combined_df.mean()

# 結果を表示
print("平均値:")
print(average_data)

# グラフ化する場合（例: Kyonの数の推移）
import matplotlib.pyplot as plt

combined_df['kyon_nums'].plot(title='Kyon Population Over Time')
plt.xlabel('Step')
plt.ylabel('Kyon Population')
plt.show()
