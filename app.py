import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib_fontja
from matplotlib.backends.backend_pdf import PdfPages
import io
import json
import os
from datetime import datetime

# ページ設定
st.set_page_config(
    page_title="視覚のQOL調査 AS-20",
    page_icon="👁️",
    layout="wide"
)

# データ保存用ディレクトリ
DATA_DIR = "survey_data"
os.makedirs(DATA_DIR, exist_ok=True)

# AS-20アンケート質問項目
QUESTIONS = [
    "1. 私の目が人にどう見られるかが気になる",
    "2. 何も言われなくても、人が私の目のことを気にしているように感じる",
    "3. 私の目のせいで、人に見られていると不快に感じる",
    "4. 自分の目のせいで、私を見ている人が、何を考えているのだろうと考えてしまう",
    "5. 自分の目のせいで、人は私に機会を与えてくれない",
    "6. 私は自分の目を気にしている",
    "7. 自分の目のせいで、人は私を見るのを避ける",
    "8. 自分の目のせいで、他の人より劣っていると感じる",
    "9. 自分の目のせいで、人は私に対して違う反応をする",
    "10. 自分の目のせいで、初対面の人との交流が難しいと感じる",
    "11. ものが良く見えるように、片方の目を隠したり閉じたりすることがある",
    "12. 自分の目のせいで、読むのを避けてしまう",
    "13. 自分の目のせいで、集中できないので、物事を中断している",
    "14. 奥行きの感覚に問題があると思う",
    "15. 目が疲れる",
    "16. 自分の目の調子のせいで、読むことに支障をきたしている",
    "17. 自分の目が原因で、ストレスを感じる",
    "18. 自分の目が心配だ",
    "19. 自分の目が気になって、趣味を楽しめない",
    "20. 自分の目のせいで、読むときに頻繁に休憩する必要がある"
]

LIKERT_OPTIONS = ["全くない", "まれにしかない", "時々ある", "よくある", "いつもある"]

SCORE_MAP = {
    "全くない": 100,
    "まれにしかない": 75,
    "時々ある": 50,
    "よくある": 25,
    "いつもある": 0
}

PSYCHOSOCIAL_ITEMS = list(range(0, 10))
FUNCTIONAL_ITEMS = list(range(10, 20))


def save_response(name, patient_id, responses):
    scores = [SCORE_MAP[r] for r in responses]
    total_avg = sum(scores) / 20
    psychosocial_avg = sum(scores[i] for i in PSYCHOSOCIAL_ITEMS) / 10
    functional_avg = sum(scores[i] for i in FUNCTIONAL_ITEMS) / 10

    data = {
        "name": name,
        "patient_id": patient_id,
        "timestamp": datetime.now().isoformat(),
        "responses": responses,
        "scores": scores,
        "total_avg": total_avg,
        "psychosocial_avg": psychosocial_avg,
        "functional_avg": functional_avg
    }

    filename = f"{DATA_DIR}/{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return data


def create_visualization(data):
    fig = plt.figure(figsize=(18, 10))
    gs = fig.add_gridspec(2, 2, width_ratios=[2, 1], height_ratios=[1, 1], hspace=0.3, wspace=0.3)

    ax1 = fig.add_subplot(gs[:, 0])
    questions_short = [f"Q{i+1}" for i in range(20)]
    colors = ['#2ECC71' if s == 100 else '#95E1D3' if s == 75 else '#FFD93D' if s == 50 else '#FF9A76' if s == 25 else '#FF6B6B' for s in data['scores']]
    bars = ax1.barh(questions_short, data['scores'], color=colors, edgecolor='black', linewidth=0.8)
    ax1.set_xlabel('スコア（100点満点）', fontsize=13, fontweight='bold')
    ax1.set_ylabel('質問項目', fontsize=13, fontweight='bold')
    ax1.set_title('項目ごとのスコア（各項目100点満点）', fontsize=16, fontweight='bold', pad=15)
    ax1.set_xlim(0, 110)
    ax1.invert_yaxis()
    ax1.grid(axis='x', alpha=0.3, linestyle='--')
    for bar, score in zip(bars, data['scores']):
        ax1.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2, f'{int(score)}', ha='left', va='center', fontsize=10, fontweight='bold')

    ax2 = fig.add_subplot(gs[0, 1])
    categories = ['全体\n(Q1-20)', '心理社会面\n(Q1-10)', '機能面\n(Q11-20)']
    avg_scores = [data['total_avg'], data['psychosocial_avg'], data['functional_avg']]
    bars2 = ax2.bar(categories, avg_scores, color=['#9B59B6', '#E74C3C', '#3498DB'], edgecolor='black', linewidth=1.5, alpha=0.85, width=0.6)
    ax2.set_ylabel('平均点（100点満点）', fontsize=12, fontweight='bold')
    ax2.set_title('カテゴリー別平均点', fontsize=15, fontweight='bold', pad=12)
    ax2.set_ylim(0, 110)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    for bar, score in zip(bars2, avg_scores):
        ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 3, f'{score:.1f}点', ha='center', va='bottom', fontsize=13, fontweight='bold')
        ax2.text(bar.get_x() + bar.get_width()/2., score/2, f'{score:.1f}%', ha='center', va='center', fontsize=11, fontweight='bold', color='white')

    ax3 = fig.add_subplot(gs[1, 1])
    bars3 = ax3.bar(['心理社会面\n(Q1-10)', '機能面\n(Q11-20)'], [data['psychosocial_avg'], data['functional_avg']], color=['#E74C3C', '#3498DB'], edgecolor='black', linewidth=1.5, alpha=0.85, width=0.5)
    ax3.set_ylabel('平均点（100点満点）', fontsize=12, fontweight='bold')
    ax3.set_title('心理社会面 vs 機能面', fontsize=15, fontweight='bold', pad=12)
    ax3.set_ylim(0, 110)
    ax3.grid(axis='y', alpha=0.3, linestyle='--')
    for bar, score in zip(bars3, [data['psychosocial_avg'], data['functional_avg']]):
        ax3.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 3, f'{score:.1f}点', ha='center', va='bottom', fontsize=13, fontweight='bold')
        ax3.text(bar.get_x() + bar.get_width()/2., score/2, f'{score:.1f}%', ha='center', va='center', fontsize=11, fontweight='bold', color='white')

    diff = abs(data['psychosocial_avg'] - data['functional_avg'])
    if diff > 10:
        diff_text = f'心理社会面が{diff:.1f}点高い' if data['psychosocial_avg'] > data['functional_avg'] else f'機能面が{diff:.1f}点高い'
        color = '#E74C3C' if data['psychosocial_avg'] > data['functional_avg'] else '#3498DB'
        ax3.text(0.5, 0.95, diff_text, transform=ax3.transAxes, ha='center', va='top', fontsize=10, fontweight='bold', bbox=dict(boxstyle='round,pad=0.5', facecolor=color, alpha=0.3))

    plt.tight_layout()
    return fig


def generate_pdf_report(data):
    buf = io.BytesIO()
    with PdfPages(buf) as pdf:
        # --- ページ1: サマリー + グラフ (横A4) ---
        fig = plt.figure(figsize=(11.69, 8.27))

        fig.suptitle('視覚のQOL調査 AS-20 結果レポート', fontsize=18, fontweight='bold', y=0.98)

        timestamp = data['timestamp'][:10]
        fig.text(0.5, 0.94,
                 f"患者名: {data['name']}　|　患者ID: {data['patient_id']}　|　実施日: {timestamp}",
                 ha='center', fontsize=11)

        fig.text(0.5, 0.90,
                 f"全体平均: {data['total_avg']:.1f}点　|　心理社会面: {data['psychosocial_avg']:.1f}点　|　機能面: {data['functional_avg']:.1f}点",
                 ha='center', fontsize=10, color='#333333')

        gs = fig.add_gridspec(2, 2, left=0.07, right=0.98, top=0.87, bottom=0.05,
                              width_ratios=[2, 1], height_ratios=[1, 1], hspace=0.35, wspace=0.3)

        ax1 = fig.add_subplot(gs[:, 0])
        questions_short = [f"Q{i+1}" for i in range(20)]
        colors = ['#2ECC71' if s == 100 else '#95E1D3' if s == 75 else '#FFD93D' if s == 50 else '#FF9A76' if s == 25 else '#FF6B6B' for s in data['scores']]
        bars = ax1.barh(questions_short, data['scores'], color=colors, edgecolor='black', linewidth=0.6)
        ax1.set_xlabel('スコア（100点満点）', fontsize=10, fontweight='bold')
        ax1.set_ylabel('質問項目', fontsize=10, fontweight='bold')
        ax1.set_title('項目ごとのスコア', fontsize=12, fontweight='bold', pad=8)
        ax1.set_xlim(0, 115)
        ax1.invert_yaxis()
        ax1.grid(axis='x', alpha=0.3, linestyle='--')
        for bar, score in zip(bars, data['scores']):
            ax1.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2, f'{int(score)}', ha='left', va='center', fontsize=8, fontweight='bold')

        ax2 = fig.add_subplot(gs[0, 1])
        categories = ['全体\n(Q1-20)', '心理社会面\n(Q1-10)', '機能面\n(Q11-20)']
        avg_scores = [data['total_avg'], data['psychosocial_avg'], data['functional_avg']]
        bars2 = ax2.bar(categories, avg_scores, color=['#9B59B6', '#E74C3C', '#3498DB'], edgecolor='black', linewidth=1.2, alpha=0.85, width=0.6)
        ax2.set_ylabel('平均点', fontsize=10, fontweight='bold')
        ax2.set_title('カテゴリー別平均点', fontsize=12, fontweight='bold', pad=8)
        ax2.set_ylim(0, 115)
        ax2.grid(axis='y', alpha=0.3, linestyle='--')
        for bar, score in zip(bars2, avg_scores):
            ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 2, f'{score:.1f}点', ha='center', va='bottom', fontsize=10, fontweight='bold')
            if score > 15:
                ax2.text(bar.get_x() + bar.get_width()/2., score/2, f'{score:.1f}%', ha='center', va='center', fontsize=9, fontweight='bold', color='white')

        ax3 = fig.add_subplot(gs[1, 1])
        bars3 = ax3.bar(['心理社会面\n(Q1-10)', '機能面\n(Q11-20)'], [data['psychosocial_avg'], data['functional_avg']], color=['#E74C3C', '#3498DB'], edgecolor='black', linewidth=1.2, alpha=0.85, width=0.5)
        ax3.set_ylabel('平均点', fontsize=10, fontweight='bold')
        ax3.set_title('心理社会面 vs 機能面', fontsize=12, fontweight='bold', pad=8)
        ax3.set_ylim(0, 115)
        ax3.grid(axis='y', alpha=0.3, linestyle='--')
        for bar, score in zip(bars3, [data['psychosocial_avg'], data['functional_avg']]):
            ax3.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 2, f'{score:.1f}点', ha='center', va='bottom', fontsize=10, fontweight='bold')
            if score > 15:
                ax3.text(bar.get_x() + bar.get_width()/2., score/2, f'{score:.1f}%', ha='center', va='center', fontsize=9, fontweight='bold', color='white')

        diff = abs(data['psychosocial_avg'] - data['functional_avg'])
        if diff > 10:
            diff_text = f'心理社会面が{diff:.1f}点高い' if data['psychosocial_avg'] > data['functional_avg'] else f'機能面が{diff:.1f}点高い'
            color = '#E74C3C' if data['psychosocial_avg'] > data['functional_avg'] else '#3498DB'
            ax3.text(0.5, 0.95, diff_text, transform=ax3.transAxes, ha='center', va='top', fontsize=9, fontweight='bold', bbox=dict(boxstyle='round,pad=0.4', facecolor=color, alpha=0.3))

        fig.text(0.5, 0.01, '本調査の権利は後関利明教授および視能訓練士・高橋慎也が保有しています。',
                 ha='center', fontsize=7, color='gray')

        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)

        # --- ページ2: 全回答一覧 (縦A4) ---
        fig2, ax = plt.subplots(figsize=(8.27, 11.69))
        ax.axis('off')

        fig2.suptitle('AS-20 回答詳細', fontsize=14, fontweight='bold', y=0.97)
        fig2.text(0.5, 0.94, f"患者名: {data['name']}　患者ID: {data['patient_id']}　実施日: {timestamp}",
                  ha='center', fontsize=10)

        table_data = [[f"Q{i+1}", QUESTIONS[i][3:], data['responses'][i], f"{data['scores'][i]}点"]
                      for i in range(20)]
        table = ax.table(
            cellText=table_data,
            colLabels=['No', '質問', '回答', 'スコア'],
            cellLoc='left',
            loc='center',
            bbox=[0, 0, 1, 0.92]
        )
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        for (row, col), cell in table.get_celld().items():
            if row == 0:
                cell.set_facecolor('#4A4A8A')
                cell.set_text_props(color='white', fontweight='bold')
            elif row % 2 == 0:
                cell.set_facecolor('#F0F0F8')
            cell.set_edgecolor('#CCCCCC')

        fig2.text(0.5, 0.01, '本調査の権利は後関利明教授および視能訓練士・高橋慎也が保有しています。',
                  ha='center', fontsize=7, color='gray')

        pdf.savefig(fig2, bbox_inches='tight')
        plt.close(fig2)

    buf.seek(0)
    return buf


# メイン
st.title("📋 視覚のQOL調査 AS-20")
st.markdown("""
本アンケートは斜視や斜視の疑いのある方への簡易的な国際的に有用な質問票です。
斜視が日常生活にどのような影響を与えるのか調査する目的で行っています。

**全部で20項目あります。** 各項目ご自身のお気持ちをよく表している項目を選択してください。
""")

st.divider()

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("氏名 *", placeholder="お名前を入力してください")
with col2:
    patient_id = st.text_input("患者ID *", placeholder="患者IDを入力してください")

st.divider()

st.subheader("📝 アンケート質問")
st.caption("*すべての質問にお答えください*")

responses = []
for i, question in enumerate(QUESTIONS):
    response = st.radio(question, options=LIKERT_OPTIONS, index=None, key=f"q{i}", horizontal=True)
    responses.append(response)

st.divider()

if st.button("✅ 回答を送信してスコアを表示", type="primary", use_container_width=True):
    if not name or not patient_id:
        st.error("❌ 氏名とIDを入力してください。")
    elif None in responses:
        st.error("❌ すべての質問に回答してください。")
    else:
        data = save_response(name, patient_id, responses)
        st.success("✅ 回答を送信しました！")
        st.divider()
        st.header("📊 結果")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("全体平均点", f"{data['total_avg']:.1f}点")
        with col2:
            st.metric("心理社会面平均点", f"{data['psychosocial_avg']:.1f}点")
        with col3:
            st.metric("機能面平均点", f"{data['functional_avg']:.1f}点")

        fig = create_visualization(data)
        st.pyplot(fig)

        st.divider()
        pdf_buf = generate_pdf_report(data)
        filename = f"AS20_{data['patient_id']}_{data['timestamp'][:10]}.pdf"
        st.download_button(
            label="🖨️ PDFレポートをダウンロード",
            data=pdf_buf,
            file_name=filename,
            mime="application/pdf",
            use_container_width=True
        )

st.divider()
st.caption("© 2025 視覚のQOL調査 AS-20 | すべての回答は自動的に保存されます")
st.caption("本調査の権利は後関利明教授および視能訓練士・高橋慎也が保有しています。無断転載・複製を禁じます。")
