import pandas as pd
import matplotlib.pyplot as plt

# 解析するためのリストを作成
all_data = []

# 正しいファイルパスを使用してデータを読み込む
file_paths = [
    "results/random_150_250_recovery0__0.05_result_1.csv",
    "results/random_150_250_recovery0__0.05_result2_.csv",
    "results/random_150_250_recovery0__0.05_result3_.csv"
]

for file_path in file_paths:
    try:
        df = pd.read_csv(file_path)
        all_data.append(df)
    except FileNotFoundError:
        print(f"File not found: {file_path}")

# データが読み込めたかどうかを確認
if all_data:
    # データフレームを結合（インデックスで）
    combined_df = pd.concat(all_data, axis=0)

    # 平均を計算する
    average_data = combined_df.groupby(combined_df.index).mean()

    # 平均データをCSVとして保存
    average_data.to_csv('results/average_random_150_250_recovery0_0.05.csv')

    # グラフ化
    plt.figure(figsize=(10, 6))

    # 3回分のシミュレーションデータのプロット
    for df in all_data:
        plt.plot(df.index, df['kyon_nums'], alpha=0.3, color='blue', linestyle='-', label='_nolegend_')

    # 3回分の平均データのプロット
    plt.plot(average_data.index, average_data['kyon_nums'], label='平均キョン個体数', color='green', linewidth=2)

    # ラベルとタイトルを設定
    plt.xlabel('ステップ数')
    plt.ylabel('キョン個体数')
    plt.title('キョン個体数の推移：シミュレーションと平均')
    plt.legend()

    # 画像として保存する
    plt.savefig('results/simulation_results_random_150_250_recovery0_0.05.png')

    # グラフを表示
    plt.show()
else:
    print("No data files were loaded.")


#ターミナルまたはコマンドラインで以下を実行して、解析コードを動かします
#python analyze_results.py
