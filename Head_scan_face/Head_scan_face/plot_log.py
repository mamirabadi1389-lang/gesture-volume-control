import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("logs/emotion_log.csv")

if df.empty:
    print("Log khali ast.")
else:
    plt.figure(figsize=(10, 5))
    df['emotion'].value_counts().plot(kind='bar', color='skyblue')
    plt.title("Toziye Ehsasat dar Tool Zaman")
    plt.xlabel("Ehsas")
    plt.ylabel("Tedad")
    plt.tight_layout()
    plt.savefig("logs/emotion_chart.png")
    plt.show()
    print("Nemoodar zakhire shod: logs/emotion_chart.png")